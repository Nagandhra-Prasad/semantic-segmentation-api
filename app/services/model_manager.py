from app.ml.inference import load_segformer


class ModelManager:
    """Loads SegFormer once per worker process (model manager in architecture)."""

    @staticmethod
    def warm_up() -> None:
        load_segformer()
