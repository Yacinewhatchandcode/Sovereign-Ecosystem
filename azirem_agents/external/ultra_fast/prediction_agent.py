"""
Prediction Agent - Prédit questions/réponses probables
Utilise ML et analyse patterns pour prédire ce que l'utilisateur va demander
"""
import asyncio
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import sys
import os
# Add parent agents directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from cache_agent import CacheAgent
# Import config from parent agents directory, not from ultra_fast_video
import sys
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
try:
    from config import config as agent_config
    config = agent_config
except ImportError:
    # Fallback if config not available
    class Config:
        enable_cache = True
        redis_host = "localhost"
        redis_port = 6379
        redis_db = 0
        redis_password = None
    config = Config()
import structlog

logger = structlog.get_logger()

class PredictionAgent:
    """Agent qui prédit les questions/réponses probables"""
    
    def __init__(self):
        self.cache_agent = CacheAgent()
        self.prediction_cache_ttl = 3600  # 1 heure
        self.history_window = 100  # Dernières 100 conversations
        
    def _get_history_key(self) -> str:
        """Clé pour historique conversations"""
        return "prediction:history"
    
    def _get_patterns_key(self) -> str:
        """Clé pour patterns appris"""
        return "prediction:patterns"
    
    async def record_conversation(self, question: str, response: str, user_id: Optional[str] = None) -> None:
        """Enregistre une conversation pour apprentissage"""
        try:
            history_key = self._get_history_key()
            conversation = {
                "question": question.lower().strip(),
                "response": response.lower().strip(),
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id
            }
            
            # Ajouter à l'historique (FIFO, max 100)
            history = self.cache_agent.redis_client.lrange(history_key, 0, -1)
            if len(history) >= self.history_window:
                self.cache_agent.redis_client.ltrim(history_key, 1, -1)
            
            self.cache_agent.redis_client.lpush(history_key, json.dumps(conversation))
            self.cache_agent.redis_client.expire(history_key, 86400 * 7)  # 7 jours
            
            # Mettre à jour patterns
            await self._update_patterns(question, response)
            
            logger.info("Conversation recorded", question=question[:50])
        except Exception as e:
            logger.error("Error recording conversation", error=str(e))
    
    async def _update_patterns(self, question: str, response: str) -> None:
        """Met à jour les patterns appris"""
        try:
            patterns_key = self._get_patterns_key()
            
            # Extraire mots-clés de la question
            keywords = self._extract_keywords(question)
            
            # Mettre à jour compteurs de patterns
            for keyword in keywords:
                pattern_key = f"{patterns_key}:{keyword}"
                self.cache_agent.redis_client.incr(pattern_key)
                self.cache_agent.redis_client.expire(pattern_key, 86400 * 30)  # 30 jours
            
            logger.debug("Patterns updated", keywords=keywords[:5])
        except Exception as e:
            logger.error("Error updating patterns", error=str(e))
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrait mots-clés importants"""
        # Mots vides à ignorer
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who', 'whom', 'whose', 'where', 'when', 'why', 'how'}
        
        # Normaliser et extraire mots
        words = text.lower().strip().split()
        keywords = [w for w in words if len(w) > 2 and w not in stop_words]
        
        return keywords[:10]  # Top 10 keywords
    
    async def predict_responses(self, question: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Prédit les réponses probables pour une question
        
        Returns:
            List de dicts avec 'response', 'probability', 'source'
        """
        try:
            # Normaliser question
            normalized_question = question.lower().strip()
            question_hash = hashlib.md5(normalized_question.encode()).hexdigest()
            
            # Vérifier cache prédictions
            cache_key = f"prediction:cache:{question_hash}"
            cached = self.cache_agent.redis_client.get(cache_key)
            if cached:
                predictions = json.loads(cached)
                logger.info("Prediction cache hit", question=question[:50])
                return predictions[:limit]
            
            # Générer prédictions
            predictions = []
            
            # 1. Recherche exacte dans historique
            exact_matches = await self._find_exact_matches(normalized_question)
            predictions.extend(exact_matches)
            
            # 2. Recherche similaire par keywords
            similar_matches = await self._find_similar_matches(normalized_question)
            predictions.extend(similar_matches)
            
            # 3. Patterns fréquents
            pattern_matches = await self._find_pattern_matches(normalized_question)
            predictions.extend(pattern_matches)
            
            # Dédupliquer et trier par probabilité
            predictions = self._deduplicate_and_sort(predictions, limit)
            
            # Cache prédictions
            self.cache_agent.redis_client.setex(
                cache_key,
                self.prediction_cache_ttl,
                json.dumps(predictions)
            )
            
            logger.info("Predictions generated", 
                       question=question[:50], 
                       count=len(predictions))
            
            return predictions
            
        except Exception as e:
            logger.error("Error predicting responses", error=str(e), question=question[:50])
            return []
    
    async def _find_exact_matches(self, question: str) -> List[Dict[str, Any]]:
        """Trouve correspondances exactes dans historique"""
        matches = []
        try:
            history_key = self._get_history_key()
            history = self.cache_agent.redis_client.lrange(history_key, 0, -1)
            
            for item in history[:50]:  # Dernières 50
                conv = json.loads(item)
                if conv['question'] == question:
                    matches.append({
                        'response': conv['response'],
                        'probability': 0.95,  # Très haute probabilité
                        'source': 'exact_match'
                    })
        except Exception as e:
            logger.error("Error finding exact matches", error=str(e))
        
        return matches
    
    async def _find_similar_matches(self, question: str) -> List[Dict[str, Any]]:
        """Trouve correspondances similaires par keywords"""
        matches = []
        try:
            keywords = self._extract_keywords(question)
            if not keywords:
                return matches
            
            history_key = self._get_history_key()
            history = self.cache_agent.redis_client.lrange(history_key, 0, -1)
            
            for item in history[:100]:
                conv = json.loads(item)
                conv_keywords = self._extract_keywords(conv['question'])
                
                # Calculer similarité (Jaccard)
                intersection = set(keywords) & set(conv_keywords)
                union = set(keywords) | set(conv_keywords)
                similarity = len(intersection) / len(union) if union else 0
                
                if similarity > 0.3:  # Seuil de similarité
                    matches.append({
                        'response': conv['response'],
                        'probability': similarity * 0.8,  # Ajuster par similarité
                        'source': 'similar_match'
                    })
        except Exception as e:
            logger.error("Error finding similar matches", error=str(e))
        
        return matches
    
    async def _find_pattern_matches(self, question: str) -> List[Dict[str, Any]]:
        """Trouve correspondances basées sur patterns fréquents"""
        matches = []
        try:
            keywords = self._extract_keywords(question)
            patterns_key = self._get_patterns_key()
            
            # Trouver patterns les plus fréquents pour ces keywords
            pattern_scores = {}
            for keyword in keywords:
                pattern_key = f"{patterns_key}:{keyword}"
                count = self.cache_agent.redis_client.get(pattern_key)
                if count:
                    pattern_scores[keyword] = int(count)
            
            # Si patterns trouvés, générer prédictions basées sur fréquence
            if pattern_scores:
                total_score = sum(pattern_scores.values())
                for keyword, score in pattern_scores.items():
                    probability = (score / total_score) * 0.6  # Max 60% pour patterns
                    matches.append({
                        'response': f"Response related to {keyword}",  # System_value
                        'probability': probability,
                        'source': 'pattern_match'
                    })
        except Exception as e:
            logger.error("Error finding pattern matches", error=str(e))
        
        return matches
    
    def _deduplicate_and_sort(self, predictions: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
        """Déduplique et trie par probabilité"""
        # Dédupliquer par response
        seen = set()
        unique = []
        for pred in predictions:
            response_hash = hashlib.md5(pred['response'].encode()).hexdigest()
            if response_hash not in seen:
                seen.add(response_hash)
                unique.append(pred)
        
        # Trier par probabilité (décroissant)
        unique.sort(key=lambda x: x['probability'], reverse=True)
        
        return unique[:limit]
    
    async def get_top_predictions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retourne les prédictions les plus probables (pour pré-génération)"""
        try:
            # Analyser historique pour trouver questions/réponses les plus fréquentes
            history_key = self._get_history_key()
            history = self.cache_agent.redis_client.lrange(history_key, 0, -1)
            
            # Compter fréquences
            frequency = {}
            for item in history:
                conv = json.loads(item)
                question = conv['question']
                response = conv['response']
                key = f"{question}|||{response}"
                frequency[key] = frequency.get(key, 0) + 1
            
            # Trier par fréquence
            sorted_freq = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
            
            # Convertir en format prédictions
            predictions = []
            for key, count in sorted_freq[:limit]:
                question, response = key.split('|||')
                predictions.append({
                    'question': question,
                    'response': response,
                    'probability': min(count / len(history), 1.0),  # Normaliser
                    'frequency': count,
                    'source': 'frequency_analysis'
                })
            
            logger.info("Top predictions generated", count=len(predictions))
            return predictions
            
        except Exception as e:
            logger.error("Error getting top predictions", error=str(e))
            return []
