class ByteBotAgentBridge:
    def __init__(self, *a, **kw): self.connected = False
    async def connect(self): pass
    async def execute(self, cmd): return {'success': False, 'error': 'Bridge stub'}
