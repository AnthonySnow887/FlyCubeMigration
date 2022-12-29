class ConsoleLogger:
    __instance = None
    __show_out = False
    __debug = ""
    __info = "\033[94m"
    __info_2 = "\033[1;96m"
    __success = "\033[32m"
    __warning = "\033[1;33m"
    __error = "\033[1;31m"
    __fatal = "\033[1;41m"
    __end = "\033[0m"

    @staticmethod
    def instance():
        """Получить инстанс класса

        :return: инстанс класса
        :rtype: ConsoleLogger
        """

        if not isinstance(ConsoleLogger.__instance, ConsoleLogger):
            ConsoleLogger.__instance = ConsoleLogger()
        return ConsoleLogger.__instance

    def show_out(self) -> bool:
        return self.__show_out

    def set_show_out(self, show: bool):
        self.__show_out = show

    def debug(self, string: str):
        self.__output(string, 'debug')

    def info(self, string: str):
        self.__output(string, 'info')

    def warning(self, string: str):
        self.__output(string, 'warning')

    def error(self, string: str):
        self.__output(string, 'error')

    def fatal(self, string: str):
        self.__output(string, 'fatal')

    def make_color_string(self, string: str, text_type: str) -> str:
        if text_type.strip().lower() == 'debug':
            return string
        elif text_type.strip().lower() == 'info':
            return f"{self.__info}{string}{self.__end}"
        elif text_type.strip().lower() == 'info-2':
            return f"{self.__info_2}{string}{self.__end}"
        elif text_type.strip().lower() == 'ok':
            return f"{self.__success}{string}{self.__end}"
        elif text_type.strip().lower() == 'success':
            return f"{self.__success}{string}{self.__end}"
        elif text_type.strip().lower() == 'warning':
            return f"{self.__warning}{string}{self.__end}"
        elif text_type.strip().lower() == 'error':
            return f"{self.__error}{string}{self.__end}"
        elif text_type.strip().lower() == 'fatal':
            return f"{self.__fatal}{string}{self.__end}"
        return string

    def __output(self, string: str, text_type: str):
        if not self.__show_out:
            return
        string = self.make_color_string(string, text_type)
        print(string)
