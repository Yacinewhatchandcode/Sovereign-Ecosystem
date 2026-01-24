"""
Progressive Streaming Agent - Génération vidéo par chunks ultra-petits (0.5-1s)
Stream progressif pour latence minimale (< 1 seconde perçue)
"""
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime
import hashlib
import json
import sys
import os

# Add parent agents directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from cache_agent import CacheAgent
try:
    from .prediction_agent import PredictionAgent
except ImportError:
    from prediction_agent import PredictionAgent

import structlog
import httpx
import re

logger = structlog.get_logger()

class ProgressiveStreamingAgent:
    """
    Agent qui génère et stream des vidéos par chunks ultra-petits (0.5-1s)
    pour une latence minimale (< 1 seconde perçue)
    """
    
    def __init__(self):
        self.cache_agent = CacheAgent()
        self.prediction_agent = PredictionAgent()
        self.min_chunk_duration = 0.5  # 0.5 seconde minimum
        self.max_chunk_duration = 1.0  # 1 seconde maximum
        self.words_per_second = 2.5  # Estimation mots/seconde
        self.chunks_cache_key = "progressive:chunks"
        
    def _split_text_into_micro_chunks(self, text: str) -> List[Dict[str, Any]]:
        """
        Découpe le texte en micro-chunks de 0.5-1 seconde
        
        Returns:
            List de chunks avec 'text', 'hash', 'estimated_duration'
        """
        try:
            # Nettoyer texte
            text = text.strip()
            if not text:
                return []
            
            # Split par phrases courtes (point, virgule, pause naturelle)
            # Priorité: phrases courtes < 1s, sinon découper par virgules
            sentences = re.split(r'([.!?]+[\s]+|,\s+)', text)
            
            chunks = []
            current_chunk = []
            current_duration = 0.0
            
            for part in sentences:
                if not part.strip():
                    continue
                
                # Estimer durée (mots / words_per_second)
                words = part.split()
                estimated_duration = len(words) / self.words_per_second
                
                # Si chunk actuel + nouveau part < max_duration, ajouter
                if current_duration + estimated_duration <= self.max_chunk_duration:
                    current_chunk.append(part)
                    current_duration += estimated_duration
                else:
                    # Sauvegarder chunk actuel si >= min_duration
                    if current_chunk and current_duration >= self.min_chunk_duration:
                        chunk_text = ''.join(current_chunk).strip()
                        if chunk_text:
                            chunk_hash = hashlib.md5(chunk_text.lower().encode()).hexdigest()
                            chunks.append({
                                'text': chunk_text,
                                'hash': chunk_hash,
                                'estimated_duration': round(current_duration, 2),
                                'word_count': len(chunk_text.split())
                            })
                    
                    # Nouveau chunk
                    current_chunk = [part]
                    current_duration = estimated_duration
            
            # Ajouter dernier chunk
            if current_chunk and current_duration >= self.min_chunk_duration:
                chunk_text = ''.join(current_chunk).strip()
                if chunk_text:
                    chunk_hash = hashlib.md5(chunk_text.lower().encode()).hexdigest()
                    chunks.append({
                        'text': chunk_text,
                        'hash': chunk_hash,
                        'estimated_duration': round(current_duration, 2),
                        'word_count': len(chunk_text.split())
                    })
            
            logger.info("Text split into micro-chunks",
                       total_chunks=len(chunks),
                       text_length=len(text))
            
            return chunks
            
        except Exception as e:
            logger.error("Error splitting text into micro-chunks", error=str(e))
            return []
    
    async def _get_cached_chunk_video(self, chunk_hash: str) -> Optional[str]:
        """Récupère vidéo d'un chunk depuis le cache"""
        try:
            chunk_key = f"{self.chunks_cache_key}:{chunk_hash}"
            cached = self.cache_agent.redis_client.get(chunk_key)
            if cached:
                chunk_data = json.loads(cached)
                return chunk_data.get('video_url')
            return None
        except Exception as e:
            logger.error("Error getting cached chunk video", error=str(e))
            return None
    
    async def _cache_chunk_video(self, chunk: Dict[str, Any], video_url: str) -> None:
        """Cache une vidéo de chunk"""
        try:
            chunk_key = f"{self.chunks_cache_key}:{chunk['hash']}"
            chunk_data = {
                'text': chunk['text'],
                'hash': chunk['hash'],
                'video_url': video_url,
                'cached_at': datetime.now().isoformat(),
                'duration': chunk.get('estimated_duration', 0.5)
            }
            self.cache_agent.redis_client.setex(
                chunk_key,
                604800,  # 7 jours
                json.dumps(chunk_data)
            )
        except Exception as e:
            logger.error("Error caching chunk video", error=str(e))
    
    async def _generate_chunk_video(
        self, 
        chunk: Dict[str, Any],
        whisk_avatar: str = "/code/data/lisa.png"
    ) -> Optional[str]:
        """
        Génère vidéo pour un chunk (0.5-1s)
        Utilise le même pipeline que génération normale
        """
        try:
            chunk_text = chunk['text']
            chunk_hash = chunk['hash']
            
            # Vérifier cache d'abord
            cached = await self._get_cached_chunk_video(chunk_hash)
            if cached:
                logger.info("Using cached chunk video", hash=chunk_hash[:8])
                return cached
            
            # Générer audio pour chunk
            tts_endpoint = os.getenv('TTS_ENDPOINT', 'http://localhost:18180/v1/invoke')
            whisk_voice = os.getenv('WHISK_VOICE', '/code/data/whisk_voice.wav')
            
            tts_payload = {
                'speaker': chunk_hash[:16],
                'text': chunk_text,
                'format': 'wav',
                'reference_audio': whisk_voice,
                'reference_text': chunk_text[:50]  # Premiers 50 caractères
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Générer audio
                try:
                    tts_response = await client.post(tts_endpoint, json=tts_payload)
                    if tts_response.status_code != 200:
                        logger.error("TTS failed for chunk", 
                                   status=tts_response.status_code,
                                   response_text=tts_response.text[:200],
                                   chunk=chunk_text[:30])
                        return None
                    
                    audio_data = tts_response.content
                    if len(audio_data) == 0:
                        logger.error("TTS returned empty audio", chunk=chunk_text[:30])
                        return None
                except httpx.TimeoutException:
                    logger.error("TTS timeout", endpoint=tts_endpoint, chunk=chunk_text[:30])
                    return None
                except Exception as e:
                    logger.error("TTS request failed", error=str(e), endpoint=tts_endpoint, chunk=chunk_text[:30])
                    return None
                
                # Upload audio
                upload_endpoint = os.getenv('UPLOAD_ENDPOINT', 'http://localhost:5000/upload-audio')
                try:
                    files = {'audio': ('audio.wav', audio_data, 'audio/wav')}
                    upload_response = await client.post(upload_endpoint, files=files)
                    
                    if upload_response.status_code != 200:
                        logger.error("Audio upload failed", 
                                   status=upload_response.status_code,
                                   response_text=upload_response.text[:200])
                        return None
                    
                    upload_result = upload_response.json()
                    audio_path = upload_result.get('path')
                    if not audio_path:
                        logger.error("Upload returned no path", response=upload_result)
                        return None
                except httpx.TimeoutException:
                    logger.error("Upload timeout", endpoint=upload_endpoint)
                    return None
                except Exception as e:
                    logger.error("Upload request failed", error=str(e), endpoint=upload_endpoint)
                    return None
                
                # Submit video job
                video_submit_endpoint = os.getenv('VIDEO_SUBMIT', 'http://localhost:8383/easy/submit')
                job_id = chunk_hash[:16]
                
                video_payload = {
                    'audio_url': audio_path,
                    'video_url': whisk_avatar,
                    'code': job_id,
                    'chaofen': 0,
                    'watermark_switch': 0,
                    'pn': 1
                }
                
                try:
                    submit_response = await client.post(
                        video_submit_endpoint,
                        json=video_payload,
                        timeout=10.0
                    )
                    
                    if submit_response.status_code != 200:
                        logger.error("Video submission failed", 
                                   status=submit_response.status_code,
                                   response_text=submit_response.text[:200],
                                   payload=video_payload)
                        return None
                except httpx.TimeoutException:
                    logger.error("Video submit timeout", endpoint=video_submit_endpoint)
                    return None
                except Exception as e:
                    logger.error("Video submit request failed", error=str(e), endpoint=video_submit_endpoint)
                    return None
                
                # Poll pour vidéo (timeout réduit pour chunks petits)
                video_query_endpoint = os.getenv('VIDEO_QUERY', 'http://localhost:8383/easy/query')
                max_attempts = 60  # 60 secondes max pour chunk de 0.5-1s
                
                for attempt in range(max_attempts):
                    await asyncio.sleep(0.5)  # Poll toutes les 0.5s
                    
                    query_response = await client.get(
                        f"{video_query_endpoint}?code={job_id}",
                        timeout=5.0
                    )
                    
                    if query_response.status_code == 200:
                        query_result = query_response.json()
                        if query_result.get('code') == 10000:
                            data = query_result.get('data', {})
                            if data.get('status') == 2:  # Completed
                                video_url = data.get('result') or data.get('file_path')
                                if video_url:
                                    # Cache chunk vidéo
                                    await self._cache_chunk_video(chunk, video_url)
                                    logger.info("Chunk video generated",
                                               hash=chunk_hash[:8],
                                               duration=chunk.get('estimated_duration'))
                                    return video_url
                
                logger.warning("Chunk video generation timeout", hash=chunk_hash[:8])
                return None
                
        except httpx.TimeoutException as e:
            logger.error("Timeout generating chunk video", error=str(e), chunk=chunk.get('text', '')[:30])
            return None
        except httpx.RequestError as e:
            logger.error("Request error generating chunk video", error=str(e), chunk=chunk.get('text', '')[:30])
            return None
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error("Error generating chunk video", 
                       error=str(e) if str(e) else type(e).__name__,
                       error_type=type(e).__name__,
                       chunk=chunk.get('text', '')[:30],
                       traceback=error_details[-500:])  # Last 500 chars of traceback
            return None
    
    async def stream_video_progressively(
        self,
        response_text: str,
        question: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream vidéo progressivement par micro-chunks
        
        Yields:
            Dict avec 'chunk_number', 'total_chunks', 'video_url', 'text', 'status'
        """
        try:
            # Découper en micro-chunks
            chunks = self._split_text_into_micro_chunks(response_text)
            
            if not chunks:
                yield {
                    'status': 'error',
                    'error': 'No chunks generated'
                }
                return
            
            total_chunks = len(chunks)
            logger.info("Starting progressive streaming",
                       total_chunks=total_chunks,
                       text_length=len(response_text))
            
            # Générer chunks en parallèle (batch de 3 pour ne pas surcharger)
            batch_size = 3
            completed_chunks = []
            
            for batch_start in range(0, total_chunks, batch_size):
                batch_end = min(batch_start + batch_size, total_chunks)
                batch = chunks[batch_start:batch_end]
                
                # Générer batch en parallèle
                tasks = [self._generate_chunk_video(chunk) for chunk in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Yielder résultats au fur et à mesure
                for i, (chunk, result) in enumerate(zip(batch, results)):
                    chunk_num = batch_start + i + 1
                    
                    if isinstance(result, Exception):
                        yield {
                            'chunk_number': chunk_num,
                            'total_chunks': total_chunks,
                            'text': chunk['text'],
                            'status': 'error',
                            'error': str(result)
                        }
                    elif result:
                        completed_chunks.append({
                            'chunk_number': chunk_num,
                            'text': chunk['text'],
                            'video_url': result,
                            'duration': chunk.get('estimated_duration', 0.5)
                        })
                        
                        yield {
                            'chunk_number': chunk_num,
                            'total_chunks': total_chunks,
                            'text': chunk['text'],
                            'video_url': result,
                            'status': 'ready',
                            'duration': chunk.get('estimated_duration', 0.5),
                            'progress': round((chunk_num / total_chunks) * 100, 1)
                        }
                    else:
                        yield {
                            'chunk_number': chunk_num,
                            'total_chunks': total_chunks,
                            'text': chunk['text'],
                            'status': 'failed',
                            'error': 'Video generation failed'
                        }
            
            # Yielder résultat final avec tous les chunks
            yield {
                'status': 'completed',
                'total_chunks': total_chunks,
                'completed_chunks': len(completed_chunks),
                'chunks': completed_chunks,
                'message': 'All chunks generated'
            }
            
        except Exception as e:
            logger.error("Error in progressive streaming", error=str(e))
            yield {
                'status': 'error',
                'error': str(e)
            }
