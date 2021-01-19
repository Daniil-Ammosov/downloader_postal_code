# coding: utf-8

class BaseDownloaderException(Exception):
    def __init__(self, msg):
        super(BaseDownloaderException, self).__init__(msg)


class ArchiveNotZip(BaseDownloaderException):
    def __init__(self, str_type=None):
        message = u" или служба не отправляет заголовок 'Content-Disposition'" if not str_type else u": {0}".format(str_type)
        super(ArchiveNotZip, self).__init__(u"Архив не является ZIP{message}".format(message=message))


class NotZip(ArchiveNotZip):
    def __init__(self):
        super(BaseDownloaderException, NotZip).__init__(
            u"Скаченный файл не является архивом или некорректен"
        )


class NotCorrectStatusCode(BaseDownloaderException):
    def __init__(self, code):
        super(NotCorrectStatusCode, self).__init__(
            u"Неккоректный статус код: {code}".format(code=code)
        )


class UnhandledError(BaseDownloaderException):
    def __init__(self, exception):
        super(UnhandledError, self).__init__(
            u"Необработанная ошибка\n{error}".format(error=exception.message)
        )


class UnhandledRequestsError(BaseDownloaderException):
    def __init__(self, exception):
        super(UnhandledRequestsError, self).__init__(
            u"Необработанная ошибка от 'requests'\n{error}".format(error=exception.message)
        )
