import aio_pika

from fastapi import WebSocket, WebSocketDisconnect, HTTPException

from app.core.settings import settings

from loggers import get_logger

logger = get_logger(__name__)


class WebSocketManager:
    """WebSocket connection manager with history saving (long queue) and live distribution via fanout Exchange."""
    def __init__(self, websocket: WebSocket, branch_id: str):
        self.websocket = websocket
        self.branch_id = branch_id
        self.rabbitmq_dsn = settings.build_rabbitmq_dsn()
        self.connection = None
        self.channel = None
        self.queue = None

    async def accept_connection(self):
        """Accepts the connection and validates the token"""
        await self.websocket.accept()
        token = self.websocket.query_params.get("token")
        if not token:
            await self.websocket.close(code=4001)
            return False
        try:
            # call some service
            pass
        except HTTPException:
            await self.websocket.close(code=4001)
            return False
        return True

    async def connect_rabbitmq(self):
        """
        Connects to RabbitMQ:
          1. Declares a durable queue (queue_branch_{branch_id}) to store old messages with a TTL of 5 minutes.
          2. Processes old messages from this queue.
          3. Declares durable fanout exchange (exchange_branch_{branch_id}) for live distribution.
          4. Creates a temporary (exclusive, auto_delete) queue tied to exchange for live messages.
        """
        try:
            self.connection = await aio_pika.connect_robust(self.rabbitmq_dsn)
            self.channel = await self.connection.channel()

            # 1. Declare a durable queue to store old messages
            durable_queue_name = f"queue_branch_{self.branch_id}"
            durable_queue = await self.channel.declare_queue(
                durable_queue_name,
                durable=True,
                auto_delete=False,
                arguments={"x-message-ttl": 300000}  # TTL 5 минут
            )

            # 2. Process old messages (if any)
            await self.process_old_messages(durable_queue)

            # 3. Declare durable fanout exchange for live messages
            exchange_name = f"exchange_branch_{self.branch_id}"
            exchange = await self.channel.declare_exchange(
                exchange_name,
                aio_pika.ExchangeType.FANOUT,
                durable=True
            )

            # 4. Create a temporary queue for a live subscription and link it to exchange
            self.queue = await self.channel.declare_queue("", exclusive=True, auto_delete=True)
            await self.queue.bind(exchange, routing_key="")

            logger.info(
                f"WebSocket subscribed to exchange {exchange_name} with temporary queue {self.queue.name}"
            )

            # Process live messages from the temporary queue
            async with self.queue.iterator() as queue_iter:
                async for message in queue_iter:
                    try:
                        message_data = message.body.decode()
                        logger.info("WebSocket sending real-time message: %s", message_data)
                        await self.websocket.send_text(message_data)
                        await message.ack()
                    except (WebSocketDisconnect, RuntimeError):
                        logger.info("WebSocket disconnected or closed, stopping message processing.")
                        break
                    except Exception as e:
                        logger.error("Error sending real-time message: %s", e)
                        await message.nack(requeue=True)
                        break

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for branch {self.branch_id}")
        except Exception as e:
            logger.error(f"RabbitMQ error for branch {self.branch_id}: {e}")
        finally:
            await self.cleanup()

    async def process_old_messages(self, durable_queue):
        """
        Retrieves and sends old messages from the durable queue.
        """
        while True:
            try:
                message = await durable_queue.get(timeout=1.0, no_ack=True)
            except aio_pika.exceptions.QueueEmpty:
                logger.info("No old messages in durable queue, moving to live subscription.")
                break

            try:
                message_data = message.body.decode()
                logger.info("WebSocket sending old message: %s", message_data)
                await self.websocket.send_text(message_data)
            except (WebSocketDisconnect, RuntimeError):
                logger.info("WebSocket disconnected or closed during old message processing, dropping message.")
                break
            except Exception as e:
                logger.error("Error sending old message: %s", e)
                break

    async def cleanup(self):
        """Closes the connection to RabbitMQ when the WebSocket is disconnected"""
        if self.connection:
            await self.connection.close()
        logger.info(f"WebSocket closed for branch {self.branch_id}")
