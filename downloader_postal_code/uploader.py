# coding:utf-8

import os
import zipfile

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.exc import SQLAlchemyError

from .logger import get_logger, set_log_lvl
from .downloader import PATH_TO_SAVE as SOURCE_PATH
from .db import CONNECT_STR, DISABLE_INDEXES_QUERY, LOAD_DATA_QUERY, ENABLE_INDEXES_QUERY, DROP_TABLE_QUERY, RENAME_TABLE_QUERY
from downloader_postal_code.parsers import AddrParser, HouseParser
from .exceptions import NotZip, BaseDownloaderException, UnhandledError

PATH_TO_EXTRACT = "/srv/downloader_postal_code/tmp"

NAMES = ("as_addrobj", "as_house")

DICT_OF_HANDLING_INFO = {
    "as_addrobj": {
        "tablename": "addr_objects",
        "parser": AddrParser,
        "description": u"Файл с улицами / File with streets"
    },

    "as_house": {
        "tablename": "house_objects",
        "parser": HouseParser,
        "description": u"Файл с домами / File with houses"
    }
}


class UploaderXML(object):
    """
    Class for uploading ZIP archive to Mysql DB
    """
    def __init__(self, host=None, login=None, password=None, database=None, max_size=1, log_lvl="info"):
        self.name = "UPLOADER"
        self.logger = get_logger(self.name)
        set_log_lvl(log_lvl, self.name)

        self.db_engine = create_engine(CONNECT_STR.format(
            host=host,
            login=login,
            password=password,
            database=database
        ))
        self.connection = None
        self.zip_viewer = None
        self.size = max_size
        self.current_table = None

    def upload_archive(self):
        """
        Main method
        """
        try:
            self.check_zip()
            try:
                for file_in_archive in self.zip_viewer.filelist:
                    for important_xml in NAMES:
                        if file_in_archive.filename.startswith(important_xml.upper()):
                            self.handling_file(file_in_archive, important_xml)
            finally:
                if self.connection:
                    self.connection.close()

                self.zip_viewer.close()
                os.remove(SOURCE_PATH)

        except BaseDownloaderException as e:
            self.logger.exception(e)

        except Exception as e:
            self.logger.exception(UnhandledError(e))

    def handling_file(self, file_info, file_type):
        """
        Method for handling file in archive and upload it to db
        """
        csv_paths = self.convert_to_several_csv(file_info, file_type)
        self.update_table(csv_paths)

    def upload_csv(self, conn, tmp_table, csv_list):
        try:
            self.logger.info(u"Начало загрузки csv в бд\nВсего частей: {0}".format(len(csv_list)))
            conn.execute(DISABLE_INDEXES_QUERY.format(table=tmp_table))

            for part_num in range(len(csv_list)):
                part_path = csv_list[part_num]
                conn.execute(LOAD_DATA_QUERY.format(path_to_csv=part_path, table=tmp_table))
                os.remove(part_path)
                self.logger.info(u"Часть #{0}: Успех".format(unicode(part_num + 1)))

            conn.execute(ENABLE_INDEXES_QUERY.format(table=tmp_table))
            self.logger.info(u"Индексы включены")

            conn.execute(DROP_TABLE_QUERY.format(table=self.current_table))
            conn.execute(RENAME_TABLE_QUERY.format(tmp_table=tmp_table, table=self.current_table))
            self.logger.info(u"Временная таблица сделана основной")

        except SQLAlchemyError as e:
            self.logger.exception(UnhandledError(e))

    def convert_to_several_csv(self, file_object, object_type):
        """
        Method for a extracting XML file from archive and a splitting it to several parts
        """
        self.logger.info(u"Начало извлечения xml\nФайл: {}".format(file_object.filename))
        handling_info = DICT_OF_HANDLING_INFO[object_type]
        self.current_table = handling_info["tablename"]
        try:
            extracted_file = self.zip_viewer.extract(file_object, PATH_TO_EXTRACT)
            self.logger.info(u"XML файл извлечён. Начало деления на csv")
            parser = handling_info["parser"](PATH_TO_EXTRACT, self.size)
            csv_paths = parser.parse_file(extracted_file)
            self.logger.info(u'XML файл разделён на {} csv частей'.format(len(csv_paths)))

            return csv_paths

        except IOError:
            for filename in os.listdir(PATH_TO_EXTRACT):
                os.remove(os.path.join(PATH_TO_EXTRACT, filename))
            raise

        finally:
            filepath = os.path.join(PATH_TO_EXTRACT, file_object.filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                self.logger.info(u"XML файл удалён")

    def check_zip(self):
        self.logger.info(u"Проверка на ZIP")
        if not zipfile.is_zipfile(SOURCE_PATH):
            raise NotZip

        self.zip_viewer = zipfile.ZipFile(SOURCE_PATH)

    def update_table(self, csv_list):
        """
        Method for a uploading csv to table
        """
        with self.db_engine.begin() as connection:
            tmp = self.create_tmp_table()
            self.upload_csv(connection, tmp, csv_list)

    def create_tmp_table(self):
        """
        Method for a creating tmp table in db
        This table will be written new info
        """
        tmp_table_name = self.current_table + "_tmp"
        self.logger.info(u"Начало создания таблицы '{name}'".format(name=tmp_table_name))
        # Создаём временную таблицу на основании меты существующей
        meta = MetaData(bind=self.db_engine)
        table = Table(
            self.current_table,
            meta,
            autoload=True,
            autoload_with=self.db_engine,
            schema='postal_code')

        new_meta = MetaData(bind=self.db_engine)
        tmp_table = table.tometadata(new_meta)
        tmp_table.name = tmp_table_name

        # Дропаем временную таблицу, если такая существует
        if tmp_table.exists():
            tmp_table.drop()

        tmp_table.create()
        self.logger.info(u"Таблица '{name}' создана".format(name=tmp_table_name))
        return tmp_table_name
