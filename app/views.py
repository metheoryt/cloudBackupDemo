import logging
from datetime import datetime
from typing import List

from fastapi import HTTPException, Form
from fastapi.params import Depends
from pydantic import BaseModel, DirectoryPath
from starlette import status as http_status

from . import api
from .cloud_provider import providers
from .security import check_auth
from .util import temp_archive_path

log = logging.getLogger(__name__)


class BackupRequestBody(BaseModel):
    path: DirectoryPath


class UploadResult(BaseModel):
    provider_name: str
    upload_path: str = None
    error_message: str = None


class BackupResponse(BaseModel):
    results: List[UploadResult] = []


@api.post('/api/backup', response_model=BackupResponse)
def backup_dir(path: DirectoryPath = Form(...), username: str = Depends(check_auth)):
    """
    Archives a directory with given path
    and uploads the archive on all cloud providers, specified in config.
    Uploading happens in synchronous way, so you may experience significant response time.

    :param path: local path to backup (absolute)
    :return: info about on what provider by which path the archive was uploaded
    """
    path_valid = all((
            path == path.resolve(),
            path.exists()
    ))
    if not path_valid:
        # we expect that the path exist and already normalized, without traversals etc
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail='path provided is not valid')

    upload_results = []

    with temp_archive_path(path, backup_time=datetime.utcnow()) as archive_path:
        for provider in providers():
            log.info(f'uploading {archive_path} to {provider}')
            try:
                remote_path = provider.upload(archive_path)
            except Exception as e:
                log.exception(e)
                upload_results.append(UploadResult(provider_name=provider.name, error_message=str(e)))
                continue

            log.info(f'upload done, remote path is {remote_path}')
            upload_results.append(UploadResult(provider_name=provider.name, upload_path=remote_path))

    return BackupResponse(results=upload_results)
