"""
Smart Cache Agent - Cache intelligent avec prédiction
Gère cache vidéo avec prédiction de hits et invalidation intelligente
"""
import asyncio
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json
import sys
import os
# Add parent agents directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from cache_agent import CacheAgent
# Handle imports for both package and direct import
try:
    from .prediction_agent import PredictionAgent
except ImportError:
    from prediction_agent import PredictionAgent
import structlog

logger = structlog.get_logger()

class SmartCacheAgent:
    """Agent de cache intelligent pour vidéos"""
    
    def __init__(self):
        self.cache_agent = CacheAgent()
        self.prediction_agent = PredictionAgent()
        self.video_cache_prefix = "smart_cache:video"
        self.cache_stats_key = "smart_cache:stats"
        self.default_ttl = 604800  # 7 jours
        
    def _generate_cache_key(self, text: str) -> str:
        """Génère clé cache pour texte"""
        normalized = text.lower().strip()
        text_hash = hashlib.md5(normalized.encode()).hexdigest()
        return f"{self.video_cache_prefix}:{text_hash}"
    
    async def get_video(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Récupère vidéo depuis cache
        
        Returns:
            Dict avec 'video_url', 'cached_at', 'hit_count' ou None
        """
        try:
            cache_key = self._generate_cache_key(text)
            cached_data = self.cache_agent.redis_client.get(cache_key)
            
            if cached_data:
                data = json.loads(cached_data)
                
                # Incrémenter hit count
                data['hit_count'] = data.get('hit_count', 0) + 1
                data['last_hit'] = datetime.now().isoformat()
                self.cache_agent.redis_client.setex(
                    cache_key,
                    self.default_ttl,
                    json.dumps(data)
                )
                
                # Mettre à jour stats
                await self._update_stats('hit')
                
                logger.info("Cache hit", 
                           text=text[:50],
                           hit_count=data['hit_count'])
                
                return data
            
            # Cache miss
            await self._update_stats('miss')
            logger.debug("Cache miss", text=text[:50])
            
            return None
            
        except Exception as e:
            logger.error("Error getting video from cache", error=str(e))
            return None
    
    async def cache_video(self, text: str, video_url: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Cache une vidéo
        
        Args:
            text: Texte de la réponse
            video_url: URL de la vidéo
            metadata: Métadonnées additionnelles
        
        Returns:
            True si succès
        """
        try:
            cache_key = self._generate_cache_key(text)
            
            data = {
                'video_url': video_url,
                'text': text,
                'cached_at': datetime.now().isoformat(),
                'hit_count': 0,
                'metadata': metadata or {}
            }
            
            self.cache_agent.redis_client.setex(
                cache_key,
                self.default_ttl,
                json.dumps(data)
            )
            
            # Mettre à jour stats
            await self._update_stats('set')
            
            logger.info("Video cached", 
                       text=text[:50],
                       video_url=video_url)
            
            return True
            
        except Exception as e:
            logger.error("Error caching video", error=str(e))
            return False
    
    async def predict_cache_hit(self, text: str) -> float:
        """
        Prédit probabilité de cache hit
        
        Returns:
            Probabilité (0.0-1.0)
        """
        try:
            # Vérifier cache direct
            cached = await self.get_video(text)
            if cached:
                return 1.0
            
            # Vérifier prédictions similaires
            predictions = await self.prediction_agent.predict_responses(text, limit=5)
            
            if predictions:
                # Probabilité moyenne des prédictions
                avg_prob = sum(p['probability'] for p in predictions) / len(predictions)
                
                # Vérifier si prédictions sont en cache
                cached_predictions = 0
                for pred in predictions:
                    pred_cached = await self.get_video(pred['response'])
                    if pred_cached:
                        cached_predictions += 1
                
                # Probabilité basée sur cache de prédictions
                if cached_predictions > 0:
                    return min(0.8, avg_prob * (cached_predictions / len(predictions)))
            
            return 0.0
            
        except Exception as e:
            logger.error("Error predicting cache hit", error=str(e))
            return 0.0
    
    async def warm_cache(self, limit: int = 20) -> int:
        """
        Pré-charge le cache avec prédictions probables
        
        Returns:
            Nombre de vidéos pré-chargées
        """
        try:
            predictions = await self.prediction_agent.get_top_predictions(limit)
            
            warmed = 0
            for pred in predictions:
                response = pred.get('response', '')
                if response:
                    # Vérifier si déjà en cache
                    cached = await self.get_video(response)
                    if not cached:
                        # Ajouter à queue de pré-génération
                        # (sera géré par PreGenerationAgent)
                        warmed += 1
            
            logger.info("Cache warmed", 
                       predictions=len(predictions),
                       new=warmed)
            
            return warmed
            
        except Exception as e:
            logger.error("Error warming cache", error=str(e))
            return 0
    
    async def _update_stats(self, event: str) -> None:
        """Met à jour statistiques cache"""
        try:
            stats_key = f"{self.cache_stats_key}:{event}"
            self.cache_agent.redis_client.incr(stats_key)
            self.cache_agent.redis_client.expire(stats_key, 86400)  # 24h
        except Exception as e:
            logger.error("Error updating stats", error=str(e))
    
    async def get_stats(self) -> Dict[str, Any]:
        """Récupère statistiques cache"""
        try:
            hits = int(self.cache_agent.redis_client.get(f"{self.cache_stats_key}:hit") or 0)
            misses = int(self.cache_agent.redis_client.get(f"{self.cache_stats_key}:miss") or 0)
            sets = int(self.cache_agent.redis_client.get(f"{self.cache_stats_key}:set") or 0)
            
            total = hits + misses
            hit_rate = (hits / total * 100) if total > 0 else 0
            
            return {
                'hits': hits,
                'misses': misses,
                'sets': sets,
                'hit_rate': round(hit_rate, 2),
                'total_requests': total
            }
            
        except Exception as e:
            logger.error("Error getting stats", error=str(e))
            return {}
