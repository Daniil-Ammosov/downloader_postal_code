# coding: utf-8

import os
from math import pow

import requests
from requests.exceptions import MissingSchema

from .logger import get_logger, set_log_lvl
from .exceptions import ArchiveNotZip, NotCorrectStatusCode, UnhandledError

PATH_TO_SAVE = "/srv/downloader_postal_code/src/fias.zip"


class ArchiveDownloader(object):
    """
    Class for a downloading archive from FIAS
    """
    def __init__(self, url, settings, log_lvl="info"):
        self.name = "DOWNLOADER"
        self.logger = None

        self.session = None
        self.url = None
        self.timeout = None
        self.quantity_attempts = None

        self.content_length = None

        self.prepare(url, settings, log_lvl)

    def download_archive(self):
        """
        Main method
        """
        self.logger.info(u"Начало работы загрузчика")

        try:
            self.send_head_query()
            self.logger.info(u"Размер архива: {}GB".format(
                unicode(round(int(self.content_length) / pow(1024, 3), 2))))

            self.session.stream = True
            self.session.verify = False
            return self.download()

        except MissingSchema:
            self.logger.warning(u"Сервис ФИАС пока что не подготовил URL для скачивания архива\n"
                                u"Проверьте ответ с сервиса: '{url}'".format(url=self.url))
            return False

        finally:
            self.session.close()

    def prepare(self, url, settings, log_lvl="info"):
        """
        Set configuration
        """
        self.logger = get_logger(self.name)
        set_log_lvl(log_lvl, self.name)
        self.url = url
        self.timeout = settings["timeout"]
        self.quantity_attempts = settings["quantity_attempts"]
        self.session = requests.Session()

    def send_head_query(self):
        """
        Send HEAD query to FIAS and get archive size and name

        """
        request_headers = self.session.head(self.url).headers
        str_with_filename = request_headers.get('Content-Disposition', "; filename=.xyz;")

        for part in str_with_filename.split(";"):
            if part.startswith(" filename=") and part[-3:] != "zip":
                raise ArchiveNotZip(part[-3:])

        self.content_length = int(request_headers["Content-Length"])

    def attempt(self):
        """
        Attempt for download archive
        Send GET query and write file
        """
        response = self.session.get(
            url=self.url,
            timeout=30,
            headers={"Range": 'bytes={start}-'.format(start=os.path.getsize(PATH_TO_SAVE) if os.path.exists(PATH_TO_SAVE) else "0")}
        )
        if response.status_code not in (200, 206):
            raise NotCorrectStatusCode(response.status_code)

        f = open(PATH_TO_SAVE, "a")
        try:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)

        finally:
            f.close()

    def download(self):
        """
        Method for downloading archive to PC
        """
        if os.path.exists(PATH_TO_SAVE):
            os.remove(PATH_TO_SAVE)

        for attempt in range(self.quantity_attempts):
            self.logger.info(u"Попытка #{num}: Начало".format(num=attempt + 1))
            try:
                self.attempt()
                if os.path.exists(PATH_TO_SAVE) and os.path.getsize(PATH_TO_SAVE) == self.content_length:
                    self.logger.info(u"Попытка #{num}: Успех\nРазмер: {size}GB".format(
                        num=attempt + 1,
                        size=unicode(round(int(self.content_length) / pow(1024, 3), 2))
                    ))
                    return True

                else:
                    self.logger.info(u"Попытка #{num}: Неудача\nСкачано: {now}GB\nВсего: {all}GB".format(
                        num=attempt + 1,
                        now=unicode(round(int(os.path.getsize(PATH_TO_SAVE)) / pow(1024, 3), 2)) if os.path.exists(PATH_TO_SAVE) else u"0",
                        all=unicode(round(int(self.content_length) / pow(1024, 3), 2))))

            except IOError as e:
                if e.errno == 28:
                    self.logger.error(u"Свободное место закончилось. Добавьте памяти")
                    break

            except Exception as e:
                self.logger.exception(UnhandledError(e))

        return False
