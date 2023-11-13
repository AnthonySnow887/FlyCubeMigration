

class TCHelperFunction:
    __name = ""
    __callback = None

    def __init__(self, name: str, callback):
        """Консруктор класса вспомогательной функции

        :param name: название
        :param callback: функция обратного вызова
        """

        self.__name = name.strip()
        if self.__name == "":
            return
        self.__callback = callback

    def name(self) -> str:
        """ Название вспомогательной функции

        :return:
        """

        return self.__name

    def eval_function(self, args: list) -> str:
        """Метод вызова вспомогательной функции

        :param args: аргументы
        :return:
        """

        if self.__callback is None:
            raise Exception(f"[TCHelperFunction][eval_function] Invalid callback (None)! Function: '{self.__name}'")
        return str(self.__callback(*args))
