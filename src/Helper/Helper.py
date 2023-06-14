import os
import pwd


class Helper:
    @staticmethod
    def lookup(path: str, objects: dict = globals()):
        obj = None
        for element in path.split('.'):
            try:
                obj = objects[element]
            except KeyError:
                obj = getattr(objects, element)
        return obj

    @staticmethod
    def file_extension(path: str) -> str:
        """Получить расширение файла

        :param path: путь до файла
        :return:
        """

        split_tup = os.path.splitext(path)
        return split_tup[len(split_tup) - 1]

    @staticmethod
    def sort(data: dict, desc: bool = False) -> dict:
        """Метод сортировки массива

        :param data: массив с данными
        :type data: dict
        :param desc: использовать обратную сортировку
        :type desc: dict
        :return: отсортированный массив
        :rtype: dict
        """

        tmp_data = dict(data)
        keys = sorted(tmp_data.keys(), reverse=desc)
        sorted_hash = {}
        for k in keys:
            sorted_hash[k] = tmp_data[k]
        return sorted_hash

    @staticmethod
    def splice_symbol_first(string: str, symbol: str) -> str:
        """Обрезать символ вначале

        :param string: строка
        :param symbol: удаляемый символ
        :rtype: str

        print(splice_symbol_first("/tmp/app1/", "/"));
            => "tmp/app1/"
        """

        if string == "" or symbol == "":
            return string
        if len(symbol) > 1:
            symbol = symbol[0]
        if string[0] == symbol:
            if len(string) > 1:
                string = string[1:]
                string = Helper.splice_symbol_first(string, symbol)
            else:
                string = ""
        return string

    @staticmethod
    def splice_symbol_last(string: str, symbol: str) -> str:
        """Обрезать символ вконце

        :param string: строка
        :param symbol: удаляемый символ
        :rtype: str

        print(splice_symbol_last("/tmp/app1/", "/"));
            => "/tmp/app1"
        """

        if string == "" or symbol == "":
            return string
        if len(symbol) > 1:
            symbol = symbol[0]
        if string[len(string) - 1] == symbol:
            if len(string) > 1:
                string = string[0:len(string) - 1]
                string = Helper.splice_symbol_last(string, symbol)
            else:
                string = ""
        return string

    @staticmethod
    def to_underscore(string: str) -> str:
        under_string = ''
        for item in string:
            if item.isupper():
                if len(under_string) > 0:
                    under_string += "_"
                under_string += item.lower()
            else:
                under_string += item
        return under_string

    @staticmethod
    def to_camelcase(string: str) -> str:
        string = Helper.to_underscore(string)
        string = string.replace('-', ' ')
        string = string.replace('_', ' ')
        return ''.join(x for x in string.title() if not x.isspace())

    @staticmethod
    def current_user() -> str:
        return str(pwd.getpwuid(os.getuid())[0])
