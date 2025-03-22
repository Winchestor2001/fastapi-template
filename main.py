import asyncio

import sentry_sdk
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from app.database.database import init_models
from app.core.middleware import ValidationErrorMiddleware, UnexpectedErrorMiddleware, DatabaseErrorMiddleware
from app.integrations.redis.redis_client import redis_client
from app.core.routes import v1
from app.core.settings import settings
from loggers import get_logger

logger = get_logger(__name__)


# Code entrypoint


def get_application() -> FastAPI:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for tracing.
        traces_sample_rate=1.0,
        _experiments={
            # Set continuous_profiling_auto_start to True
            # to automatically start the profiler on when
            # possible.
            "continuous_profiling_auto_start": True,
        },
    )
    application = FastAPI(
        title=settings.project_name,
        debug=settings.debug,
        version=settings.version,
    )

    application.include_router(v1, prefix="/api/v1")
    logger.info(f"Total endpoints: %s", len(application.routes))

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Sentry middleware for error tracking
    application.add_middleware(SentryAsgiMiddleware)  # noqa
    application.add_middleware(ValidationErrorMiddleware)  # noqa
    application.add_middleware(DatabaseErrorMiddleware)  # noqa
    application.add_middleware(UnexpectedErrorMiddleware)  # noqa

    add_pagination(application)

    @application.on_event("startup")
    async def startup_event():
        try:
            await redis_client.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.info(f"Failed to connect to Redis: {e}")
            raise

    @application.on_event("shutdown")
    async def shutdown_event():
        await redis_client.close()

    # @application.on_event("shutdown")
    # async def shutdown_event():
    #     driver_ws_manager = BaseRedisWebSocketManager(redis_prefix="driver")
    #     user_ws_manager = BaseRedisWebSocketManager(redis_prefix="users")
    #
    #     await driver_ws_manager.clean_worker_connections()
    #     await user_ws_manager.clean_worker_connections()
    #     await redis_client.close()

    return application


app = get_application()

if __name__ == "__main__":
    asyncio.run(init_models())
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)