from abc import ABCMeta, abstractmethod, abstractproperty
from src.Logger.ConsoleLogger import ConsoleLogger


class BaseDatabaseAdapter:
    __metaclass__ = ABCMeta
    __settings = {}
    __connection = None
    __cursor = None

    def __init__(self, settings: dict):
        self.__settings = settings

    def __del__(self):
        self.disconnect()

    @abstractmethod
    def _make_connection(self):
        """Создать и вернуть объект по работе с базой данных

        :return:
        """

    def _make_cursor(self, connection):
        """Создать и вернуть курсор по работе с базой данных

        :param connection
        :return:
        """

        if not connection:
            return None
        return connection.cursor()

    @abstractmethod
    def name(self) -> str:
        """Имя адаптера

        :rtype: str
        """

    @abstractmethod
    def quote_table_name(self, name: str) -> str:
        """Получить корректное экранированное имя таблицы

        :param name: имя таблицы
        :type name: str
        :return: экранированное имя таблицы
        :rtype: str
        """

    @abstractmethod
    def server_version(self) -> str:
        """Метод запроса версии сервера базы данных

        :return: версия сервера базы данных
        :rtype: str
        """

    @abstractmethod
    def extensions(self) -> list:
        """Метод запроса списка расширений базы данных

        :return: список расширений базы данных
        :rtype: list
        """

    @abstractmethod
    def tables(self) -> list:
        """Метод запроса списка таблиц базы данных

        :return: список таблиц базы данных
        :rtype: list
        """

    def prepare_result_data(self, columns: list, result):
        """Преобразовать данные в словать

        :param columns: названия колонок таблицы
        :param result: результат запроса
        :return: преобразованный словарь
        """

        return result

    def connect(self) -> bool:
        """Подключиться к базе данных

        :return: результат подключения
        :rtype: bool
        """

        if not self.__connection:
            self.__connection = self._make_connection()
        if self.__connection:
            return True
        return False

    def disconnect(self) -> bool:
        """Отключиться от базы данных

        :return: результат отключения
        :rtype: bool
        """

        if self.__cursor:
            self.__cursor.close()
            self.__cursor = None
        if self.__connection:
            self.__connection.close()
            self.__connection = None
        return True

    def is_connected(self) -> bool:
        """Подключен ли адаптер к базе данных

        :rtype: bool
        """

        if self.__connection:
            return True
        return False

    def query(self, sql: str) -> list:
        """Выполнить запрос к базе данных

        :param sql: SQL запрос
        :type sql: str
        :return: Результат запроса
        :rtype: list
        """

        if not self.is_connected():
            raise Exception(f"Database adapter is not connected! Exec query failed! SQL: {sql}")
        in_transaction = self.in_transaction()
        if not self.__cursor:
            self.__cursor = self._make_cursor(self.__connection)  # self.__connection.cursor()
        ConsoleLogger.instance().debug(f"[SQL] {sql}")
        self.__cursor.execute(sql)
        if not in_transaction:
            self.__connection.commit()

        result = []
        cursor_description = self.__cursor.description
        if cursor_description:
            columns = list(cursor_description)
            result = self.__cursor.fetchall()
            result = self.prepare_result_data(columns, result)

        if not in_transaction:
            self.__cursor.close()
            self.__cursor = None
        return result

    def begin_transaction(self) -> bool:
        """Открыть транзакцию

        :rtype: bool
        """

        if not self.is_connected():
            raise Exception("Database adapter is not connected! Begin transaction failed!")
        if self.in_transaction():
            return True
        self.__cursor = self.__connection.cursor()
        if self.__cursor:
            return True
        return False

    def commit_transaction(self) -> bool:
        """Применить транзакцию

        :rtype: bool
        """

        if not self.is_connected():
            raise Exception("Database adapter is not connected! Commit transaction failed!")
        if not self.in_transaction():
            return False
        self.__connection.commit()
        self.__cursor.close()
        self.__cursor = None
        return True

    def rollback_transaction(self) -> bool:
        """Отменить транзакцию

        :rtype: bool
        """

        if not self.is_connected():
            raise Exception("Database adapter is not connected! Rollback transaction failed!")
        if not self.in_transaction():
            return False
        self.__connection.rollback()
        self.__cursor.close()
        self.__cursor = None
        return True

    def in_transaction(self) -> bool:
        """Открыта ли транзакция

        :rtype: bool
        """

        if self.__cursor:
            return True
        return False

    def settings(self) -> dict:
        """Получить массив с настройками

        :return: массив с настройками
        :rtype: dict
        """

        return dict(self.__settings)

    def contains_settings_value(self, key: str) -> bool:
        """Содержится ли значение настроек с требуемым ключом

        :param key: ключ
        :type key: str
        :rtype: bool
        """

        if key in self.__settings:
            return True
        return False

    def settings_value(self, key: str, default=None):
        """Получить значение настроек по ключу

        :param key: ключ
        :type key: str
        :param default: базовое значение
        :type default: Any
        :return: значение ключа настроек
        :rtype: Any
        """

        if key in self.__settings:
            return self.__settings[key]
        return default

    def set_settings(self, data: dict):
        """Задать новые настройки

        :param data: массив с настройками
        :type data: dict
        """

        self.__settings = data

    def database(self) -> str:
        """Получить имя текущей базы данных из настроек

        :return: имя текущей базы данных из настроек
        :rtype: str
        """

        if 'database' in self.__settings:
            return self.__settings['database']
        return ""
