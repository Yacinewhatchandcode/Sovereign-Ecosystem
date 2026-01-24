"""
Pre-Generation Agent - Génère vidéos en arrière-plan
Utilise GPU idle time pour pré-générer vidéos prédites
"""
import asyncio
from typing import List, Dict, Any, Optional
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
# Handle imports for both package and direct import
try:
    from .prediction_agent import PredictionAgent
except ImportError:
    from prediction_agent import PredictionAgent
import structlog

logger = structlog.get_logger()

class PreGenerationAgent:
    """Agent qui pré-génère des vidéos en arrière-plan"""
    
    def __init__(self):
        self.cache_agent = CacheAgent()
        self.prediction_agent = PredictionAgent()
        self.pregen_queue_key = "pregeneration:queue"
        self.pregen_status_key = "pregeneration:status"
        self.batch_size = 5  # Générer 5 vidéos en parallèle
        
    async def add_to_queue(self, response_text: str, priority: float = 0.5) -> str:
        """
        Ajoute une réponse à la queue de pré-génération
        
        Args:
            response_text: Texte de la réponse à pré-générer
            priority: Priorité (0.0-1.0), plus haut = plus prioritaire
        
        Returns:
            Job ID
        """
        try:
            job_id = hashlib.md5(response_text.encode()).hexdigest()[:16]
            
            job = {
                'job_id': job_id,
                'response_text': response_text,
                'priority': priority,
                'created_at': datetime.now().isoformat(),
                'status': 'pending'
            }
            
            # Ajouter à queue Redis (sorted set par priorité)
            self.cache_agent.redis_client.zadd(
                self.pregen_queue_key,
                {json.dumps(job): priority}
            )
            
            logger.info("Job added to pre-generation queue", 
                       job_id=job_id, 
                       priority=priority,
                       text=response_text[:50])
            
            return job_id
            
        except Exception as e:
            logger.error("Error adding to queue", error=str(e))
            return ""
    
    async def process_queue(self, max_jobs: int = None) -> List[str]:
        """
        Traite la queue de pré-génération
        
        Args:
            max_jobs: Nombre max de jobs à traiter (None = tous)
        
        Returns:
            List de job IDs traités
        """
        try:
            # Récupérer jobs par priorité (plus haut d'abord)
            jobs_data = self.cache_agent.redis_client.zrevrange(
                self.pregen_queue_key,
                0,
                (max_jobs or self.batch_size) - 1,
                withscores=True
            )
            
            if not jobs_data:
                return []
            
            processed_jobs = []
            
            # Traiter jobs en parallèle
            tasks = []
            for job_json, priority in jobs_data:
                job = json.loads(job_json)
                if job['status'] == 'pending':
                    tasks.append(self._generate_video_async(job))
            
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for result in results:
                    if isinstance(result, str):
                        processed_jobs.append(result)
            
            logger.info("Queue processed", 
                       processed=len(processed_jobs),
                       total=len(jobs_data))
            
            return processed_jobs
            
        except Exception as e:
            logger.error("Error processing queue", error=str(e))
            return []
    
    async def _generate_video_async(self, job: Dict[str, Any]) -> str:
        """
        Génère une vidéo de manière asynchrone
        
        IMPORTANT: Utilise le MÊME service de génération vidéo que le système normal
        pour garantir la MÊME résolution et qualité (1920x1080, H.264, 30fps)
        """
        try:
            job_id = job['job_id']
            response_text = job['response_text']
            
            # Marquer comme "processing"
            job['status'] = 'processing'
            job['started_at'] = datetime.now().isoformat()
            self._update_job_status(job)
            
            # IMPORTANT: Utiliser le MÊME service de génération vidéo
            # Même pipeline, même GPU, même résolution, même qualité
            try:
                # Générer audio d'abord (TTS) - utiliser même TTSAgent que système normal
                import sys
                import os
                parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                if parent_dir not in sys.path:
                    sys.path.insert(0, parent_dir)
                
                from tts_agent import TTSAgent
                tts_agent = TTSAgent()
                audio_data = await tts_agent.generate(response_text)
                
                # Upload audio (même endpoint que système normal)
                import httpx
                import os
                
                # Utiliser même endpoint que système normal
                upload_endpoint = os.getenv('UPLOAD_ENDPOINT', 'http://localhost:5000/upload-audio')
                
                # Upload audio
                files = {'audio': ('audio.wav', audio_data, 'audio/wav')}
                async with httpx.AsyncClient(timeout=60.0) as client:
                    upload_response = await client.post(upload_endpoint, files=files)
                    
                    if upload_response.status_code == 200:
                        upload_result = upload_response.json()
                        audio_path = upload_result.get('path')
                        
                        # Submit video job (MÊME service, MÊME paramètres)
                        video_submit_endpoint = os.getenv('VIDEO_SUBMIT', 'http://localhost:8383/easy/submit')
                        whisk_avatar = os.getenv('WHISK_AVATAR', '/code/data/whisk.mp4')
                        
                        video_payload = {
                            'audio_url': audio_path,
                            'video_url': whisk_avatar,  # Même avatar source
                            'code': job_id,
                            'chaofen': 0,  # Mêmes paramètres
                            'watermark_switch': 0,
                            'pn': 1
                        }
                        
                        submit_response = await client.post(
                            video_submit_endpoint,
                            json=video_payload,
                            timeout=60.0
                        )
                        
                        if submit_response.status_code == 200:
                            # Poll pour vidéo (même processus que normal)
                            video_query_endpoint = os.getenv('VIDEO_QUERY', 'http://localhost:8383/easy/query')
                            
                            # Poll jusqu'à completion (même que système normal)
                            max_attempts = 300  # 5 minutes max
                            for attempt in range(max_attempts):
                                await asyncio.sleep(1)
                                
                                query_response = await client.get(
                                    f"{video_query_endpoint}?code={job_id}",
                                    timeout=10.0
                                )
                                
                                if query_response.status_code == 200:
                                    query_result = query_response.json()
                                    if query_result.get('status') == 'completed':
                                        video_url = query_result.get('video_url')
                                        
                                        if video_url:
                                            # Générer clé cache vidéo
                                            normalized_text = response_text.lower().strip()
                                            video_key = f"video:url:{hashlib.md5(normalized_text.encode()).hexdigest()}"
                                            
                                            # Cache vidéo URL
                                            self.cache_agent.redis_client.setex(
                                                video_key,
                                                604800,  # 7 jours
                                                video_url
                                            )
                                            
                                            # Marquer comme "completed"
                                            job['status'] = 'completed'
                                            job['completed_at'] = datetime.now().isoformat()
                                            job['video_url'] = video_url
                                            self._update_job_status(job)
                                            
                                            # Retirer de queue
                                            self.cache_agent.redis_client.zrem(
                                                self.pregen_queue_key,
                                                json.dumps(job)
                                            )
                                            
                                            logger.info("Video pre-generated with SAME quality", 
                                                       job_id=job_id,
                                                       video_url=video_url,
                                                       text=response_text[:50])
                                            
                                            return job_id
                            
                            # Timeout
                            raise Exception("Video generation timeout")
                        else:
                            raise Exception(f"Video submission failed: {submit_response.status_code}")
                    else:
                        raise Exception(f"Audio upload failed: {upload_response.status_code}")
                        
            except Exception as e:
                logger.error("Error in video generation pipeline", error=str(e))
                raise
            
        except Exception as e:
            logger.error("Error generating video", error=str(e), job_id=job.get('job_id', 'unknown'))
            job['status'] = 'failed'
            job['error'] = str(e)
            self._update_job_status(job)
            return ""
    
    def _update_job_status(self, job: Dict[str, Any]) -> None:
        """Met à jour le statut d'un job"""
        try:
            status_key = f"{self.pregen_status_key}:{job['job_id']}"
            self.cache_agent.redis_client.setex(
                status_key,
                3600,  # 1 heure
                json.dumps(job)
            )
        except Exception as e:
            logger.error("Error updating job status", error=str(e))
    
    async def pregenerate_top_predictions(self, limit: int = 20) -> List[str]:
        """
        Pré-génère les prédictions les plus probables
        
        Returns:
            List de job IDs
        """
        try:
            # Obtenir top prédictions
            predictions = await self.prediction_agent.get_top_predictions(limit)
            
            job_ids = []
            for pred in predictions:
                response = pred.get('response', '')
                probability = pred.get('probability', 0.0)
                
                if response and probability > 0.1:  # Seuil minimum
                    job_id = await self.add_to_queue(response, priority=probability)
                    if job_id:
                        job_ids.append(job_id)
            
            logger.info("Top predictions queued for pre-generation", 
                       count=len(job_ids))
            
            return job_ids
            
        except Exception as e:
            logger.error("Error pre-generating top predictions", error=str(e))
            return []
    
    async def start_background_worker(self, interval: int = 60) -> None:
        """
        Démarre un worker en arrière-plan qui traite la queue
        
        Args:
            interval: Intervalle entre traitements (secondes)
        """
        logger.info("Background pre-generation worker started", interval=interval)
        
        while True:
            try:
                # Traiter queue
                await self.process_queue()
                
                # Pré-générer top prédictions si queue vide
                queue_size = self.cache_agent.redis_client.zcard(self.pregen_queue_key)
                if queue_size == 0:
                    await self.pregenerate_top_predictions(limit=10)
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error("Error in background worker", error=str(e))
                await asyncio.sleep(interval)
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Récupère le statut d'un job"""
        try:
            status_key = f"{self.pregen_status_key}:{job_id}"
            status_json = self.cache_agent.redis_client.get(status_key)
            
            if status_json:
                return json.loads(status_json)
            return None
            
        except Exception as e:
            logger.error("Error getting job status", error=str(e))
            return None
