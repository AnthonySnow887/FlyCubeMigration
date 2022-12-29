import psycopg2
import psycopg2.extras
import psycopg2.extensions
from src.Database.Adapters.BaseDatabaseAdapter import BaseDatabaseAdapter


class PostgreSQLAdapter(BaseDatabaseAdapter):
    def __init__(self, settings: dict):
        super().__init__(settings)

    def _make_connection(self):
        """Создать и вернуть объект по работе с базой данных

        :return:
        """

        if not self.contains_settings_value('host') and not self.contains_settings_value('unix_socket_dir'):
            raise Exception("[PostgreSQLAdapter] Invalid database settings! Not found 'host' or "
                            "'unix_socket_dir' in the database config!")
        if self.contains_settings_value('host') and self.contains_settings_value('unix_socket_dir'):
            raise Exception("[PostgreSQLAdapter] Use only 'host' or 'unix_socket_dir' in the database config!")

        host = self.settings_value('host')
        port = self.settings_value('port', 5432)
        unix_socket_dir = self.settings_value('unix_socket_dir')
        user = self.settings_value('username')
        password = self.settings_value('password')
        database = self.database()

        pdo_str = ""
        if host:
            pdo_str = f"host={host} port={port}"
        elif unix_socket_dir:
            pdo_str = f"host={unix_socket_dir}"
        if user:
            pdo_str += f" user={user}"
        if password:
            pdo_str += f" password={password}"
        if database and database != "":
            pdo_str += f" dbname={database}"

        connect = psycopg2.connect(pdo_str)
        # connect.set_session(autocommit=False)

        # get the isolation leve for autocommit
        autocommit = psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT

        # set the isolation level for the connection's cursors
        # will raise ActiveSqlTransaction exception otherwise
        connect.set_isolation_level(autocommit)
        connect.autocommit = False
        return connect

    def name(self) -> str:
        """Имя адаптера

        :rtype: str
        """

        return 'PostgreSQL'

    def quote_table_name(self, name: str) -> str:
        """Получить корректное экранированное имя таблицы

        :param name: имя таблицы
        :type name: str
        :return: экранированное имя таблицы
        :rtype: str
        """

        tmp_name = ""
        name_list = name.split('.')
        for v in name_list:
            if tmp_name == "":
                tmp_name = f"\"{v}\""
            else:
                tmp_name += f".\"{v}\""
        return tmp_name

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
                row_dict[col.name] = row[i]
            results.append(row_dict)

        return results

    def server_version(self) -> str:
        """Метод запроса версии сервера базы данных

        :return: версия сервера базы данных
        :rtype: str
        """

        res = self.query("SHOW server_version;")
        if len(res) != 0:
            return res[0]['server_version']
        return ""

    def extensions(self) -> list:
        """Метод запроса списка расширений базы данных

        :return: список расширений базы данных
        :rtype: list

        NOTE: SQLite not supported extensions.
        """

        res = self.query("SELECT * FROM pg_extension;")
        if len(res) != 0:
            tmp_list = []
            for k in res:
                tmp_name = k['extname']
                if tmp_name == 'plpgsql':
                    continue
                tmp_list.append(tmp_name)
            return tmp_list
        return []

    def tables(self) -> list:
        """Метод запроса списка таблиц базы данных

        :return: список таблиц базы данных
        :rtype: list
        """

        res = self.query(
            "select * from information_schema.tables where table_schema != 'pg_catalog' and table_schema != 'information_schema' and table_type != 'VIEW';")
        if len(res) != 0:
            tmp_list = []
            for k in res:
                tmp_list.append(f"{k['table_schema']}.{k['table_name']}")
            return tmp_list
        return []
