import tomllib

with open("config.toml", "rb") as file:
    config = tomllib.load(file)
