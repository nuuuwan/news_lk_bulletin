import os
import pathlib

import requests
from utils import File, Log

log = Log('WWW')


class WWW:
    def __init__(self, url: str):
        self.url = url

    def download(self, path: pathlib.Path):
        if os.path.exists(path):
            log.info(f'File already exists: {path}')
            return

        log.info(f'Downloading {self.url} to {path}')
        response = requests.get(self.url)
        output_file = File(path)
        output_file.write(response.text)
        file_size = os.path.getsize(path)
        log.info(f'Downloaded {self.url} to {path} ({file_size:,}B)')
