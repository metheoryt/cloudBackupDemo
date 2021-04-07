import os
import shutil
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from pydantic import DirectoryPath

from config.settings import settings
import logging

log = logging.getLogger(__name__)


@contextmanager
def temp_archive_path(path: DirectoryPath, backup_time: datetime) -> Path:
    """A context manager. Archives specified path to a .tar.gz file,
    and places into directory, specified in archive_temp_storage_dir settings var
    When exiting from the context, archive is deleted
    :param path: a path to archive
    :param backup_time: datetime, appends to an archive name
    :returns: full local path to a created archive
    """
    archive_name = str(path).replace(':', '').replace(os.path.sep, '_')
    archive_name = backup_time.strftime(f'{archive_name}_%Y%m%d_%H%M%S%f')

    archive_path = settings.archive_temp_storage_dir.joinpath(archive_name)
    # creating an archive to upload, returning filename of the archive
    log.info(f'archiving {path} into {archive_path}')
    archive_filename = shutil.make_archive(archive_path, 'gztar', root_dir=str(path))

    try:
        yield Path(archive_filename)
    finally:
        # remove created archive in case of any error during it's upload
        os.remove(archive_filename)
