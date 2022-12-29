import sys
from inspect import signature


class ConsoleHelper:
    __instance = None
    __primary_helpers = {}
    __helpers = {}
    __examples = []

    def __init__(self):
        self.append_helper(self.__show_help, {
            'command': '--help',
            'description': 'Show help',
            'alternatives': ['-h', '-?'],
            'primary': True
        })

    @staticmethod
    def instance():
        """Получить инстанс класса

        :return: инстанс класса
        :rtype: ConsoleHelper
        """

        if not isinstance(ConsoleHelper.__instance, ConsoleHelper):
            ConsoleHelper.__instance = ConsoleHelper()
        return ConsoleHelper.__instance

    @staticmethod
    def application_file() -> str:
        """Получить строку запуска приложения

        :rtype: str
        """

        return str(sys.argv[0])

    @staticmethod
    def application_argv() -> dict:
        """Получить массив входных параметров приложения в формате ключ-значение

        :rtype: dict
        """

        app_argv = list(sys.argv)
        app_argv.pop(0)  # remove app path
        argv = {}
        for a in app_argv:
            a_lst = a.split('=')
            key = a_lst[0].strip()
            value = None
            if key == "":
                continue
            if len(a_lst) > 1:
                a_lst.pop(0)
                separator = '='
                value = separator.join(a_lst).strip()
            argv[key] = value

        return argv

    @staticmethod
    def application_argv_value(key: str, default=None):
        """Получить значение входного параметра приложения по его ключу

        :param key: ключ
        :param default: базовое значение
        """

        return ConsoleHelper.application_argv().get(key, default)

    def append_helper(self, callback, args: dict):
        """Добавить обработчик команды

        :param callback: функция обратного вызова (NOTE: должна содержать 2 аргумента: команда, ее значение)
        :param args: массив параметров

        === args values ===
         - [str]  command      команда
         - [str]  param        параметры команды (только для вывода в консоль и все) (default: '')
         - [str]  description  описание (default: '')
         - [list] alternatives альтернативные значения команды (default: [])
         - [bool] has_exit     требуется ли завершить приложение после выполнения команды (default: True)
         - [bool] primary      является ли первичный обработчиком (default: False)
         - [str]  group        название группы, в которую входит (для группировки при отображении help) (default: '')
        """

        if len(args) == 0:
            return
        command = args.get('command', "").strip()
        command_param = args.get('param', None)
        command_description = args.get('description', "").strip()
        command_alternatives = args.get('alternatives', [])
        has_exit = bool(args.get('has_exit', True))
        is_primary = bool(args.get('primary', False))
        command_group = args.get('group', "").strip()
        # check command
        if command == "":
            return
        # get dict
        dict = self.__helpers
        if is_primary:
            dict = self.__primary_helpers
        # check is already added
        if command in dict:
            return
        # add
        dict[command] = {
            'param': command_param,
            'description': command_description,
            'has_exit': has_exit,
            'callback': callback,
            'alternatives': command_alternatives,
            'is_alternative': False,
            'group': command_group
        }
        # add alternatives
        for v in command_alternatives:
            v = str(v).strip()
            if len(v) == 0:
                continue
            dict[v] = {
                'param': command_param,
                'description': command_description,
                'has_exit': has_exit,
                'callback': callback,
                'alternatives': [],
                'is_alternative': True,
                'group': command_group
            }

    def append_example(self, title: str, code: str):
        """Добавить пример

        :param title: Название
        :param code: Код
        """

        if title == "" or code == "":
            return
        self.__examples.append({
            'title': title,
            'code': code
        })

    def process_command(self):
        """Метод обработки команд"""

        argv = self.application_argv()
        if len(argv) == 0:
            print(f"ERROR: Invalid arguments! Use --help!")
            return
        # check primary commands
        processed_cmd = []
        for k, v in argv.items():
            if not k in self.__primary_helpers:
                continue
            processed_cmd.append(k)
            has_exit = self.__primary_helpers[k]['has_exit']
            callback = self.__primary_helpers[k]['callback']
            # check callback
            if not callback:
                continue
            # run callback
            self.__process_callback(callback, k, v)
            # check if exit
            if has_exit:
                return
        # remove processed command
        for k in processed_cmd:
            del argv[k]

        # check commands
        for k, v in argv.items():
            if not k in self.__helpers:
                print(f"ERROR: Undefined command '{k}'! Use --help!")
                return
            has_exit = self.__helpers[k]['has_exit']
            callback = self.__helpers[k]['callback']
            # check callback
            if not callback:
                continue
            # run callback
            self.__process_callback(callback, k, v)
            # check if exit
            if has_exit:
                return

    def __process_callback(self, callback, cmd: str, cmd_value):
        """Метод вызова callback функции

        :param callback: callback функция
        :param cmd: команда
        :param cmd_value: значение команды
        """

        sig = signature(callback)
        callback_param_len = len(sig.parameters)
        if callback_param_len == 0:
            callback()
        elif callback_param_len == 1:
            callback(cmd)
        elif callback_param_len == 2:
            callback(cmd, cmd_value)
        else:
            args_lst = [cmd, cmd_value]
            for i in range(0, callback_param_len - 2):
                args_lst.append(None)
            tuple_args_lst = tuple(args_lst)
            callback(*tuple_args_lst)

    def __show_help(self):
        """Метод вывода справки"""

        print("")
        print(f"Usage: {self.application_file()} [options]")
        print("")
        print("Options include:")
        print("")
        max_cmd_with = self.__max_cmd_with()
        primary_helper_groups = self.__group_cmd(dict(self.__primary_helpers))
        helper_groups = self.__group_cmd(dict(self.__helpers))
        for group in primary_helper_groups.values():
            if len(group) == 0:
                continue
            self.__show_group_help(group, max_cmd_with)
            print("")

        if len(helper_groups.keys()) > 0:
            print("")
        for group in helper_groups.values():
            if len(group) == 0:
                continue
            self.__show_group_help(group, max_cmd_with)
            print("")
        print("")

        if len(self.__examples) > 0:
            self.__show_examples()

    def __show_group_help(self, group: dict, max_cmd_with: int):
        for k, v in group.items():
            if v['is_alternative']:
                continue
            cmd_param = v['param']
            cmd_description = v['description']
            splitter = ", "
            cmd_alternatives = splitter.join(v['alternatives']).strip()
            if not cmd_alternatives == "":
                cmd_alternatives = f"[{cmd_alternatives}]"
            cmd = k
            if cmd_param:
                cmd = f"{k}={cmd_param}"
            repeat_num = max_cmd_with - len(cmd)
            print(f"  {self.__str_append_repeat(cmd, ' ', repeat_num)}   {cmd_description} {cmd_alternatives}")

    def __show_examples(self):
        max_with = len(f"{len(self.__examples)}")
        index = 1
        print("Examples:")
        print("")
        for e in self.__examples:
            index_str = f"{index}"
            repeat_num = max_with - len(index_str)
            print(f"{self.__str_append_repeat(index_str, ' ', repeat_num, False)}. {e['title']}:")
            print(f"{self.__str_append_repeat(' ', ' ', max_with + 2, False)}{e['code']}")
            print("")
            index += 1
        print("")

    def __str_append_repeat(self, string: str, repeat_str: str, repeat_num: int, after: bool = True) -> str:
        if after:
            return f"{string}{self.__str_repeat(repeat_str, repeat_num)}"
        return f"{self.__str_repeat(repeat_str, repeat_num)}{string}"

    def __str_repeat(self, repeat_str: str, repeat_num: int) -> str:
        if repeat_num <= 0:
            return ''
        return repeat_str * repeat_num

    def __group_cmd(self, data: dict) -> dict:
        groups = {}
        for k, v in data.items():
            cmd_group = v['group']
            if not cmd_group in groups:
                groups[cmd_group] = {}
            groups[cmd_group][k] = v
        return groups

    def __max_cmd_with(self) -> int:
        max = 0
        for k, v in self.__primary_helpers.items():
            cmd = k
            cmd_param = v['param']
            if cmd_param:
                cmd = f"{k}={cmd_param}"
            cmd_len = len(cmd)
            if max < cmd_len:
                max = cmd_len
        for k, v in self.__helpers.items():
            cmd = k
            cmd_param = v['param']
            if cmd_param:
                cmd = f"{k}={cmd_param}"
            cmd_len = len(cmd)
            if max < cmd_len:
                max = cmd_len
        return max
