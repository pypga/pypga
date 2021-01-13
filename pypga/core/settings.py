from pathlib import Path
from pydantic import BaseSettings


ROOT_PATH = Path(__file__).parent.parent.parent.resolve()


class Settings(BaseSettings):
    class Config:
        env_prefix = "pypga_"

    result_path: Path = ROOT_PATH / "./out"
    build_path: Path = ROOT_PATH / "./build"


settings = Settings()