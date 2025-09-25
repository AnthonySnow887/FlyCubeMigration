import os
import re
import importlib
from abc import ABCMeta, abstractmethod, abstractproperty
from src.Logger.ConsoleLogger import ConsoleLogger
from src.Database.DatabaseFactory import DatabaseFactory
from src.Helper.Helper import Helper
from src.Migration.Migrators.BaseMigrator import BaseMigrator
from src.Migration.Migrators.SQLiteMigrator import SQLiteMigrator
from src.Migration.Migrators.PostgreSQLMigrator import PostgreSQLMigrator
from src.Migration.Migrators.MySQLMigrator import MySQLMigrator


class BaseMigration:
    __metaclass__ = ABCMeta
    __version = None
    __file = None
    __db_name = ''
    __db_adapter = None
    __migrator = None

    def __init__(self, version: int = None):
        m = importlib.import_module(self.__module__)
        self.__file = m.__file__
        b_name = os.path.basename(self.__file)
        result = re.search('^([0-9]{14})_(.*)\.py$', b_name)
        if result:
            self.__version = int(result.group(1))
        elif not version is None:
            self.__version = version

    #
    # abstract methods:
    #

    @abstractmethod
    def up(self):
        """Внесение изменений миграции"""

    @abstractmethod
    def down(self):
        """Удаление изменений миграции"""

    #
    # base methods to override if needed:
    #

    def configuration(self):
        """Метод конфигурирования миграции

        NOTE: override this method for correct implementation.
        """

    #
    # base public methods:
    #

    def is_valid(self) -> bool:
        """Является ли объект миграции корректным

        :rtype: bool
        """

        return self.__version > 0 and len(str(self.__version)) == 14

    def version(self) -> int:
        """Версия миграции

        :rtype: int
        """

        return self.__version

    def database(self) -> str:
        """Используемая база данных

        :rtype: str
        """

        return self.__db_name

    def set_database(self, db_name: str):
        """Задать имя используемой базы данных

        :param db_name: имя используемой базы данных
        """

        self.__db_name = db_name.strip()

    def database_adapter_name(self) -> str:
        """Название адаптера для работы с базой данных

        :rtype: str
        """

        if self.__db_adapter:
            return self.__db_adapter.name()
        return ""

    def migrate(self, version: int, migrator_class_name: str) -> bool:
        """Выполнить миграцию

        :param version: версия
        :param migrator_class_name: название класса мигратора
        :rtype: bool
        """

        if migrator_class_name == "":
            return False
        # get adapter
        self.__db_adapter = DatabaseFactory.instance().create_database_adapter({'database': self.database()})
        if not self.__db_adapter:
            return False
        # make migrator
        migrator_ = Helper.lookup(migrator_class_name, globals())
        self.__migrator = migrator_(self.__db_adapter)
        if not self.__migrator:
            return False
        # migrate
        self.__db_adapter.begin_transaction()
        try:
            if version >= self.__version:
                self.up()
            else:
                self.down()
            result = self.__db_adapter.commit_transaction()
        except Exception as err:
            print(ConsoleLogger.instance().make_color_string(f"[BaseMigration] Migrate failed! Error: {err}", 'error'))
            self.__db_adapter.rollback_transaction()
            result = False

        del self.__migrator
        self.__db_adapter.disconnect()
        del self.__db_adapter
        return result

    def export_migrate(self, version: int, migrator_class_name: str, dir_export: str) -> bool:
        """Выполнить экспорт миграции в SQL файл

        :param version: версия
        :param migrator_class_name: название класса мигратора
        :param dir_export: каталог для экспорта миграций
        :rtype: bool
        """

        if migrator_class_name == "":
            return False
        # get adapter
        self.__db_adapter = DatabaseFactory.instance().create_database_adapter({'database': self.database()})
        if not self.__db_adapter:
            return False

        # make export sql file name
        export_file = os.path.basename(self.__file).replace(".py", ".sql")
        export_file = f"{dir_export}/{export_file}"

        # Creates a new export file
        with open(export_file, 'w') as f:
            pass

        # make migrator
        migrator_ = Helper.lookup(migrator_class_name, globals())
        self.__migrator = migrator_(self.__db_adapter, export_file)
        if not self.__migrator:
            return False
        # export migrate
        try:
            if version >= self.__version:
                self.up()
            else:
                self.down()
            result = True
        except Exception as err:
            print(ConsoleLogger.instance().make_color_string(f"[BaseMigration] Export migration failed! Error: {err}", 'error'))
            result = False

        del self.__migrator
        self.__db_adapter.disconnect()
        del self.__db_adapter
        return result

    #
    # migration public methods:
    #

    def create_extension(self, name: str, props: dict = {}):
        """Подключить расширение базы данных

        :param name: название
        :type name: str
        :param props: свойства
        :type props: dict

        Supported Props:
          - [bool] if_not_exists - добавить флаг 'IF NOT EXISTS'
        """

        if not self.__migrator:
            return
        self.__migrator.create_extension(name, props)

    def drop_extension(self, name: str, props: dict = {}):
        """Удалить расширение базы данных

        :param name: название
        :type name: str
        :param props: свойства
        :type props: dict

        Supported Props:
          - [bool] if_exists - добавить флаг 'IF EXISTS'
        """

        if not self.__migrator:
            return
        self.__migrator.drop_extension(name, props)

    def create_schema(self, name: str, props: dict = {}):
        """Создать новую схему данных

        :param name: название
        :type name: str
        :param props: свойства
        :type props: dict

        Supported Props:
          - [bool] if_not_exists - добавить флаг 'IF NOT EXISTS'
        """

        if not self.__migrator:
            return
        self.__migrator.create_schema(name, props)

    def drop_schema(self, name: str, props: dict = {}):
        """Удалить схему данных

        :param name: название
        :type name: str
        :param props: свойства
        :type props: dict

        Supported Props:
          - [bool] if_exists - добавить флаг 'IF EXISTS'
        """

        if not self.__migrator:
            return
        self.__migrator.drop_schema(name, props)

    def create_table(self, name: str, args: dict):
        """Создать таблицу

        :param name: название
        :type name: str
        :param args: массив колонок и их спецификация
        :type args: dict

        Supported Keys:
          - [bool]     if_not_exists  - добавить флаг 'IF NOT EXISTS' (только для таблицы)
          - [bool]     id             - использовать колонку ID или нет (будет задана как первичный ключ)
          - [string]   type           - тип данных колонки (обязательный)
          - [integer]  limit          - размер данных колонки
          - [bool]     null           - может ли быть NULL
          - [string]   default        - базовое значение
          - [bool]     primary_key    - использовать как первичный ключ
          - [bool]     unique         - является уникальным
          - [string]   unique_group   - является уникальной группой (значение: имя группы)

        NOTE:
            id - serial not NULL (for MySQL: bigint unsigned)

            createTable('test', {
                'id': False,
                'if_not_exists': True,
                'my_id': {
                    'type': 'integer',
                    'null': False,
                    'primary_key': True
                },
                'my_data': {
                    'type': 'string',
                    'limit': 128,
                    'default': ''
                }
            });
        """

        if not self.__migrator:
            return
        self.__migrator.create_table(name, args)

    def rename_table(self, name: str, new_name: str):
        """Переименовать таблицу

        :param name: имя
        :param new_name: новое имя
        """

        if not self.__migrator:
            return
        self.__migrator.rename_table(name, new_name)

    def drop_table(self, name: str, props: dict = {}):
        """Удалить таблицу

        :param name: название
        :param props: свойства

        Supported Props:
          - [bool] if_exists - добавить флаг 'IF EXISTS'
          - [bool] cascade   - добавить флаг 'CASCADE'
        """

        if not self.__migrator:
            return
        self.__migrator.drop_table(name, props)

    def add_column(self, table_name: str, column_name: str, props: dict = {}):
        """Добавить колонку в таблицу

        :param table_name: название таблицы
        :param column_name: название колонки
        :param props: свойства

        Supported Props:
          - [bool]     if_not_exists  - добавить флаг 'IF NOT EXISTS'
          - [string]   type           - тип данных колонки (обязательный)
          - [integer]  limit          - размер данных колонки
          - [bool]     null           - может ли быть NULL
          - [string]   default        - базовое значение
        """

        if not self.__migrator:
            return
        self.__migrator.add_column(table_name, column_name, props)

    def rename_column(self, table_name: str, column_name: str, column_new_name: str):
        """Переименовать колонку в таблице

        :param table_name: название таблицы
        :param column_name: название колонки
        :param column_new_name: новое название колонки
        """

        if not self.__migrator:
            return
        self.__migrator.rename_column(table_name, column_name, column_new_name)

    def change_column(self, table_name: str, column_name: str, new_type: str, props: dict = {}):
        """Изменить тип колонки и ее дополнительные параметры, если они заданы

        :param table_name: название таблицы
        :param column_name: название колонки
        :param new_type: новый тип данных
        :param props: свойства

        Supported Props:
          - [integer]  limit          - размер данных колонки
          - [bool]     null           - может ли быть NULL
          - [string]   default        - базовое значение
        """

        if not self.__migrator:
            return
        self.__migrator.change_column(table_name, column_name, new_type, props)

    def change_column_default(self, table_name: str, column_name: str, default=None):
        """Изменить/Удалить секцию DEFAULT у колонки

        :param table_name: название таблицы
        :param column_name: название колонки
        :param default: значение секции DEFAULT (если None - секция DEFAULT удаляется)
        """

        if not self.__migrator:
            return
        self.__migrator.change_column_default(table_name, column_name, default)

    def change_column_null(self, table_name: str, column_name: str, not_null: bool = False):
        """Добавить/Удалить секцию NOT NULL у колонки

        :param table_name: название таблицы
        :param column_name: название колонки
        :param not_null: значение секции (если False - секция NOT NULL удаляется)
        """

        if not self.__migrator:
            return
        self.__migrator.change_column_null(table_name, column_name, not_null)

    def drop_column(self, table_name: str, column_name: str):
        """Удалить колонку из таблицы

        :param table_name: название таблицы
        :param column_name: название колонки
        """

        if not self.__migrator:
            return
        self.__migrator.drop_column(table_name, column_name)

    def add_index(self, table_name: str, columns: list, props: dict = {}):
        """Добавить индекс для таблицы

        :param table_name: название таблицы
        :param columns: названия колонок
        :param props: свойства

        Supported Props:
          - [string] name    - имя индекса (необязательное)
          - [bool]   unique  - является ли уникальным
        """

        if not self.__migrator:
            return
        self.__migrator.add_index(table_name, columns, props)

    def rename_index(self, table_name: str, old_name: str, new_name: str):
        """Переименовать индекс для таблицы

        :param table_name: название таблицы
        :param old_name: старое название
        :param new_name: новое название
        """

        if not self.__migrator:
            return
        self.__migrator.rename_index(table_name, old_name, new_name)

    def drop_index(self, table_name: str, props: dict = {}):
        """Удалить индекс таблицы

        :param table_name: название таблицы
        :param props: свойства

        Supported Props:
          - [array] columns  - имена колонок
          - [string] name    - имя индекса
          - [bool] if_exists - добавить флаг 'IF EXISTS' (может не поддерживаться) (default: False)
          - [bool] cascade   - добавить флаг 'CASCADE' (может не поддерживаться) (default: False)

        NOTE: Должен быть задан хотябы один!
        NOTE: Приоритет отдается name!
        """

        if not self.__migrator:
            return
        self.__migrator.drop_index(table_name, props)

    def set_primary_key(self, table_name: str, column_name: str):
        """Установить новый первичный ключ таблицы

        :param table_name: название таблицы
        :param column_name: название колонки
        """

        if not self.__migrator:
            return
        self.__migrator.set_primary_key(table_name, column_name)

    def drop_primary_key(self, table_name: str, column_name: str):
        """Удалить первичный ключ таблицы

        :param table_name: название таблицы
        :param column_name: название колонки
        """

        if not self.__migrator:
            return
        self.__migrator.drop_primary_key(table_name, column_name)

    def add_foreign_key(self,
                        table_name: str, columns: list,
                        ref_table_name: str, ref_columns: list,
                        props: dict = {}):
        """Добавить вторичный ключ для таблицы

        :param table_name: название таблицы
        :param columns: названия колонок
        :param ref_table_name: название таблицы на котороу ссылаемся
        :param ref_columns: названия колонок на которые ссылаемся
        :param props: свойства

        Supported Props:
          - [bool] on_update - добавить флаг 'ON UPDATE' (может не поддерживаться)
          - [bool] on_delete - добавить флаг 'ON DELETE' (может не поддерживаться)
          - [string] action  - добавить флаг поведения 'NO ACTION / CASCADE / RESTRICT / SET DEFAULT / SET NULL' (может не поддерживаться)
          - [string] name    - задать имя вторичного ключа
        """

        if not self.__migrator:
            return
        self.__migrator.add_foreign_key(table_name, columns, ref_table_name, ref_columns, props)

    def add_foreign_key_p_key(self,
                              table_name: str, column_name: str,
                              ref_table_name: str,
                              props: dict = {}):
        """Добавить вторичный ключ для таблицы, ссылающийся на первичный ключ другой таблицы

        :param table_name: название таблицы
        :param column_name: название колонки
        :param ref_table_name: название таблицы на котороу ссылаемся
        :param props: свойства

        NOTE: данный метод создает вторичный ключ, который будет ссылаться на первичный ключ таблицы ref_table_name.

        Supported Props:
          - [bool] on_update - добавить флаг 'ON UPDATE' (может не поддерживаться)
          - [bool] on_delete - добавить флаг 'ON DELETE' (может не поддерживаться)
          - [string] action  - добавить флаг поведения 'NO ACTION / CASCADE / RESTRICT / SET DEFAULT / SET NULL' (может не поддерживаться)
          - [string] name    - задать имя вторичного ключа
        """

        if not self.__migrator:
            return
        self.__migrator.add_foreign_key_p_key(table_name, column_name, ref_table_name, props)

    def drop_foreign_key(self, table_name: str, columns: list):
        """Удалить вторичный ключ таблицы

        :param table_name: название таблицы
        :param columns: названия колонок
        """

        if not self.__migrator:
            return
        self.__migrator.drop_foreign_key(table_name, columns)

    def drop_foreign_key_p_key(self, table_name: str, column_name: str):
        """Удалить вторичный ключ таблицы, ссылающийся на первичный ключ другой таблицы

        :param table_name: название таблицы
        :param column_name: название колонки
        :return:
        """

        if not self.__migrator:
            return
        self.__migrator.drop_foreign_key_p_key(table_name, column_name)

    def execute(self, sql: str):
        """Выполнить SQL запрос

        :param sql: SQL запрос
        """

        if not self.__migrator:
            return
        self.__migrator.execute(sql)
