import re
import json
from src.TemplateCompiler.TCHelperFunction import TCHelperFunction


class TemplateCompiler:
    __helpers = {}
    __params = {}

    def append_help_function(self, func: TCHelperFunction):
        """Добавить вспомогательную функцию

        :param func: Объект класса вспомогательной функции
        :return:
        """

        if len(func.name()) == 0:
            raise Exception("[TemplateCompiler][append_help_function] Helper function name is Empty!")
        if func.name() in self.__helpers:
            raise Exception(
                f"[TemplateCompiler][append_help_function] Helper function already added (name: \"{func.name()}\")!")
        self.__helpers[func.name()] = func

    def append_help_param(self, key: str, value):
        """Добавить вспомогательный параметр

        :param key: Ключ (название) параметра
        :param value: Значение параметра
        :return:
        """

        if len(key) == 0:
            raise Exception("[TemplateCompiler][append_help_param] Help param key is Empty!")
        if key in self.__params:
            raise Exception(f"[TemplateCompiler][append_help_param] Help param already added (key: \"{key}\")!")
        self.__params[key] = value

    def compile(self, data: str) -> str:
        """Собрать данные, проверяя вхождение вспомогательных функций и параметров

        :param data: Данные для разбора
        :return:
        """

        tmp_data = ""
        line_num = 1
        lines = re.split("[\r\n]", data)
        for line in lines:
            tmp_data += self.__compile_line(line, line_num) + "\r\n"
            line_num += 1
        return tmp_data

    def __compile_line(self, data: str, line_num: int) -> str:
        """Собрать данные одной строки, проверяя вхождение вспомогательных функций и параметров

        :param data: Строка для рабора
        :param line_num: Номер строки
        :return:
        """

        if len(data) == 0:
            return data
        # check functions
        tmp_data = self.__parse_help_functions(data, line_num)
        if len(tmp_data) > 0:
            return tmp_data
        # check params
        tmp_data = self.__parse_help_params(data, line_num)
        if len(tmp_data) > 0:
            return tmp_data
        # no change
        return data

    def __parse_help_functions(self, data: str, line_num: int) -> str:
        """Разбор строки со вспомогательными функциями

        :param data: Строка для рабора
        :param line_num: Номер строки
        :return:

        === Example
            ![This is Lu and Bryu!]( {{ image_path ('configure.svg') }} "Lu and Bryu")
        """

        matches = re.findall('(\{([\{\#])\s*([\w]+)\s*\(\s*([A-Za-z0-9_\ \-\,\.\'\"\{\}\[\]\:\/]*)\s*\)\s*([\}\#])\})',
                             data)
        if len(matches) == 0:
            return ""
        is_changed = False
        for match in matches:
            if len(match) < 5:
                continue
            replace_str = match[0]
            tag_open = match[1]
            help_func = match[2]
            help_func_args = self.__parse_help_function_args(match[3])
            tag_close = match[4]
            # check
            if tag_open == '{' and tag_close != '}':
                raise Exception("[TemplateCompiler][__parse_help_functions] Invalid closed symbol (not '}') in line "
                                + str(line_num) + "!")
            elif tag_open == '#' and tag_close != '#':
                raise Exception("[TemplateCompiler][__parse_help_functions] Invalid closed symbol (not '#') in line "
                                + str(line_num) + "!")
            elif not self.__has_supported_help_function(help_func):
                raise Exception(f"[TemplateCompiler][__parse_help_functions] Unsupported help function (name: '{help_func}') in line {line_num}!")

            # skip help func
            if tag_open == '#':
                replace_value = ""
            else:
                # eval help func
                replace_value = self.__eval_help_function(help_func, help_func_args)

            data = data.replace(replace_str, replace_value)
            is_changed = True

        if is_changed:
            return data
        return ""

    def __parse_help_params(self, data: str, line_num: int) -> str:
        """Разбор строки со вспомогательными параметрами

        :param data: Строка для разбора
        :param line_num: Номер строки
        :return:

        === Example
            Key: {{ my_key }}
        """

        matches = re.findall('(\{([\{\#])\s{0,}([\w]+)\s{0,}([\}\#])\})', data)
        if len(matches) == 0:
            return ""
        is_changed = False
        for match in matches:
            if len(match) < 4:
                continue
            replace_str = match[0]
            tag_open = match[1]
            help_param = match[2]
            tag_close = match[3]
            # check
            if tag_open == '{' and tag_close != '}':
                raise Exception("[TemplateCompiler][__parse_help_params] Invalid closed symbol (not '}') in line "
                                + str(line_num) + "!")
            elif tag_open == '#' and tag_close != '#':
                raise Exception("[TemplateCompiler][__parse_help_params] Invalid closed symbol (not '#') in line "
                                + str(line_num) + "!")
            elif not self.__has_supported_help_param(help_param):
                raise Exception(f"[TemplateCompiler][__parse_help_params] Unsupported help parameter (name: '{help_param}') in line {line_num}!")

            # skip help func
            if tag_open == '#':
                replace_value = ""
            else:
                # eval help func
                replace_value = self.__help_param(help_param)

            data = data.replace(replace_str, replace_value)
            is_changed = True

        if is_changed:
            return data
        return ""

    def __parse_help_function_args(self, args: str, delimiter: str = ',') -> list:
        """Метод разбора аргументов функции

        :param args:
        :param delimiter:
        :return:
        """

        args = args.strip()
        if len(args) == 0:
            return []
        tmp_args = []
        current_arg = ""
        quote = False
        dbl_quote = False
        is_array = False
        is_hash = False
        prev_char = None
        i = 0
        for char in args:
            if i > 0:
                prev_char = char
            # check quotes
            if char == "'" and dbl_quote == False and (prev_char is None or prev_char != "\\"):
                quote = not quote
            elif char == "\"" and quote == False and (prev_char is None or prev_char != "\\"):
                dbl_quote = not dbl_quote
            # check array
            elif char == "[" and is_array == False and (prev_char is None or prev_char != "\\"):
                is_array = True
            elif char == "]" and is_array == True and (prev_char is None or prev_char != "\\"):
                is_array = False
            # check hash
            elif char == "{" and is_hash == False and (prev_char is None or prev_char != "\\"):
                is_hash = True
            elif char == "}" and is_hash == True and (prev_char is None or prev_char != "\\"):
                is_hash = False

            # check delimiter
            if char == delimiter and quote == False and dbl_quote == False and is_array == False and is_hash == False:
                tmp_args.append(self.__prepare_function_arg(current_arg))
                current_arg = ""
                i += 1
                continue
            current_arg += char
            i += 1
        tmp_args.append(self.__prepare_function_arg(current_arg))
        return tmp_args

    def __prepare_function_arg(self, arg: str):
        """Метод преобразования значения аргумента функции

        :param arg:
        :return:
        """

        arg = arg.strip()
        if len(arg) == 0:
            return None
        # is string
        r = re.findall('^[\'\"]{1,1}(.*)[\'\"]{1,1}$', arg)
        if len(r) > 0:
            return str(r[0])
        # is int
        r = re.findall('^([+-]?[0-9]*)$', arg)
        if len(r) > 0:
            return int(r[0])
        # is float
        r = re.findall('^([+-]?[0-9]*[.]?[0-9]+)$', arg)
        if len(r) > 0:
            return float(r[0])
        # is hash
        r = re.findall('^\{(.*)\}$', arg)
        if len(r) > 0:
            return json.loads(arg)
        # is array
        r = re.findall('^\[(.*)\]$', arg)
        if len(r) > 0:
            return json.loads(arg)
        return None

    def __has_supported_help_function(self, func_name: str) -> bool:
        """Проверить наличие требуемой вспомогательной функции

        :param func_name:
        :return:
        """

        return func_name in self.__helpers

    def __has_supported_help_param(self, param_name: str) -> bool:
        """Проверить наличие требуемого вспомогательного параметра

        :param param_name:
        :return:
        """

        return param_name in self.__params

    def __eval_help_function(self, func_name: str, args: list) -> str:
        """Выполнить требуемую вспомогательную функцию

        :param func_name:
        :param args:
        :return:
        """

        if not self.__has_supported_help_function(func_name):
            raise Exception(f"[TemplateCompiler][__eval_help_function] Unsupported help function (name: '{func_name}')!")
        return self.__helpers[func_name].eval_function(args)

    def __help_param(self, param_name: str) -> str:
        """Получить значение параметра

        :param param_name:
        :return:
        """

        if not self.__has_supported_help_param(param_name):
            raise Exception(f"[TemplateCompiler][__help_param] Unsupported help parameter (name: '{param_name}')!")
        return str(self.__params[param_name])
