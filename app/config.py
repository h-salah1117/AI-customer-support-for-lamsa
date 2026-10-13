import tomllib
from pathlib import Path
    
ROOT = Path(__file__).resolve().parents[1]    
with open(ROOT / "config.toml", "rb") as file:
    config = tomllib.load(file)

PRODUCTS_PATH = ROOT / config["data"]["products_path"]
