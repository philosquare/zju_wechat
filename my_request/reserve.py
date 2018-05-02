import requests

from config import reserve_url, reserve_port


class RequestReserve:
    def __init__(self):
        self.host = reserve_url
        self.port = reserve_port

    def get_all_jobs(self):
        url =
        r = requests.get(url)