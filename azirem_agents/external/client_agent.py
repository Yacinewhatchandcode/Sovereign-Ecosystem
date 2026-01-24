"""
Client Agent - Frontend request handler with validation and dispatch
First point of contact for all user requests
"""
import structlog
import time

logger = structlog.get_logger()

class ClientAgent:
    """Agent responsible for handling client requests"""

    def __init__(self):
        self.orchestrator = OrchestratorAgent()
        logger.info("ClientAgent initialized")

    def validate_request(self, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate incoming request
        Returns (is_valid, error_message)
        """
        if not data:
            return False, "Invalid request body"

        message = data.get('message', '').strip()
        if not message:
            return False, "Message is required"

        if len(message) > 1000:
            return False, "Message too long (max 1000 characters)"

        return True, None

    async def handle_chat(self, data: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Handle chat request
        Returns response dict
        """
        start_time = time.time()

        # Validate request
        is_valid, error = self.validate_request(data)
        if not is_valid:
            return {
                "success": False,
                "error": error
            }

        message = data.get('message', '').strip()
        generate_audio = data.get('generate_audio', True)

        logger.info("Client request received", message=message[:50], user_id=user_id)

        try:
            # Process through orchestrator
            result = await self.orchestrator.process_message(
                query=message,
                user_id=user_id,
                generate_audio=generate_audio
            )

            # Add timing info
            elapsed = time.time() - start_time
            result["processing_time"] = round(elapsed, 2)

            logger.info("Client request completed",
                       message=message[:50],
                       elapsed=elapsed,
                       cached=result.get("cached", False))

            return result

        except Exception as e:
            logger.error("Client request error", error=str(e), message=message[:50])
            return {
                "success": False,
                "error": str(e),
                "response": f"Sorry, I encountered an error. Please try again."
            }