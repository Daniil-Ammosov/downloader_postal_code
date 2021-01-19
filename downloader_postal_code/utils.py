# coding: utf-8

import json

CONFIG_FILE = "/etc/downloader_postal_code/downloader_postal_code.json"


def read_config():
    with open(CONFIG_FILE) as config:
        return json.load(config)
