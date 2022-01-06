from pydantic import BaseSettings


class Settings(BaseSettings):
    api_key: str
    num_outputs: int = 1
    clip_guidance_scale: int = 0

    class Config:
        env_file = ".env"