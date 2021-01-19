# coding:utf-8

import requests
import requests.packages.urllib3 as urllib3
from requests.exceptions import RequestException


from .downloader import ArchiveDownloader
from .uploader import UploaderXML
from .db import DB
from .utils import read_config
from .logger import get_logger, set_log_lvl
from .exceptions import UnhandledError, UnhandledRequestsError


class CoreDownloader(object):
    """
    Core of this project
    """

    def __init__(self):
        self.name = "CORE"

        self.config = None
        self.logger = None

        self.downloader = None
        self.uploader = None
        self.db = None

        self.new_version = None

    def run(self):
        """
        Main method
        """
        self.logger = get_logger(self.name)
        try:
            self.prepare()
            download_settings = self.config["download"]
            url = self.get_url(download_settings)

            if self.new_version:
                self.logger.info(u"Начало загрузки архива")
                self.downloader = ArchiveDownloader(url, download_settings, self.config["log_lvl"])
                success = self.downloader.download_archive()

                if success:
                    self.logger.info(u'Начало обновления бд')
                    self.uploader = UploaderXML(max_size=self.config["max_part_size"],
                                                log_lvl=self.config["log_lvl"],
                                                **self.config["mysql"])
                    self.uploader.upload_archive()
                    self.db.update_release_version(self.new_version)

        except RequestException as e:
            self.logger.exception(UnhandledRequestsError(e))

        except Exception as e:
            self.logger.exception(UnhandledError(e))

    def prepare(self):
        """
        Set configuration for a correct job
        """
        self.config = read_config()
        set_log_lvl(self.config["log_lvl"], self.name)
        self.db = DB(**self.config["mysql"])
        urllib3.disable_warnings()

    def get_url(self, settings):
        """
        Send GET query ti FIAS and get info about current release
        """
        new_info = requests.get(settings["url"]).json()
        if self.db.get_version() < new_info["VersionId"]:
            self.logger.info(u"Найдена новая версия")
            self.new_version = int(new_info["VersionId"])

            return new_info[settings["method"]]
