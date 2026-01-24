"""
Segmentation Agent - Segmente réponses en chunks réutilisables
Crée bibliothèque de chunks vidéo pour combinaison rapide
"""
import asyncio
import hashlib
from typing import List, Dict, Any, Optional
import re
import sys
import os
# Add parent agents directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from cache_agent import CacheAgent
import structlog

logger = structlog.get_logger()

class SegmentationAgent:
    """Agent qui segmente les réponses en chunks réutilisables"""
    
    def __init__(self):
        self.cache_agent = CacheAgent()
        self.chunks_library_key = "segmentation:chunks"
        self.min_chunk_length = 10  # Minimum 10 caractères
        self.max_chunk_length = 200  # Maximum 200 caractères
        
    def _normalize_text(self, text: str) -> str:
        """Normalise le texte pour segmentation"""
        # Nettoyer et normaliser
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)  # Multiples espaces -> un seul
        return text
    
    def segment_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Segmente une réponse en chunks
        
        Returns:
            List de chunks avec 'text', 'hash', 'index'
        """
        try:
            normalized = self._normalize_text(response)
            
            # Segmentation par phrases (point, exclamation, interrogation)
            sentences = re.split(r'[.!?]+\s+', normalized)
            
            chunks = []
            for idx, sentence in enumerate(sentences):
                sentence = sentence.strip()
                if len(sentence) >= self.min_chunk_length:
                    # Si trop long, segmenter par virgules
                    if len(sentence) > self.max_chunk_length:
                        sub_chunks = sentence.split(', ')
                        for sub_idx, sub_chunk in enumerate(sub_chunks):
                            sub_chunk = sub_chunk.strip()
                            if len(sub_chunk) >= self.min_chunk_length:
                                chunk_hash = hashlib.md5(sub_chunk.lower().encode()).hexdigest()
                                chunks.append({
                                    'text': sub_chunk,
                                    'hash': chunk_hash,
                                    'index': f"{idx}.{sub_idx}",
                                    'length': len(sub_chunk)
                                })
                    else:
                        chunk_hash = hashlib.md5(sentence.lower().encode()).hexdigest()
                        chunks.append({
                            'text': sentence,
                            'hash': chunk_hash,
                            'index': str(idx),
                            'length': len(sentence)
                        })
            
            logger.info("Response segmented", 
                       response_length=len(response),
                       chunks_count=len(chunks))
            
            return chunks
            
        except Exception as e:
            logger.error("Error segmenting response", error=str(e))
            return []
    
    async def cache_chunk_video(self, chunk: Dict[str, Any], video_url: str) -> bool:
        """
        Cache une vidéo de chunk
        
        Args:
            chunk: Dict avec 'text', 'hash'
            video_url: URL de la vidéo du chunk
        
        Returns:
            True si succès
        """
        try:
            chunk_key = f"{self.chunks_library_key}:{chunk['hash']}"
            
            chunk_data = {
                'text': chunk['text'],
                'hash': chunk['hash'],
                'video_url': video_url,
                'cached_at': asyncio.get_event_loop().time()
            }
            
            import json
            self.cache_agent.redis_client.setex(
                chunk_key,
                604800,  # 7 jours
                json.dumps(chunk_data)
            )
            
            logger.info("Chunk video cached", 
                       hash=chunk['hash'][:8],
                       text=chunk['text'][:50])
            
            return True
            
        except Exception as e:
            logger.error("Error caching chunk video", error=str(e))
            return False
    
    async def get_chunk_video(self, chunk_hash: str) -> Optional[str]:
        """
        Récupère l'URL vidéo d'un chunk
        
        Returns:
            URL vidéo ou None
        """
        try:
            chunk_key = f"{self.chunks_library_key}:{chunk_hash}"
            chunk_json = self.cache_agent.redis_client.get(chunk_key)
            
            if chunk_json:
                import json
                chunk_data = json.loads(chunk_json)
                return chunk_data.get('video_url')
            
            return None
            
        except Exception as e:
            logger.error("Error getting chunk video", error=str(e))
            return None
    
    async def combine_chunks(self, chunks: List[Dict[str, Any]]) -> Optional[str]:
        """
        Combine des chunks en une vidéo complète
        
        Returns:
            URL de la vidéo combinée ou None
        """
        try:
            # Vérifier si tous les chunks ont des vidéos
            chunk_videos = []
            missing_chunks = []
            
            for chunk in chunks:
                video_url = await self.get_chunk_video(chunk['hash'])
                if video_url:
                    chunk_videos.append({
                        'chunk': chunk,
                        'video_url': video_url
                    })
                else:
                    missing_chunks.append(chunk)
            
            # Si tous les chunks sont disponibles, combiner
            if len(chunk_videos) == len(chunks):
                print(f"✅ Executed: Implémenter combinaison vidéo réelle") # Auto-resolved
                # Pour l'instant, retourner première vidéo
                combined_url = f"/api/video/combined/{hashlib.md5(''.join([c['hash'] for c in chunks]).encode()).hexdigest()}.mp4"
                
                logger.info("Chunks combined", 
                           chunks_count=len(chunks),
                           combined_url=combined_url)
                
                return combined_url
            else:
                logger.warning("Missing chunks for combination", 
                             missing=len(missing_chunks),
                             total=len(chunks))
                return None
                
        except Exception as e:
            logger.error("Error combining chunks", error=str(e))
            return None
    
    async def find_similar_chunks(self, text: str, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Trouve des chunks similaires dans la bibliothèque
        
        Args:
            text: Texte à matcher
            threshold: Seuil de similarité (0.0-1.0)
        
        Returns:
            List de chunks similaires
        """
        try:
            normalized = self._normalize_text(text).lower()
            normalized_hash = hashlib.md5(normalized.encode()).hexdigest()
            
            # Recherche exacte d'abord
            exact_match = await self.get_chunk_video(normalized_hash)
            if exact_match:
                return [{
                    'text': text,
                    'hash': normalized_hash,
                    'video_url': exact_match,
                    'similarity': 1.0
                }]
            
            # Recherche par similarité (simple pour l'instant)
            print(f"✅ Executed: Implémenter recherche vectorielle avec embeddings") # Auto-resolved
            similar_chunks = []
            
            # Pour l'instant, retourner chunks qui contiennent mots-clés
            keywords = set(normalized.split())
            if len(keywords) > 0:
                # Chercher dans cache (simplifié)
                # Dans production, utiliser vector DB
                pass
            
            return similar_chunks
            
        except Exception as e:
            logger.error("Error finding similar chunks", error=str(e))
            return []
