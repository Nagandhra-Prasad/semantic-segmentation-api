from urllib.parse import urlparse

from beanie import init_beanie
from pymongo import AsyncMongoClient

from app.core.config import settings
from app.db.models.activity import UserActivity
from app.db.models.processing_job import ProcessingJob
from app.db.models.report import Report
from app.db.models.upload import Upload
from app.db.models.user import User

client: AsyncMongoClient | None = None
_beanie_initialized = False


def _connection_string() -> str:
    uri = settings.MONGODB_URI.rstrip("/")
    parsed = urlparse(uri)
    if not parsed.path or parsed.path == "/":
        return f"{uri}/{settings.MONGODB_DB_NAME}"
    return uri


async def connect_to_mongo() -> None:
    global client, _beanie_initialized
    if _beanie_initialized:
        return

    connection = _connection_string()
    client = AsyncMongoClient(connection)
    await init_beanie(
        database=client[settings.MONGODB_DB_NAME],
        document_models=[User, Upload, ProcessingJob, Report, UserActivity],
    )
    _beanie_initialized = True


async def close_mongo_connection() -> None:
    global client, _beanie_initialized
    if client is not None:
        await client.close()
        client = None
    _beanie_initialized = False
