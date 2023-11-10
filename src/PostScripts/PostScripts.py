import os
import os.path
import yaml
from src.Config.Config import Config
from src.Logger.ConsoleLogger import ConsoleLogger
from src.Helper.Helper import Helper


class PostScripts:
    __instance = None
    __settings = {}
    __postScripts = []
    __postScriptsConfig = "post-scripts.yml"

    @staticmethod
    def instance():
        """Получить инстанс класса

        :return: инстанс класса
        :rtype: PostScripts
        """

        if not isinstance(PostScripts.__instance, PostScripts):
            PostScripts.__instance = PostScripts()
        return PostScripts.__instance

    def load_config(self, path: str):
        """Загрузить настройки для работы с post-скриптами

        :param path: путь до каталога с конфигурационным файлом
        :type path: str
        """

        if len(self.__settings) != 0:
            return
        if not os.path.isdir(path):
            return  # TODO show error!
        config_file_path = f"{Helper.splice_symbol_last(path, '/')}/{self.__postScriptsConfig}"
        if not os.path.exists(config_file_path):
            return  # TODO show error!
        config_data = {}
        with open(config_file_path, "r") as stream:
            try:
                config_data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise exc

        # Load mode type
        working_mode = 'development'
        if Config.instance().is_production():
            working_mode = 'production'

        # Load primary settings
        self.__settings = self.__load_post_scripts_settings(working_mode, config_data, config_file_path)

        # Load files
        if 'file' in self.__settings:
            lst = []
            if isinstance(self.__settings['file'], str):
                lst = [self.__settings['file']]
            elif isinstance(self.__settings['file'], list):
                lst = self.__settings['file']

            for f in lst:
                if not os.path.isfile(f):
                    continue
                file_extension = Helper.file_extension(f)
                if not file_extension.lower() == ".sql":
                    continue
                if not os.path.abspath(f) in self.__postScripts:
                    self.__postScripts.append(os.path.abspath(f))

            if 'file-use-sort' in self.__settings and self.__settings['file-use-sort']:
                self.__postScripts.sort()

        # Load dirs
        if 'directory' in self.__settings:
            lst = []
            if isinstance(self.__settings['directory'], str):
                lst = [self.__settings['directory']]
            elif isinstance(self.__settings['directory'], list):
                lst = self.__settings['directory']

            recursive = False
            if 'directory-recursive-load' in self.__settings:
                recursive = bool(self.__settings['directory-recursive-load'])

            for value in lst:
                for f in self.__load_post_scripts_files(os.path.abspath(value), recursive):
                    if not f in self.__postScripts:
                        self.__postScripts.append(f)

    def reset_config(self):
        """Сбросить настройки конфигурации"""

        # Reset primary settings
        self.__settings = {}
        # Reset post scripts list
        self.__postScripts = []

    def post_scripts(self) -> list:
        """Получить список загруженных SQL скриптов

        :return: список загруженных SQL скриптов
        :rtype: list
        """
        return self.__postScripts

    def __load_post_scripts_settings(self, key: str, yaml_data: dict, path: str) -> dict:
        """Загрузить настройки по работе с post-скриптами

        :param key: ключ раздела настроек в YAML
        :type key: str
        :param yaml_data: данные файла конфигурации
        :type yaml_data: dict
        :param path: путь до файла конфигурации
        :type path: str
        :return: настройки по работе с post-скриптами
        :rtype: dict
        :raise: Exception
        """
        if not key in yaml_data:
            raise Exception(f"[PostScripts][loadPostScriptsSettings] Not found post scripts {key} settings! Path: {path}")
        settings = yaml_data[key]
        if not settings:
            settings = {}
        return settings

    def __load_post_scripts_files(self, dir_path: str, recursive: bool = False) -> list:
        """Загрузить SQL скрипты из каталога

        :param dir_path: путь до каталога
        :type dir_path: str
        :param recursive: использовать рекурсивную загрузку
        :type recursive: bool
        :return: список SQL скриптов
        :rtype: list
        :raise: Exception
        """
        if not os.path.isdir(dir_path):
            return []
        found_files = []
        # load only dir files
        if not recursive:
            for f in os.listdir(dir_path):
                if not os.path.isfile(f):
                    continue
                file_extension = Helper.file_extension(f)
                if not file_extension.lower() == ".sql":
                    continue
                found_files.append(f)
        else:
            # load dir files recursive
            for address, dirs, files in os.walk(dir_path):
                for f in files:
                    file_extension = Helper.file_extension(f)
                    if not file_extension.lower() == ".sql":
                        continue
                    found_files.append(os.path.join(address, f))
        found_files.sort()
        return found_files
