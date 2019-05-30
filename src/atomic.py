import os
from contextlib import contextmanager
from tempfile import NamedTemporaryFile


@contextmanager
def atomic_replace(dest):
    """Atomically replace the file at `dest` with a new file.

    If atomic replacement fails, remove `dest` and replace non-atomically.
    If all replacement fails, delete the temporary file.
    """
    with NamedTemporaryFile(
        mode="r+",
        dir=str(dest.parent),
        encoding='utf-8',
        delete=False,
        prefix=dest.name + '.temp-'
    ) as temp:
        try:
            yield temp

            temp.flush()
            os.fsync(temp.fileno())
            temp.close()

            temp_path = temp.name
            dest_path = str(dest)

            try:
                os.replace(temp_path, dest_path)
            except PermissionError:
                print('Could not atomically replace {}.'.format(dest_path))
                os.unlink(dest_path)
                os.replace(temp_path, dest_path)
        finally:
            try:
                os.unlink(temp_path)
            except FileNotFoundError:
                pass
