import mysql.connector
import re
from src.Database.Adapters.BaseDatabaseAdapter import BaseDatabaseAdapter


class MySQLAdapter(BaseDatabaseAdapter):
    def __init__(self, settings: dict):
        super().__init__(settings)

    def _make_connection(self):
        """Создать и вернуть объект по работе с базой данных

        :return:
        """

        if not self.contains_settings_value('host') and not self.contains_settings_value('unix_socket'):
            raise Exception("[MySQLAdapter] Invalid database settings! Not found 'host' or "
                            "'unix_socket' in the database config!")
        if self.contains_settings_value('host') and self.contains_settings_value('unix_socket'):
            raise Exception("[MySQLAdapter] Use only 'host' or 'unix_socket' in the database config!")

        host = self.settings_value('host')
        port = self.settings_value('port', 3306)
        unix_socket = self.settings_value('unix_socket')
        user = self.settings_value('username')
        password = self.settings_value('password')
        database = self.database()

        pdo_dict = {}
        if host:
            pdo_dict['host'] = host
            pdo_dict['port'] = port
        elif unix_socket:
            pdo_dict['unix_socket'] = unix_socket
        if user:
            pdo_dict['user'] = user
        if password:
            pdo_dict['password'] = password
        if database and database != "":
            pdo_dict['database'] = database

        connect = mysql.connector.connect(**pdo_dict)
        connect.autocommit = False
        return connect

    def _make_cursor(self, connection):
        """Создать и вернуть курсор по работе с базой данных

        :param connection
        :return:
        """

        if not connection:
            return None
        return connection.cursor(buffered=True)

    def name(self) -> str:
        """Имя адаптера

        :rtype: str
        """

        return 'MySQL'

    def quote_table_name(self, name: str) -> str:
        """Получить корректное экранированное имя таблицы

        :param name: имя таблицы
        :type name: str
        :return: экранированное имя таблицы
        :rtype: str
        """

        # tmp_name = ""
        # name_list = name.split('.')
        # for v in name_list:
        #     if tmp_name == "":
        #         tmp_name = f"`{v}`"
        #     else:
        #         tmp_name += f".`{v}`"
        # return tmp_name
        return f"`{name}`"

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

    def server_version(self) -> str:
        """Метод запроса версии сервера базы данных

        :return: версия сервера базы данных
        :rtype: str
        """

        res = self.query("SHOW VARIABLES LIKE \"%version%\";")
        for r in res:
            if r['Variable_name'] != 'version':
                continue
            result = re.search(r'^(\d+\.)?(\d+\.)?(\*|\d+)', r['Value'])
            if result:
                return result.group(0)
            return r['Value']
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

        db_name = self.database()
        res = self.query(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{db_name}';")
        if len(res) != 0:
            tmp_list = []
            for k in res:
                tmp_list.append(k['table_name'])
            return tmp_list
        return []
