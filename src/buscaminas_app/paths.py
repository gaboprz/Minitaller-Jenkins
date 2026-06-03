from pathlib import Path
import os


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = PROJECT_ROOT / "Datos"


def data_dir() -> Path:
    return Path(os.environ.get("BUSCAMINAS_DATA_DIR", DEFAULT_DATA_DIR))


def asset_path(name: str) -> Path:
    return data_dir() / name


def ranking_path() -> Path:
    return data_dir() / "data.json"
