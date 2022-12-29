import sqlite3
from src.Database.Adapters.BaseDatabaseAdapter import BaseDatabaseAdapter


class SQLiteAdapter(BaseDatabaseAdapter):
    def __init__(self, settings: dict):
        super().__init__(settings)

    def _make_connection(self):
        """Создать и вернуть объект по работе с базой данных

        :return:
        """

        connection = sqlite3.connect(self.database())
        return connection

    def name(self) -> str:
        """Имя адаптера

        :rtype: str
        """

        return 'SQLite'

    def quote_table_name(self, name: str) -> str:
        """Получить корректное экранированное имя таблицы

        :param name: имя таблицы
        :type name: str
        :return: экранированное имя таблицы
        :rtype: str
        """

        return f"\"{name}\""

    def server_version(self) -> str:
        """Метод запроса версии сервера базы данных

        :return: версия сервера базы данных
        :rtype: str
        """

        res = self.query("select sqlite_version() as version;")
        if len(res) != 0:
            return res[0]['version']
        return ""

    def extensions(self) -> list:
        """Метод запроса списка расширений базы данных

        :return: список расширений базы данных
        :rtype: list

        NOTE: SQLite not supported extensions.
        """

        return []

    def tables(self) -> list:
        """Метод запроса списка таблиц базы данных

        :return: список таблиц базы данных
        :rtype: list
        """

        res = self.query("SELECT tbl_name FROM sqlite_master WHERE type = 'table';")
        if len(res) != 0:
            tmp_list = []
            for k in res:
                if 'tbl_name' in k:
                    tmp_list.append(k['tbl_name'])
            return tmp_list
        return []

    def prepare_result_data(self, columns: list, result):
        """Преобразовать данные в словать

        :param columns: названия колонок таблицы
        :param result: результат запроса
        :return: преобразованный словарь
        """

        results = []
        for row in result:
            row_dict = {}
            for i, col in enumerate(columns):
                row_dict[col[0]] = row[i]
            results.append(row_dict)

        return results
