import asyncio
import json
import aio_pika
from celery import shared_task
from app.core.settings import settings
from app.websocket.enums import EventType
from loggers import get_logger

logger = get_logger(__name__)


@shared_task
def send_websocket_event(event_type: EventType, data: dict):
    message = json.dumps({"event": event_type, "data": data})
    rabbitmq_dsn = settings.build_rabbitmq_dsn()

    asyncio.run(_send_message(rabbitmq_dsn, message, event_type))


async def _send_message(rabbitmq_dsn: str, message: str, event_type: str):
    """Publishing a message to the durable queue and fanout exchange."""
    connection = None
    try:
        connection = await aio_pika.connect_robust(rabbitmq_dsn)
        channel = await connection.channel()

        # Publish to durable queue (to store history)
        durable_queue_name = f"channel_name"
        await channel.declare_queue(
            durable_queue_name,
            durable=True,
            auto_delete=False,
            arguments={"x-message-ttl": 300000}
        )
        message_obj = aio_pika.Message(
            body=message.encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        await channel.default_exchange.publish(
            message_obj,
            routing_key=durable_queue_name,
            mandatory=True
        )

        # Publish in fanout exchange for live mailing
        exchange_name = f"exchange_channel_name"
        exchange = await channel.declare_exchange(
            exchange_name,
            aio_pika.ExchangeType.FANOUT,
            durable=True
        )
        live_message_obj = aio_pika.Message(
            body=message.encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        await exchange.publish(live_message_obj, routing_key="")

        logger.info("Event type: %s, Message sent successfully to durable queue %s and exchange %s: %s",
                    event_type, durable_queue_name, exchange_name, message)

    except Exception as e:
        logger.error("Error sending message to RabbitMQ: %s", e)
    finally:
        if connection:
            await connection.close()