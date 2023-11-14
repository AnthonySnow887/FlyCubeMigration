import os
import yaml
from src.Helper.Helper import Helper


class Config:
    __instance = None
    __args = {}
    __env = "env"
    __config_file = "fly-cube-migration.yml"
    __config_file_path = ""

    TAG_CONFIG_DIR = "FLY_CUBE_MIGRATION_CONFIG_DIR"
    TAG_DB_MIGRATIONS_DIR = "FLY_CUBE_MIGRATION_DB_MIGRATIONS_DIR"

    @staticmethod
    def instance():
        """Получить инстанс класса

        :return: инстанс класса
        :rtype: Config
        """

        if not isinstance(Config.__instance, Config):
            Config.__instance = Config()
        return Config.__instance

    def load_config(self, path: str):
        """Загрузить настройки для работы

        :param path: путь до каталога с конфигурационным файлом
        :type path: str
        """

        if len(self.__args) != 0:
            return
        if not os.path.isdir(path):
            raise Exception(f"[Config][load_config] Invalid config directory (is not directory)! Path: {path}")
        self.__config_file_path = f"{Helper.splice_symbol_last(path, '/')}/{self.__config_file}"
        if not os.path.exists(self.__config_file_path):
            raise Exception(f"[Config][load_config] Not found config file! Path: {self.__config_file_path}")
        with open(self.__config_file_path, "r") as stream:
            try:
                self.__args = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise exc

    def reset_config(self):
        """Сбросить настройки конфигурации"""

        self.__args = {}
        self.__config_file_path = ""

    def config_file_path(self) -> str:
        """Путь до конфигурационного файла

        :rtype: str
        """

        return self.__config_file_path

    def env_key(self) -> str:
        return self.__env

    def env_mode_str(self) -> str:
        env_mode = "Development"
        if self.is_production():
            env_mode = "Production"
        return env_mode

    def keys(self) -> list:
        """Получить список ключей для загруженных аргументов

        :return: список ключей для загруженных аргументов
        :rtype: list
        """

        return list(self.__args)

    def args(self) -> dict:
        """Получить массив загруженных аргументов

        :return: массив загруженных аргументов
        :rtype: dict
        """

        return self.__args

    def arg(self, key: str, default=None):
        """Получить значение аргумента настроек

        :param key: ключ
        :type key: str
        :param default: базовое значение
        :type default: Any
        :return: значение аргумента настроек
        :rtype: Any
        """

        if not key in self.__args:
            return default
        return self.__args[key]

    def set_arg(self, key: str, value):
        """Задать значение аргумента настроек

        :param key: ключ
        :type key: str
        :param value: значение
        :type value: Any
        """

        self.__args[key] = value

    def is_production(self) -> bool:
        """Check is ENV Production

        :return: is ENV Production
        :rtype: bool
        """

        if self.arg(self.__env, '') == 'production':
            return True
        return False

    def is_development(self) -> bool:
        """Check is ENV Development

        :return: is ENV Development
        :rtype: bool
        """

        return not self.is_production()
