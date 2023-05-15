import os
from functools import lru_cache

from pydantic import BaseSettings, Extra

from app.adapters.secret_manager import SecretsManager
from app.utils import logger as _logger


logger = _logger.get_logger()



class Settings(BaseSettings, extra=Extra.ignore):
    SQL_HOST: str
    SQL_USER: str
    SQL_PASSWORD: str
    SQL_DATABASE: str

class SettingsLocal(BaseSettings):
    AWS_PROFILE: str
    AWS_SECRET_ID: str
    SQL_HOST: str
    SQL_USER: str
    SQL_PASSWORD: str
    SQL_DATABASE: str
    class Config:
        env_file = ".env"
        extra = Extra.ignore


@lru_cache()
def get_settings():
    environment = os.getenv("ENVIRONMENT")
    logger.info(f"environment: {environment}")
    if environment == "local":
        return SettingsLocal()

    elif os.getenv("FORCE_SECRETS_AWS_FROM_LOCAL"):
        settings_tmp = SettingsLocal()
        secret_id = settings_tmp.AWS_SECRET_ID
        # AWS_PROFILE for production is not necesary but on local we need select the aws profile
        # in order to get the secrets. 
        os.environ["AWS_PROFILE"] = settings_tmp.AWS_PROFILE

    else:
        # in production the lambda has this value, witch is set at building time
        secret_id = os.getenv("AWS_SECRET_ID")

        secret_manager = SecretsManager()
        secrets= secret_manager.get_secret(secret_id)
        database_credentialas = {
            "SQL_HOST": secrets.get("host"),
            "SQL_USER": secrets.get("username"),
            "SQL_PASSWORD": secrets.get("password"),
            "SQL_DATABASE": secrets.get("dbname"),
        }
        return Settings(**database_credentialas)


