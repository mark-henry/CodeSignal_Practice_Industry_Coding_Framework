from copy import deepcopy, copy
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class File:
    name: str
    size: str
    expiry: datetime = None


class FileHosting:
    def __init__(self):
        self.files = {}
        self.history = []

    def _save_history(self, time):
        self.history.append((time, deepcopy(self.files)))

    def file_upload(self, file_name, size):
        """  - Upload the file to the remote storage server.
          - If a file with the same name already exists on the server, it throws a runtime exception.
        """
        if file_name in self.files:
            raise FileExistsError
        self.files[file_name] = File(file_name, size)

    def file_get(self, file_name):
        """Returns the size of the file, or nothing if the file doesn't exist."""
        file = self.files.get(file_name)
        return file and file.size

    def file_copy(self, source, dest):
        """Copy the source file to a new location.
          - If the source file doesn’t exist, it throws a runtime exception.
          - If the destination file already exists, it overwrites the existing file."""
        if source not in self.files:
            raise FileNotFoundError
        self.files[dest] = copy(self.files[source])
        self.files[dest].name = dest

    def _search(self, prefix):
        results = [file for file in self.files.values() if file.name.startswith(prefix)]
        results.sort(key=lambda f: f.name)
        results.sort(key=lambda f: f.size, reverse=True)
        return results

    def file_search(self, prefix):
        results = self._search(prefix)
        return [file.name for file in results]

    def file_upload_at(self, timestamp, file_name, file_size, ttl=None):
        if file_name in self.files:
            raise FileExistsError
        time = datetime.fromisoformat(timestamp)
        self._save_history(time)
        expiry = ttl and time + timedelta(seconds=ttl)
        self.files[file_name] = File(file_name, file_size, expiry)

    def file_get_at(self, timestamp, file_name):
        file = self.files.get(file_name)
        if not file:
            return None
        expired = file.expiry and file.expiry < datetime.fromisoformat(timestamp)
        return file.size if not expired else None

    def file_copy_at(self, timestamp, file_from, file_to):
        self._save_history(datetime.fromisoformat(timestamp))
        return self.file_copy(file_from, file_to)

    def file_search_at(self, timestamp, prefix):
        timestamp = datetime.fromisoformat(timestamp)
        return [file.name for file in self._search(prefix) if not file.expiry or file.expiry > timestamp]

    def rollback(self, timestamp):
        timestamp = datetime.fromisoformat(timestamp)
        for time, state in self.history:
            if time <= timestamp:
                self.files = state


def simulate_coding_framework(commands):
    """
    Simulates a coding framework operation on a list of lists of strings.

    Parameters:
    list_of_lists (List[List[str]]): A list of lists containing strings.
    """
    fh = FileHosting()
    return [
        getattr(fh, command[0].lower())(*command[1:])
        for command in commands
    ]
