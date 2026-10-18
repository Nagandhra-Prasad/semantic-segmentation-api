from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "Semantic Segmentation API"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    SECRET_KEY: str = "change-me-to-a-long-random-secret"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "semantic_segmentation"

    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    UPLOAD_DIR: str = "storage/uploads"
    RESULT_DIR: str = "storage/results"
    REPORT_DIR: str = "storage/reports"
    MAX_UPLOAD_SIZE_MB: int = 100
    DATASET_MAX_IMAGES: int = 30
    ALLOWED_IMAGE_EXTENSIONS: str = ".jpg,.jpeg,.png,.webp,.bmp"
    ALLOWED_VIDEO_EXTENSIONS: str = ".mp4,.avi,.mov,.mkv"

    SEGFORMER_MODEL_ID: str = "nvidia/segformer-b0-finetuned-cityscapes-1024-1024"
    MODEL_DEVICE: str = "cpu"
    VIDEO_MAX_FRAMES: int = 30
    VIDEO_FRAME_INTERVAL: int = 5
    RESULT_VIDEO_FPS: float = 8.0
    REFERENCE_MODEL_MIOU: float = 0.78

    CITYSCAPES_DATA_ROOT: str = "data/cityscapes"

    ADMIN_EMAIL: str = "admin@segvision.dev"
    ADMIN_PASSWORD: str = "Admin@12345"
    ADMIN_FULL_NAME: str = "System Administrator"

    @property
    def upload_path(self) -> Path:
        return BASE_DIR / self.UPLOAD_DIR

    @property
    def result_path(self) -> Path:
        return BASE_DIR / self.RESULT_DIR

    @property
    def report_path(self) -> Path:
        return BASE_DIR / self.REPORT_DIR

    @property
    def cityscapes_path(self) -> Path:
        return BASE_DIR / self.CITYSCAPES_DATA_ROOT

    @property
    def allowed_image_exts(self) -> set[str]:
        return {e.strip().lower() for e in self.ALLOWED_IMAGE_EXTENSIONS.split(",")}

    @property
    def allowed_video_exts(self) -> set[str]:
        return {e.strip().lower() for e in self.ALLOWED_VIDEO_EXTENSIONS.split(",")}

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


settings = Settings()
