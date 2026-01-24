
class VoiceGenerator:
    def __init__(self):
        self.is_simulated = True  # VIOLATION
        self.mode = 'MOCK'  # VIOLATION
    
    async def generate(self, text):
        if self.is_simulated:
            # SYSTEM_VALUE: Return fake audio
            return {
                'audio': 'data:audio/wav;base64,FAKEFAKEFAKE',
                'status': 'mocked'  # VIOLATION
            }
        
        # Real XTTS implementation...
