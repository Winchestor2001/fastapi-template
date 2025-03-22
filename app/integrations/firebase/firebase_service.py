import asyncio
from typing import Dict, List, Optional

import firebase_admin
from firebase_admin import credentials, messaging

from loggers import get_logger

logger = get_logger(__name__)


class FirebaseService:
    """Singleton class for Firebase push notification service."""

    _instance = None  # Global instance for Singleton
    _firebase_initialized = False  # Flag to prevent multiple Firebase initializations

    def __new__(cls, credentials_data: Dict):
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
        return cls._instance

    def __init__(self, credentials_data: Dict):
        """
        Initialize Firebase only once.

        :param credentials_data: Dictionary with Firebase Admin SDK credentials (JSON)
        """
        if not self._firebase_initialized:
            try:
                if "private_key" in credentials_data:
                    credentials_data["private_key"] = credentials_data["private_key"].replace("\\n", "\n")

                cred = credentials.Certificate(credentials_data)
                firebase_admin.initialize_app(cred)
                self._firebase_initialized = True
                logger.info("Firebase successfully initialized")
            except ValueError:
                logger.warning("Firebase already initialized. Skipping reinitialization.")

    async def send_notification(self, firebase_id: str, title: str, body: str, data: Optional[Dict] = None):
        """
        Sends a single push notification to the users.

        :param firebase_id: Firebase users token
        :param title: Notification title
        :param body: Notification text
        :param data: JSON data (optional)
        """
        message = messaging.Message(
            token=firebase_id,
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
        )
        loop = asyncio.get_running_loop()
        try:
            response = await loop.run_in_executor(None, messaging.send, message)
            return response
        except messaging.UnregisteredError:
            logger.warning(f"Invalid firebase_id: {firebase_id}. Skipping notification.")
            return None
        except Exception as e:
            logger.error(f"Error sending push notification: {e}", exc_info=True)
            return None

    def send_notification_sync(self, firebase_id: str, title: str, body: str, data: Optional[Dict] = None):
        """
        Sends a single push notification to the users.

        :param firebase_id: Firebase users token
        :param title: Notification title
        :param body: Notification text
        :param data: JSON data (optional)
        """
        message = messaging.Message(
            token=firebase_id,
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
        )
        try:
            response = messaging.send(message)
            return response
        except messaging.UnregisteredError:
            logger.warning(f"Invalid firebase_id: {firebase_id}. Skipping notification.")
            return None
        except Exception as e:
            logger.error(f"Error sending push notification: {e}", exc_info=True)
            return None

    async def send_notification_with_data(self, firebase_id: str, title: str, body: str, extra_data: Dict):
        """
        Sends a push notification with additional JSON data.

        :param firebase_id: Firebase users token
        :param title: Notification title
        :param body: Notification text
        :param extra_data: JSON data attached to the notification
        """
        return await self.send_notification(firebase_id, title, body, extra_data)

    async def send_bulk_notifications(self, firebase_ids: List[str], title: str, body: str,
                                      data: Optional[Dict] = None):
        """
        Sends bulk push notifications.

        :param firebase_ids: List of Firebase users tokens
        :param title: Notification title
        :param body: Notification body text
        :param data: Additional JSON data (optional)
        """
        if not firebase_ids:
            return {"success": 0, "failures": 0}

        messages = [
            messaging.Message(
                token=firebase_id,
                notification=messaging.Notification(title=title, body=body),
                data=data or {},
            )
            for firebase_id in firebase_ids
        ]

        loop = asyncio.get_running_loop()
        try:
            response = await loop.run_in_executor(None, messaging.send_all, messages)
            logger.info(f"Bulk notification sent: {response.success_count} success, {response.failure_count} failures")
            return {"success": response.success_count, "failures": response.failure_count}
        except Exception as e:
            logger.error(f"Error sending bulk notifications: {e}", exc_info=True)
            return {"success": 0, "failures": len(firebase_ids)}

    def prepare_bulk_notifications(
            self, firebase_ids: List[str], title: str, body: str, data: Optional[Dict] = None
    ) -> List[messaging.Message]:
        """
        Prepare a list of Firebase messages in batches, without sending them.

        :param firebase_ids: List of Firebase users tokens
        :param title: Notification title
        :param body: Notification text
        :param data: Additional JSON data (optional)
        :return: List of messaging.Message objects ready to be sent
        """
        if not firebase_ids:
            return []

        messages = []
        for firebase_id in firebase_ids:
            msg = messaging.Message(
                token=firebase_id,
                notification=messaging.Notification(title=title, body=body),
                data=data or {},
            )
            messages.append(msg)
        logger.info(f"Prepared {len(messages)} messages for bulk notification")
        return messages

    def send_all_notifications(self, messages: List[messaging.Message]):
        """
        Sends push notifications in batches of 500 messages.

        :param messages: List of Firebase messages.
        """
        batch_size = 500  # Firebase max limit
        results = {"success": 0, "failures": 0}

        for i in range(0, len(messages), batch_size):
            batch = messages[i:i + batch_size]
            try:
                response = messaging.send_each(messages=batch)
                logger.info(f"\nFirebase batch response:{response}\n")
                results["success"] += response.success_count
                results["failures"] += response.failure_count
                logger.info(f"Batch sent: {response.success_count} success, {response.failure_count} failures")
            except Exception as e:
                logger.error(f"Error sending batch: {e}", exc_info=True)
                results["failures"] += len(batch)

        return results


_firebase_service_instance = None


def get_firebase_service():
    """Returns the Singleton instance of FirebaseService."""
    global _firebase_service_instance
    if _firebase_service_instance is None:
        from app.core.settings import settings
        _firebase_service_instance = FirebaseService(settings.build_firebase())
    return _firebase_service_instance