import os
import yaml
from src.Config.Config import Config
from src.Logger.ConsoleLogger import ConsoleLogger
from src.Helper.Helper import Helper
from src.Database.Adapters.BaseDatabaseAdapter import BaseDatabaseAdapter
from src.Database.Adapters.SQLiteAdapter import SQLiteAdapter
from src.Database.Adapters.PostgreSQLAdapter import PostgreSQLAdapter
from src.Database.Adapters.MySQLAdapter import MySQLAdapter


class DatabaseFactory:
    __instance = None
    __settings = {}
    __secondarySettings = {}
    __adapters = {}
    __databaseConfig = "database.yml"

    def __init__(self):
        # --- append default adapters - --
        self.__register_database_adapter('sqlite', 'SQLiteAdapter')
        self.__register_database_adapter('sqlite3', 'SQLiteAdapter')
        self.__register_database_adapter('postgresql', 'PostgreSQLAdapter')
        self.__register_database_adapter('mysql', 'MySQLAdapter')
        self.__register_database_adapter('mariadb', 'MySQLAdapter')

    @staticmethod
    def instance():
        """Получить инстанс класса

        :return: инстанс класса
        :rtype: DatabaseFactory
        """

        if not isinstance(DatabaseFactory.__instance, DatabaseFactory):
            DatabaseFactory.__instance = DatabaseFactory()
        return DatabaseFactory.__instance

    def load_config(self, path: str):
        """Загрузить настройки для работы с базой данных

        :param path: путь до каталога с конфигурационным файлом
        :type path: str
        """

        if len(self.__settings) != 0:
            return
        if not os.path.isdir(path):
            return  # TODO show error!
        config_file_path = f"{Helper.splice_symbol_last(path, '/')}/{self.__databaseConfig}"
        if not os.path.exists(config_file_path):
            return  # TODO show error!
        config_data = {}
        with open(config_file_path, "r") as stream:
            try:
                config_data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise exc

        # Load mode type
        db_mode = 'development'
        if Config.instance().is_production():
            db_mode = 'production'

        # Load primary settings
        self.__settings = self.__load_database_settings(db_mode, config_data, config_file_path)
        # Check supported adapters
        self.__check_supported_adapters(self.__settings, config_file_path)
        # Load secondary settings
        self.__secondarySettings = self.__load_database_settings(f"{db_mode}_secondary", config_data, config_file_path)
        # Check supported adapters
        for key, value in self.__secondarySettings.items():
            self.__check_supported_adapters(value, config_file_path)

    def reset_config(self):
        """Сбросить настройки конфигурации"""

        # Reset primary settings
        self.__settings = {}
        # Reset secondary settings
        self.__secondarySettings = {}

    def __load_database_settings(self, key: str, yaml_data: dict, path: str) -> dict:
        """Загрузить настройки по работе с БД

        :param key: ключ раздела настроек в YAML
        :type key: str
        :param yaml_data: данные файла конфигурации
        :type yaml_data: dict
        :param path: путь до файла конфигурации
        :type path: str
        :return: настройки по работе с БД
        :rtype: dict
        :raise: Exception
        """
        if not key in yaml_data:
            raise Exception(f"[DatabaseFactory][loadDatabaseSettings] Not found database {key} settings! Path: {path}")
        settings = yaml_data[key]
        if not settings:
            settings = {}
        return settings

    def create_database_adapter(self, args: dict = {'auto-connect': True}):
        """Создать адаптер по работе с базой данных

        :param args: Массив параметров создания адаптера
        :type args: dict
        :returns: Драйвер по работе с базой данных
        :rtype: BaseDatabaseAdapter|None

        ==== Args
         - [bool] auto-connect - connect automatically on creation (default: True)
         - [string] database   - database key name in '*_secondary' config (default: '')

        NOTE: If database name is empty - used primary database.
        """

        if len(self.__settings) == 0 and len(self.__secondarySettings):
            return None
        database = args.get('database', '')
        if not isinstance(database, str):
            return None
        if database == "":
            return self.__create_adapter(self.__settings, args)
        if database in self.__secondarySettings:
            return self.__create_adapter(self.__secondarySettings[database], args)
        return None

    def primary_adapter_name(self) -> str:
        """Имя основного (первичного) адаптера по работе с базой данных

        :returns: Имя адаптера
        :rtype: str
        """

        return self.__adapter_name(self.__settings)

    def secondary_adapter_name(self, database: str) -> str:
        """Имя вторичного адаптера по работе с базой данных

        :param database: Название базы данных
        :type database: str
        """

        if len(self.__secondarySettings) == 0 or database == "":
            return ""
        if not database in self.__secondarySettings:
            return ""
        return self.__adapter_name(self.__secondarySettings[database])

    def secondary_databases(self) -> list:
        """Список названий ключей к дополнительным базам данных из раздела конфигурации '*_secondary'

        :returns: Список названий ключей к дополнительным базам данных
        :rtype: list
        """

        return list(self.__secondarySettings.keys())

    def has_secondary_databases(self) -> bool:
        """Задан ли список дополнительных баз данных?

        :rtype: bool
        """

        return len(self.secondary_databases()) > 0

    def __register_database_adapter(self, name: str, class_name: str):
        """Зарегистрировать адаптер по работе с базой данных

        :param name: название адаптера, используемое в конфигурацинном файле для доступа к БД
        :type name: str
        :param class_name: имя класса адаптера (с namespace; наследник класса BaseDatabaseAdapter)
        :type class_name: str
        """

        name = name.strip()
        class_name = class_name.strip()
        if name == "" or class_name == "":
            return
        if name in self.__adapters:
            return
        self.__adapters[name] = class_name

    def __create_adapter(self, settings: dict, args: dict = {'auto-connect': True}):
        """Создать адаптер по работе с БД

        :param settings: настройки подключения
        :type settings: dict
        :param args: массив параметров создания адаптера
        :type args: dict
        :returns: Адаптер по работе с БД или None
        :rtype: BaseDatabaseAdapter|None
        """

        if len(settings) == 0:
            return None
        if not 'adapter' in settings:
            return None
        adapter_class_name = self.__select_adapter_class_name(settings['adapter'])
        if adapter_class_name == "":
            return None
        adapter_ = Helper.lookup(adapter_class_name, globals())
        adapter = adapter_(settings)
        auto_connect = args.get('auto-connect', True)
        if auto_connect:
            try:
                adapter.connect()
            except Exception as e:
                print(ConsoleLogger.instance().make_color_string(f"[DatabaseFactory][__create_adapter] Connect to database failed! Error: {e}", 'error'))
                return None
        return adapter

    def __check_supported_adapters(self, settings: dict, path: str):
        """Метод проверки поддерживаемых адаптеров по работе с БД

        :param settings: настройки по работе с БД
        :type settings: dict
        :param path: путь до файла конфигурации
        :type path: str
        :raise: Exception
        """

        if not 'adapter' in settings:
            raise Exception(f"[DatabaseFactory][checkSupportedAdapters] Not found database adapter! Path: {path}")
        tmp_adapter = settings['adapter']
        tmp_adapter_class_name = self.__select_adapter_class_name(tmp_adapter)
        if tmp_adapter_class_name == "":
            raise Exception(f"[DatabaseFactory][checkSupportedAdapters] Unsupported database adapter! Name: {tmp_adapter}; Path: {path}")

    def __select_adapter_class_name(self, name: str) -> str:
        """Запросить имя класса адаптера по работе с базой данных

        :param name: название адаптера
        :type name: str
        :returns: имя класса адартера
        :rtype: str
        """

        name = name.strip()
        if name in self.__adapters:
            return self.__adapters[name]
        return ""

    def __adapter_name(self, settings: dict) -> str:
        """Имя адаптера по работе с базой данных

        :param settings: настройки подключения
        :type settings: dict
        :returns: имя адаптера
        :rtype: str
        """

        if len(settings) == 0:
            return ""
        if not 'adapter' in settings:
            return ""
        return settings['adapter']

    # def __lookup(self, path: str):
    #     obj = globals()
    #     for element in path.split('.'):
    #         try:
    #             obj = obj[element]
    #         except KeyError:
    #             obj = getattr(obj, element)
    #     return obj
