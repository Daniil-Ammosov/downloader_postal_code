# coding:utf-8

from xml.parsers.expat import ParserCreate
import os
from datetime import datetime


class BaseParser(object):
    """
    Базовый парсер и конвертатор xml в csv файлы
    """
    list_of_attr = ()
    main_tag_name = ""

    # Поля-расширения для записи в бд для более корректного поиска
    # Пример: extending = {"field_name_into_db": ("attr1", "attr2")} -> attr1 + attr2
    extending = {}

    def __init__(self, path_to_tmp_folder, max_gb_size):
        """
        Инициализирует инстанс парсера
        :param path_to_tmp_folder: Путь к директории, в которой будут создаваться CSV файлы
        :param max_gb_size: Максимальный размер в гигабайтах одного созданого CSV файла
        """
        self.parser = ParserCreate()
        self.parser.StartElementHandler = self.start_handler
        self.parser.EndElementHandler = self.end_handler
        self.parser.CharacterDataHandler = self.data_handler
        
        self.tmp_folder = path_to_tmp_folder
        self.max_output_file_size = max_gb_size * 1024 * 1024 * 1024
        self.current_line_num = 1
        self.output_files = []
        self.output_file = self.get_next_filepath()
        self.today = datetime.today().date()

    def parse_file(self, path_to_xml):
        """
        Основной метод парсера
        Парсит файл по введённому пути и конвертирует в CSV файлы
        :param path_to_xml: Абсолютный путь к XML файлу, который необходимо распарсить
        :return:
        type: list
        Возвращает список абсолютных путей к созданным CSV файлам
        """

        with open(path_to_xml) as f:
            self.parser.ParseFile(f)

        self.output_file.close()
        return self.output_files

    def start_handler(self, tag, attrs):
        """
        Метод парсера, отвечающий за отлов начала элементов и их атрибутов при парсинге
        Если имя тэга совпадает с основным тэгом парсера, производит обработку его атрибутов и записывает результат в CSV файл
        :param tag: Тэг, который пойман при парсинге
        :param attrs: Атрибуты пойманого тэга
        :return:
        """

        # Сверяем имя найденного тэга с именем основного тэга парсера
        if tag != self.main_tag_name or datetime.strptime(attrs[u"ENDDATE"], u"%Y-%m-%d").date() <= self.today:
            return

        # Создаём структуру для вставки в CSV файл
        data = [str(self.current_line_num)]

        # Добавляем в data основные поля для вставки
        for attrib_name in self.list_of_attr:
            data.append(attrs.get(attrib_name, ""))

        # Добавляем в data поля-расширения, к примеру, поле 'joined_num'
        if self.extending:
            for _, needs_attribs in self.extending.iteritems():
                value_for_insert = tuple(set([attrs.get(attrib_name, "") for attrib_name in needs_attribs]))
                data.append("".join(value_for_insert))

        # Проверка размера текущего файлового объекта типа CSV для записи резултатов парсинга на превыщение максимального размера
        # Если он оказывается больше, то создаём новый
        if os.path.getsize(self.output_file.name) >= self.max_output_file_size:
            self.output_file.close()
            self.output_file = self.get_next_filepath()

        self.output_file.write((";".join(data) + "\n").encode("utf-8"))
        self.current_line_num += 1

    def end_handler(self, name):
        pass

    def data_handler(self, data):
        pass

    def get_next_filepath(self):
        """
        Метод для получения следующего относительного пути к CSV файлу
        Возвращает открытый для записи объект типа file
        :return:
        """
        created_path_to_save_data = os.path.join(self.tmp_folder, "part_{}.csv".format(len(self.output_files)))
        self.output_files.append(created_path_to_save_data)
        return open(created_path_to_save_data, "wb")


class AddrParser(BaseParser):
    """
    Парсер для xml, начинающегося с "AS_ADDROBJ"
    """

    main_tag_name = "Object"
    list_of_attr = (
        "REGIONCODE", "AREACODE", "CITYCODE", "PLACECODE", "PLANCODE",
        "STREETCODE", "SHORTNAME", "OFFNAME", "OKATO", "OKTMO",
        "POSTALCODE", "AOLEVEL", "CODE", "AOGUID", "PARENTGUID"
    )

    def __init__(self, tmp_folder, max_size):
        super(AddrParser, self).__init__(tmp_folder, max_size)


class HouseParser(BaseParser):
    """
    Парсер для xml, начинающегося с "AS_HOUSE"
    """
    main_tag_name = "House"
    list_of_attr = (
        "AOGUID", "HOUSEGUID", "HOUSENUM", "BUILDNUM",
        "STRUCNUM", "POSTALCODE", "OKATO", "OKTMO"
    )
    extending = {"joined_num": ("HOUSENUM", "BUILDNUM", "STRUCNUM")}

    def __init__(self, tmp_folder, max_size):
        super(HouseParser, self).__init__(tmp_folder, max_size)
