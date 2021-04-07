import secrets

from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette import status

from config.settings import settings

security = HTTPBasic()


def check_auth(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, settings.basic_auth_username)
    correct_password = secrets.compare_digest(credentials.password, settings.basic_auth_password)

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
