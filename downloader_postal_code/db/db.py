# coding: utf-8

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from downloader_postal_code.db.models import Release

CONNECT_STR = "mysql://{login}:{password}@{host}/{database}?charset=utf8&use_unicode=1&local_infile=1"
CONNECT_STR_WITHOUT_DB = "mysql://{login}:{password}@{host}"


class DB(object):
    """
    Класс для работы с бд MySQL
    """

    def __init__(self, host=None, login=None, password=None, database=None):
        self.engine = create_engine(CONNECT_STR.format(
            host=host,
            login=login,
            password=password,
            database=database
        ))
        Session = sessionmaker(self.engine)
        self.session_ = Session()

    def get_version(self):
        """
        Метод для получения даты последнего релиза архива, установленного локально
        :return:
        """
        return self.session_.query(Release.version).scalar()

    def update_release_version(self, new_version):
        """
        Метод для обновления даты последнего релиза архива, установленного локально
        :param new_version:
        :return:
        """
        try:
            self.session_.query(
                Release
            ).filter_by(
                id=1
            ).update(
                {Release.version: new_version}
            )
            self.session_.commit()

        finally:
            self.session_.close()
