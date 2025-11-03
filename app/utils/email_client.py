import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

async def send_verification_email(to_email: str, subject: str, body: str):
    """Send email through external Spring Boot email service."""
    async with httpx.AsyncClient() as client:
        form_data = {
            "to": to_email,
            "subject": subject,
            "body": body
        }

         # Allow up to 20 seconds total, 5s to connect
        timeout = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=5.0)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(settings.EMAIL_SERVICE_URL, data=form_data)
                response.raise_for_status()

                # Try parsing JSON safely
                try:
                    return response.json()
                except ValueError:
                    logger.warning(f"Non-JSON response from email service: {response.text}")
                    return {"status": "success", "raw_response": response.text}

        except httpx.RequestError as exc:
            logger.error(f"Error sending email: {exc}")
            raise RuntimeError(f"Email service unreachable: {exc}")
        except httpx.HTTPStatusError as exc:
            logger.error(f"Email service returned HTTP {exc.response.status_code}: {exc.response.text}")
            raise RuntimeError(f"Email service error: {exc.response.status_code}")
