#!/usr/bin/env python3
"""
🎬 AZIREM PODCAST RECORDER - Episode Recording & Export
========================================================
Records full podcast sessions and exports as MP4/MP3 with show notes.
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import subprocess
import tempfile


class PodcastRecorder:
    """Records and exports podcast episodes."""
    
    def __init__(self, output_dir: str = "/tmp/azirem_podcasts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.current_session = None
        self.transcript = []
        
    def start_session(self, title: str = None) -> str:
        """Start a new recording session."""
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_session = {
            "id": session_id,
            "title": title or f"AZIREM Podcast {session_id}",
            "started_at": datetime.now().isoformat(),
            "transcript": [],
            "audio_segments": []
        }
        print(f"🎙️ Recording started: {self.current_session['title']}")
        return session_id
        
    def add_exchange(self, user_input: str, azirem_response: str, audio_path: str = None):
        """Add a conversation exchange to the recording."""
        if not self.current_session:
            raise ValueError("No active session. Call start_session() first.")
            
        exchange = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "azirem": azirem_response,
            "audio_path": audio_path
        }
        
        self.current_session["transcript"].append(exchange)
        if audio_path:
            self.current_session["audio_segments"].append(audio_path)
            
    async def export_mp3(self) -> str:
        """Export session as MP3 audio."""
        if not self.current_session:
            raise ValueError("No active session")
            
        session_id = self.current_session["id"]
        output_file = self.output_dir / f"{session_id}.mp3"
        
        # Concatenate audio segments
        audio_files = self.current_session["audio_segments"]
        if not audio_files:
            print("⚠️ No audio segments to export")
            return None
            
        # Create file list for ffmpeg
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            for audio_file in audio_files:
                f.write(f"file '{audio_file}'\n")
            list_file = f.name
            
        try:
            # Concatenate with ffmpeg
            cmd = [
                'ffmpeg', '-f', 'concat', '-safe', '0',
                '-i', list_file,
                '-c:a', 'libmp3lame', '-b:a', '192k',
                str(output_file), '-y'
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ MP3 exported: {output_file}")
            return str(output_file)
        except subprocess.CalledProcessError as e:
            print(f"❌ FFmpeg error: {e.stderr.decode()}")
            return None
        finally:
            Path(list_file).unlink()
            
    async def export_mp4(self, avatar_video: str = None) -> str:
        """Export session as MP4 video."""
        if not self.current_session:
            raise ValueError("No active session")
            
        session_id = self.current_session["id"]
        output_file = self.output_dir / f"{session_id}.mp4"
        
        # First create MP3
        audio_file = await self.export_mp3()
        if not audio_file:
            return None
            
        # If avatar video provided, combine
        if avatar_video and Path(avatar_video).exists():
            cmd = [
                'ffmpeg',
                '-i', avatar_video,
                '-i', audio_file,
                '-c:v', 'copy', '-c:a', 'aac',
                '-shortest',
                str(output_file), '-y'
            ]
        else:
            # Create video from static image + audio
            # Generate a simple waveform visualization
            cmd = [
                'ffmpeg',
                '-i', audio_file,
                '-filter_complex',
                '[0:a]showwaves=s=1280x720:mode=line:rate=25,format=yuv420p[v]',
                '-map', '[v]', '-map', '0:a',
                '-c:v', 'libx264', '-c:a', 'aac',
                str(output_file), '-y'
            ]
            
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ MP4 exported: {output_file}")
            return str(output_file)
        except subprocess.CalledProcessError as e:
            print(f"❌ FFmpeg error: {e.stderr.decode()}")
            return None
            
    def generate_show_notes(self) -> str:
        """Generate markdown show notes from transcript."""
        if not self.current_session:
            raise ValueError("No active session")
            
        session = self.current_session
        notes = [
            f"# {session['title']}",
            "",
            f"**Recorded:** {session['started_at']}",
            f"**Duration:** {len(session['transcript'])} exchanges",
            "",
            "## Transcript",
            ""
        ]
        
        for i, exchange in enumerate(session['transcript'], 1):
            notes.append(f"### Exchange {i}")
            notes.append(f"**You:** {exchange['user']}")
            notes.append("")
            notes.append(f"**AZIREM:** {exchange['azirem'][:500]}...")
            notes.append("")
            
        show_notes = "\n".join(notes)
        
        # Save to file
        session_id = session["id"]
        notes_file = self.output_dir / f"{session_id}_notes.md"
        notes_file.write_text(show_notes)
        
        print(f"✅ Show notes: {notes_file}")
        return str(notes_file)
        
    def end_session(self) -> Dict:
        """End the current session and return summary."""
        if not self.current_session:
            raise ValueError("No active session")
            
        session = self.current_session
        session["ended_at"] = datetime.now().isoformat()
        
        # Save session metadata
        session_file = self.output_dir / f"{session['id']}_session.json"
        session_file.write_text(json.dumps(session, indent=2))
        
        summary = {
            "session_id": session["id"],
            "title": session["title"],
            "exchanges": len(session["transcript"]),
            "audio_segments": len(session["audio_segments"]),
            "session_file": str(session_file)
        }
        
        self.current_session = None
        return summary


# CLI
async def main():
    """Demo the recorder."""
    recorder = PodcastRecorder()
    
    # Start session
    session_id = recorder.start_session("Demo Podcast")
    
    # Add some exchanges
    recorder.add_exchange(
        "What is AZIREM?",
        "AZIREM is a sovereign AI orchestration system...",
        None  # Would be actual audio path
    )
    
    # Generate show notes
    notes = recorder.generate_show_notes()
    print(f"\nShow notes: {notes}")
    
    # End session
    summary = recorder.end_session()
    print(f"\nSession summary: {summary}")


if __name__ == "__main__":
    asyncio.run(main())
