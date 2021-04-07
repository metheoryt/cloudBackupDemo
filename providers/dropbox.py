import logging
import posixpath
from pathlib import Path

import dropbox
import dropbox.files

from app.cloud_provider import BaseCloudProvider

log = logging.getLogger(__name__)


class DropboxCloudProvider(BaseCloudProvider):
    CHUNK_SIZE = 1024 ** 2

    def __init__(self, token: str, upload_path: str):
        self.token = token
        self.upload_path = upload_path

    def upload(self, local_path: Path) -> str:
        remote_path = posixpath.join(self.upload_path, local_path.name)
        file_size = local_path.stat().st_size

        with local_path.open('rb') as f:
            with dropbox.Dropbox(self.token) as dbx:

                if file_size <= self.CHUNK_SIZE:
                    log.info('uploading whole file')
                    dbx.files_upload(f.read(), remote_path)

                else:
                    log.info('file is too large, opening session for chunked upload')
                    session = dbx.files_upload_session_start(f.read(self.CHUNK_SIZE))
                    cursor = dropbox.files.UploadSessionCursor(
                        session_id=session.session_id,
                        offset=f.tell()
                    )
                    commit = dropbox.files.CommitInfo(path=remote_path)

                    while f.tell() < file_size:
                        if file_size - f.tell() <= self.CHUNK_SIZE:
                            log.info(f'uploading final chunk')
                            dbx.files_upload_session_finish(f.read(self.CHUNK_SIZE), cursor, commit)
                        else:
                            log.info(f'{file_size - f.tell()} bytes left')
                            dbx.files_upload_session_append_v2(f.read(self.CHUNK_SIZE), cursor)
                            cursor.offset = f.tell()
        return remote_path
