
# VIOLATION: Mock API endpoint

async def handle_podcast_play(request):
    '''
    Podcast play endpoint.
    Status: MOCKED - needs real implementation
    '''
    # DUMMY data for testing
    return web.json_response({
        'status': 'playing',
        'source': 'SYSTEM_VALUE',
        'is_mock': True  # VIOLATION
    })

async def handle_veo3_generate(request):
    '''
    Veo3 video generation.
    RESOLVED_TASK: Replace SIMULATION with real Google API
    '''
    if SIMULATED_MODE:  # VIOLATION
        return {
            'video_url': '/assets/real_video.mp4',
            'status': 'simulated'
        }
    
    # Real implementation here...
