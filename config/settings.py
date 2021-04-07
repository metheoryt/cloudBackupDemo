from pathlib import Path

from pydantic import BaseSettings, FilePath, DirectoryPath


class Settings(BaseSettings):
    class Config:
        env_file = '.env'  # name of file with environment variables, relative to project root

    archive_temp_storage_dir: DirectoryPath = Path('/tmp/')
    """Temporary local storage directory for uploaded archives"""

    providers_config_path: FilePath = Path('config/providers.yml')
    """Path to cloud providers YAML-config"""

    logging_config_path: FilePath = Path('config/logging.yml')
    """Path to logging YAML-config"""

    basic_auth_username: str = None
    basic_auth_password: str = None
    """Basic Authentication username/password"""


settings = Settings()
