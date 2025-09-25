import sys
import os
import re
import importlib
import shutil
from src.Logger.ConsoleLogger import ConsoleLogger
from src.Database.DatabaseFactory import DatabaseFactory
from src.Helper.Helper import Helper
from src.Migration.Migrators.BaseMigrator import BaseMigrator
from src.Migration.Migrators.SQLiteMigrator import SQLiteMigrator
from src.Migration.Migrators.PostgreSQLMigrator import PostgreSQLMigrator
from src.Migration.Migrators.MySQLMigrator import MySQLMigrator
from src.PostScripts.PostScripts import PostScripts


class MigrationCore:
    __instance = None
    __migrators = {}
    __migrations = {}

    def __init__(self):
        # --- append default migrators - --
        self.__register_migrator('sqlite', 'SQLiteMigrator')
        self.__register_migrator('sqlite3', 'SQLiteMigrator')
        self.__register_migrator('postgresql', 'PostgreSQLMigrator')
        self.__register_migrator('mysql', 'MySQLMigrator')
        self.__register_migrator('mariadb', 'MySQLMigrator')

    @staticmethod
    def instance():
        """Получить инстанс класса

        :return: инстанс класса
        :rtype: MigrationCore
        """

        if not isinstance(MigrationCore.__instance, MigrationCore):
            MigrationCore.__instance = MigrationCore()
        return MigrationCore.__instance

    def load_migrations(self, path: str):
        """Произвести поиск и зугрузку файлов миграций

        :param path: путь до каталога с файлами миграций
        :return:
        """

        if len(self.__migrations) > 0:
            return
        if not os.path.isdir(path):
            return
        sys.path.append(path)
        arr = os.listdir(path)
        for f in arr:
            file_extension = Helper.file_extension(f)
            if not file_extension.lower() == ".py":
                continue
            result = re.search('^([0-9]{14})_(.*)\.py$', f)
            if not result:
                continue
            migration_version = int(result.group(1))
            migration_class_name = result.group(2)
            try:
                module = importlib.import_module(f"{migration_version}_{migration_class_name}")
                class_ = getattr(module, migration_class_name)
                instance = class_()
                if instance.is_valid():
                    self.__migrations[migration_version] = instance
                else:
                    del instance
            except Exception as inst:
                print(f"Exception: {inst}")

    def reset_migrations(self):
        """Сбросить список миграций"""

        self.__migrations = {}

    def current_version(self, db_names: list):
        """Получить текущую версию установленных миграций

        :param db_names: список имен баз данных в которых будет производиться поиск
        :return:
        """

        return self.__current_migration_version(db_names)

    def migrate(self, db_names: list, version: int = -1):
        """Метод миграции базы данных

        :param db_names: список имен баз данных в которых будет производиться миграция
        :param version: версия миграции, до которой требуется актуализировать базы данных
        """

        if len(self.__migrations) == 0:
            print(ConsoleLogger.instance().make_color_string("[MigrationsCore] Not found migration files!", 'error'))
            return
        if len(db_names) == 0:
            print(ConsoleLogger.instance().make_color_string("[MigrationsCore] Database names list is Empty!", 'error'))
            return
        if version < 0:
            version = sys.maxsize
        # select current migration version from database
        current_version = self.__current_migration_version(db_names)
        # check versions
        if current_version == version:
            print(ConsoleLogger.instance().make_color_string("[MigrationsCore] Current migration version already installed", 'info'))
            return
        # sort migrations
        m_command = 'up'
        mirgations = self.__migrations
        if current_version < version:
            mirgations = Helper.sort(mirgations)
        else:
            mirgations = Helper.sort(mirgations, True)
            m_command = 'down'

        print(f"[MigrationsCore] Start migrate from {current_version}:")
        new_version = -1
        changed_databases = []
        for k, m in mirgations.items():
            # configuration current migration
            m.configuration()
            # select migration info
            m_version = int(k)
            m_class_name = type(m).__name__
            m_database = m.database()
            m_database_title = m_database
            if m_database_title == "":
                m_database_title = 'primary'
            # select current adapter name
            db_adapter_name = ''
            if m_database == "":
                db_adapter_name = DatabaseFactory.instance().primary_adapter_name()
            else:
                db_adapter_name = DatabaseFactory.instance().secondary_adapter_name(m_database)
            # check db adapter name
            if db_adapter_name == "":
                print(ConsoleLogger.instance().make_color_string("[MigrationsCore] Invalid current database adapter name!", 'error'))
                return
            # select current migrator name
            migrator_name = self.__migrator_class_name(db_adapter_name)
            if migrator_name == "":
                print(ConsoleLogger.instance().make_color_string(f"[MigrationsCore] Invalid current migrator name for database adapter (name: {db_adapter_name})!", 'error'))
                return
            # check database name
            if not m_database in db_names:
                continue
            # check version
            if m_command == "up" and new_version == version:
                break
            elif m_command == "down" and m_version == version:
                new_version = version
                break
            # select current migration database version
            current_db_version = self.__last_migration_version(m_database)
            # check skip
            if m_command == "up" and current_version >= version:
                print(f"[{ConsoleLogger.instance().make_color_string('Skip', 'info')}][DB: {m_database_title}] Migration ({m_version} - '{m_class_name}')")
                continue
            if m_command == "up" and current_db_version >= m_version:
                print(f"[{ConsoleLogger.instance().make_color_string('Skip', 'info')}][DB: {m_database_title}] Migration ({m_version} - '{m_class_name}')")
                continue
            if m_command == "down" and current_version < m_version:
                print(f"[{ConsoleLogger.instance().make_color_string('Skip', 'info')}][DB: {m_database_title}] Migration ({m_version} - '{m_class_name}')")
                continue
            if m_command == "down" and current_db_version < m_version:
                print(f"[{ConsoleLogger.instance().make_color_string('Skip', 'info')}][DB: {m_database_title}] Migration ({m_version} - '{m_class_name}')")
                continue

            msg_attr = "to"
            if m_command == "down":
                msg_attr = "from"

            print(f"[{ConsoleLogger.instance().make_color_string(m_command.capitalize(), 'ok')}][DB: {m_database_title}] Migrate {msg_attr} ({m_version} - '{m_class_name}')")
            if not m.migrate(version, migrator_name):
                print(f"[{ConsoleLogger.instance().make_color_string(m_command.capitalize() + ' - FAILED', 'error')}][DB: {m_database_title}] Migrate {msg_attr} ({m_version} - '{m_class_name}')")
                break

            # save changed database
            if not m_database in changed_databases:
                changed_databases.append(m_database)

            new_version = m_version
            if m_command == "up":
                self.__append_migration_version(m_database, new_version)
            elif m_command == "down":
                self.__remove_migration_version(m_database, new_version)

        print("[MigrationsCore] Finish migrate")
        # select current migration version from database
        current_version = self.__current_migration_version(db_names)
        print(f"[MigrationsCore] Current migration version: {current_version}")

        # Execute post-scripts
        self.__execute_all_post_scripts(changed_databases)

    def migrate_export(self, db_names: list, version: int = -1, dir_export: str = ""):
        """Метод выгрузки миграций базы данных в SQL файлы

        :param db_names: список имен баз данных для которых требуется миграция
        :param version: версия миграции, до которой требуется актуализировать базы данных
        :param dir_export: каталог для экспорта миграций
        """

        if len(self.__migrations) == 0:
            print(ConsoleLogger.instance().make_color_string("[MigrationsCore] Not found migration files!", 'error'))
            return
        if len(db_names) == 0:
            print(ConsoleLogger.instance().make_color_string("[MigrationsCore] Database names list is Empty!", 'error'))
            return
        if version < 0:
            version = sys.maxsize
        # sort migrations
        m_command = 'up'
        mirgations = self.__migrations
        if version > 0:
            mirgations = Helper.sort(mirgations)
        else:
            mirgations = Helper.sort(mirgations, True)
            m_command = 'down'

        print(f"[MigrationsCore] Start export migrations:")

        # check export dir
        if not os.path.exists(dir_export):
            os.mkdir(dir_export)
        else:
            shutil.rmtree(dir_export)
            os.mkdir(dir_export)

        new_version = -1
        for k, m in mirgations.items():
            # configuration current migration
            m.configuration()
            # select migration info
            m_version = int(k)
            m_class_name = type(m).__name__
            m_database = m.database()
            m_database_title = m_database
            if m_database_title == "":
                m_database_title = 'primary'
            # select current adapter name
            db_adapter_name = ''
            if m_database == "":
                db_adapter_name = DatabaseFactory.instance().primary_adapter_name()
            else:
                db_adapter_name = DatabaseFactory.instance().secondary_adapter_name(m_database)
            # check db adapter name
            if db_adapter_name == "":
                print(ConsoleLogger.instance().make_color_string(
                    "[MigrationsCore] Invalid current database adapter name!", 'error'))
                return
            # select current migrator name
            migrator_name = self.__migrator_class_name(db_adapter_name)
            if migrator_name == "":
                print(ConsoleLogger.instance().make_color_string(
                    f"[MigrationsCore] Invalid current migrator name for database adapter (name: {db_adapter_name})!",
                    'error'))
                return
            # check database name
            if not m_database in db_names:
                continue
            # check version
            if m_command == "up" and new_version == version:
                break
            elif m_command == "down" and m_version == version:
                new_version = version
                break

            # check dir for current database migrations
            tmp_dir_export = f"{Helper.splice_symbol_last(dir_export, '/')}/{m_database_title}"
            if not os.path.exists(tmp_dir_export):
                os.mkdir(tmp_dir_export)

            print(
                f"[{ConsoleLogger.instance().make_color_string(m_command.capitalize(), 'ok')}][DB: {m_database_title}] Export ({m_version} - '{m_class_name}')")
            if not m.export_migrate(version, migrator_name, Helper.splice_symbol_last(tmp_dir_export, '/')):
                print(
                    f"[{ConsoleLogger.instance().make_color_string(m_command.capitalize() + ' - FAILED', 'error')}][DB: {m_database_title}] Export ({m_version} - '{m_class_name}')")
                break

            new_version = m_version

        print("[MigrationsCore] Finish export migrations")
        print(f"[MigrationsCore] Directory for export: {dir_export}")

    def rollback(self, db_names: list, step: int = 1):
        """Метод отката миграции

        :param db_names: список имен баз данных в которых будет производиться миграция
        :param step: число шагов, на которые нужно откатить базу данных
        """

        if len(self.__migrations) == 0:
            print(ConsoleLogger.instance().make_color_string("[MigrationsCore] Not found migration files!", 'error'))
            return
        if len(db_names) == 0:
            print(ConsoleLogger.instance().make_color_string("[MigrationsCore] Database names list is Empty!", 'error'))
            return
        if step == 0:
            print(ConsoleLogger.instance().make_color_string("[MigrationsCore] Not specified the number of steps to change. Stop.", 'error'))
            return
        if step < 0 or step > len(self.__migrations.keys()):
            step = len(self.__migrations.keys())
        # select current migration version from database
        current_version = self.__current_migration_version(db_names)
        # check versions
        if current_version == 0:
            print(ConsoleLogger.instance().make_color_string("[MigrationsCore] Migrations have not yet been installed!", 'warning'))
            return
        mirgations = Helper.sort(self.__migrations, True)
        print(f"[MigrationsCore] Start rollback from {current_version}:")
        new_version = -1
        save_version_in_db = False
        changed_databases = []
        for k, m in mirgations.items():
            # configuration current migration
            m.configuration()
            # select migration info
            m_version = int(k)
            m_class_name = type(m).__name__
            m_database = m.database()
            m_database_title = m_database
            if m_database_title == "":
                m_database_title = 'primary'
            # select current adapter name
            db_adapter_name = ''
            if m_database == "":
                db_adapter_name = DatabaseFactory.instance().primary_adapter_name()
            else:
                db_adapter_name = DatabaseFactory.instance().secondary_adapter_name(m_database)
            # check db adapter name
            if db_adapter_name == "":
                print(ConsoleLogger.instance().make_color_string("[MigrationsCore] Invalid current database adapter name!", 'error'))
                return
            # select current migrator name
            migrator_name = self.__migrator_class_name(db_adapter_name)
            if migrator_name == "":
                print(ConsoleLogger.instance().make_color_string(f"[MigrationsCore] Invalid current migrator name for database adapter (name: {db_adapter_name})!", 'error'))
                return
            # check save version in db
            if save_version_in_db:
                self.__append_migration_version(m_database, m_version)
                save_version_in_db = False

            # select current migration database version
            current_db_version = self.__last_migration_version(m_database)
            # check steps
            if step == 0:
                new_version = m_version
                break
            # check database name
            if not m_database in db_names:
                continue
            # check version
            if current_version < m_version or current_db_version < m_version:
                print(f"[{ConsoleLogger.instance().make_color_string('Skip', 'info')}][DB: {m_database_title}] Migration ({m_version} - '{m_class_name}')")
                continue
            print(f"[{ConsoleLogger.instance().make_color_string('Down', 'ok')}][DB: {m_database_title}] Migrate from ({m_version} - '{m_class_name}')")
            if not m.migrate(m_version - 1, migrator_name):
                print(
                    f"[{ConsoleLogger.instance().make_color_string('Down - FAILED', 'error')}][DB: {m_database_title}] Migrate from ({m_version} - '{m_class_name}')")
                break

            # save changed database
            if not m_database in changed_databases:
                changed_databases.append(m_database)

            new_version = m_version
            self.__remove_migration_version(m_database, new_version)
            # check is remove all versions
            tmp_current_db_version = self.__last_migration_version(m_database)
            if tmp_current_db_version == 0:
                save_version_in_db = True
            step -= 1

        print("[MigrationsCore] Finish rollback")
        # select current migration version from database
        current_version = self.__current_migration_version(db_names)
        print(f"[MigrationsCore] Current migration version: {current_version}")

        # Execute post-scripts
        self.__execute_all_post_scripts(changed_databases)

    def migrate_redo(self, db_names: list, step: int = 1):
        """Метод перустановки миграции

        :param db_names: список имен баз данных в которых будет производиться миграция
        :param step: число шагов, на которые нужно перустановить базу данных
        """

        cur_v = self.current_version(db_names)
        if cur_v == 0:
            print(ConsoleLogger.instance().make_color_string("[MigrationsCore] Migrations have not yet been installed!", 'warning'))
            return
        self.rollback(db_names, step)
        print("")
        self.migrate(db_names, cur_v)

    def migrate_status(self, db_names: list):
        """Запросить состояние миграций

        :param db_names: список имен баз данных в которых будет производиться поиск
        :return:
        """

        cur_v = self.current_version(db_names)
        all_v = self.__all_install_migration_versions(db_names)
        tmp_state_lst = {}
        for v in all_v:
            m_class_name = ConsoleLogger.instance().make_color_string('???', 'warning')
            state_str = ConsoleLogger.instance().make_color_string('File Not Found', 'warning')
            db_title = ConsoleLogger.instance().make_color_string('???', 'warning')
            if v in self.__migrations:
                m = self.__migrations[v]
                # configuration current migration
                m.configuration()
                # select migration info
                m_class_name = type(m).__name__
                m_database = m.database()
                db_title = m_database
                if db_title == "":
                    db_title = 'primary'
                # check database name
                if not m_database in db_names:
                    continue  # skip
                state_str = ConsoleLogger.instance().make_color_string('Not Installed', 'info-2')
                if self.__last_migration_version(m.database()) >= v:
                    state_str = ConsoleLogger.instance().make_color_string('Installed', 'ok')

            tmp_state_lst[v] = str(f"[{state_str}][DB: {db_title}] Migration ({v} - '{m_class_name}')")

        size = 0
        for k, m in self.__migrations.items():
            # configuration current migration
            m.configuration()
            # select migration info
            m_class_name = type(m).__name__
            m_database = m.database()
            db_title = m_database
            if db_title == "":
                db_title = 'primary'
            # check database name
            if not m_database in db_names:
                continue  # skip
            state_str = ConsoleLogger.instance().make_color_string('Not Installed', 'info-2')
            if self.__last_migration_version(m.database()) >= k:
                state_str = ConsoleLogger.instance().make_color_string('Installed', 'ok')
            tmp_state_lst[k] = str(f"[{state_str}][DB: {db_title}] Migration ({k} - '{m_class_name}')")
            size += 1

        size_installed = len(all_v)
        tmp_state_lst_sorted = Helper.sort(tmp_state_lst)
        print(f"[MigrationsCore] Current database version: {cur_v}")
        print(f"[MigrationsCore] Found migration files: {size}")
        print(f"[MigrationsCore] Installed in database: {size_installed}")
        for t in tmp_state_lst_sorted.values():
            print(t)

    def db_create(self, db_name: str):
        """Создать базу данных для миграций

        :param db_name: имя базы данных
        """

        db_adapter_name = DatabaseFactory.instance().primary_adapter_name()
        if db_name != "":
            db_adapter_name = DatabaseFactory.instance().secondary_adapter_name(db_name)
        if db_adapter_name == "":
            print(ConsoleLogger.instance().make_color_string("[MigrationsCore] Invalid current database adapter name!", 'error'))
            return
        migrator_name = self.__migrator_class_name(db_adapter_name)
        if migrator_name == "":
            print(ConsoleLogger.instance().make_color_string(f"[MigrationsCore] Invalid current migrator name for database adapter (name: {db_adapter_name})!", 'error'))
            return
        # processing
        # create database
        db_adapter = DatabaseFactory.instance().create_database_adapter({'database': db_name, 'auto-connect': False})
        if not db_adapter:
            print(ConsoleLogger.instance().make_color_string("[MigrationsCore] Invalid database adapter (None)!", 'error'))
            return
        migrator_ = Helper.lookup(migrator_name, globals())
        migrator = migrator_(db_adapter)
        if not migrator:
            print(ConsoleLogger.instance().make_color_string("[MigrationsCore] Invalid database migrator (None)!", 'error'))
            return
        db_adapter_settings = db_adapter.settings()
        tmp_db_name = db_adapter_settings.get('database', '')
        if tmp_db_name == "":
            print(ConsoleLogger.instance().make_color_string("[MigrationsCore] Invalid database adapter settings (not found key 'database' or empty value)!", 'error'))
            return

        print(f"[MigrationsCore] Start create database (name: {tmp_db_name})")
        del db_adapter_settings['database']
        db_adapter.set_settings(db_adapter_settings)
        if not db_adapter.connect():
            print(ConsoleLogger.instance().make_color_string("[MigrationsCore] Connect to database server failed!", 'error'))
            return
        migrator.create_database(tmp_db_name)
        del migrator
        del db_adapter
        print("[MigrationsCore] Finish create database")

    def db_drop(self, db_name: str):
        """Удалить базу данных для миграций

        :param db_name: имя базы данных
        """

        db_adapter_name = DatabaseFactory.instance().primary_adapter_name()
        if db_name != "":
            db_adapter_name = DatabaseFactory.instance().secondary_adapter_name(db_name)
        if db_adapter_name == "":
            print(ConsoleLogger.instance().make_color_string("[MigrationsCore] Invalid current database adapter name!", 'error'))
            return
        migrator_name = self.__migrator_class_name(db_adapter_name)
        if migrator_name == "":
            print(ConsoleLogger.instance().make_color_string(f"[MigrationsCore] Invalid current migrator name for database adapter (name: {db_adapter_name})!", 'error'))
            return
        # processing
        # create database
        db_adapter = DatabaseFactory.instance().create_database_adapter({'database': db_name, 'auto-connect': False})
        if not db_adapter:
            print(ConsoleLogger.instance().make_color_string("[MigrationsCore] Invalid database adapter (None)!", 'error'))
            return
        migrator_ = Helper.lookup(migrator_name, globals())
        migrator = migrator_(db_adapter)
        if not migrator:
            print(ConsoleLogger.instance().make_color_string("[MigrationsCore] Invalid database migrator (None)!", 'error'))
            return
        db_adapter_settings = db_adapter.settings()
        tmp_db_name = db_adapter_settings.get('database', '')
        if tmp_db_name == "":
            print(ConsoleLogger.instance().make_color_string("[MigrationsCore] Invalid database adapter settings (not found key 'database' or empty value)!", 'error'))
            return

        print(f"[MigrationsCore] Start drop database (name: {tmp_db_name})")
        del db_adapter_settings['database']
        db_adapter.set_settings(db_adapter_settings)
        if not db_adapter.connect():
            print(ConsoleLogger.instance().make_color_string("[MigrationsCore] Connect to database server failed!", 'error'))
            return
        migrator.drop_database(tmp_db_name)
        del migrator
        del db_adapter
        print("[MigrationsCore] Finish drop database")

    def __register_migrator(self, name: str, class_name: str):
        """Зарегистрировать обработчик миграций

        :param name: название
        :param class_name: имя класса
        :return:
        """

        name = name.strip()
        class_name = class_name.strip()
        if name == "" or class_name == "":
            return
        if name in self.__migrators:
            return
        self.__migrators[name] = class_name

    def __migrator_class_name(self, name: str) -> str:
        """Запросить имя класса адаптера миграции

        :param name: название адаптера
        :type name: str
        :return: имя класса адаптера миграции
        :rtype: str
        """

        name = name.strip()
        if name in self.__migrators:
            return self.__migrators[name]
        return ""

    def __check_migration_tables(self, db_names: list) -> bool:
        """Проверка таблицы версий миграций

        :param db_names: список имен баз данных в которых будет производиться проверка
        :return:
        """

        for name in db_names:
            if not self.__check_migration_table(name):
                return False
        return True

    def __check_migration_table(self, db_name: str) -> bool:
        """Проверка таблицы версий миграций для конкретной БД

        :param db_name: имя базы данных
        :return:
        """

        db_adapter = DatabaseFactory.instance().create_database_adapter({'database': db_name})
        if not db_adapter:
            return False
        show_out = ConsoleLogger.instance().show_out()
        ConsoleLogger.instance().set_show_out(False)
        tables = db_adapter.tables()
        ConsoleLogger.instance().set_show_out(show_out)
        if 'schema_migrations' in tables or 'public.schema_migrations' in tables:
            return True
        sql = """
        CREATE TABLE schema_migrations (
            version VARCHAR(128) NOT NULL,
            CONSTRAINT schema_migrations_pkey PRIMARY KEY (version)
        )
        """
        try:
            show_out = ConsoleLogger.instance().show_out()
            ConsoleLogger.instance().set_show_out(False)
            db_adapter.query(sql)
            ConsoleLogger.instance().set_show_out(show_out)
        except:
            return False
        return True

    def __current_migration_version(self, db_names: list, max: bool = True) -> int:
        """Получить текущую версию установленных миграций

        :param db_names: список имен баз данных в которых будет производиться поиск
        :param max: максимальная или минимальная
        :return:
        """

        if len(db_names) == 0 or not self.__check_migration_tables(db_names):
            return 0
        # --- select ---
        tmp_version = 0
        if not max:
            tmp_version = sys.maxsize
        for name in db_names:
            tmp_version_s = self.__last_migration_version(name)
            if max and tmp_version < tmp_version_s:
                tmp_version = tmp_version_s
            elif not max and tmp_version > tmp_version_s:
                tmp_version = tmp_version_s

        return tmp_version

    def __last_migration_version(self, db_name: str) -> int:
        """Получить последнюю версию установленных миграций для конкретной БД

        :param db_name: имя базы данных
        :return:
        """

        if not self.__check_migration_table(db_name):
            return 0
        db_adapter = DatabaseFactory.instance().create_database_adapter({'database': db_name})
        if not db_adapter:
            return 0
        show_out = ConsoleLogger.instance().show_out()
        ConsoleLogger.instance().set_show_out(False)
        res = db_adapter.query("SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 1;")
        ConsoleLogger.instance().set_show_out(show_out)
        if len(res) == 0:
            return 0
        return int(res[0]['version'])

    def __all_install_migration_versions(self, db_names: list) -> list:
        """Получить все версии установленных миграций

        :param db_names: список имен баз данных в которых будет производиться поиск
        :return:
        """

        if len(db_names) == 0 or not self.__check_migration_tables(db_names):
            return []
        # --- select - --
        tmp_versions = []
        for name in db_names:
            tmp_versions += self.__install_migration_versions(name)

        # --- sort ASC ---
        tmp_versions.sort()
        return tmp_versions

    def __install_migration_versions(self, db_name: str) -> list:
        """Получить все версии установленных миграций для конкретной БД

        :param db_name: имя базы данных
        :return:
        """

        if not self.__check_migration_table(db_name):
            return []
        db_adapter = DatabaseFactory.instance().create_database_adapter({'database': db_name})
        if not db_adapter:
            return []
        show_out = ConsoleLogger.instance().show_out()
        ConsoleLogger.instance().set_show_out(False)
        res = db_adapter.query("SELECT version FROM schema_migrations ORDER BY version ASC;")
        ConsoleLogger.instance().set_show_out(show_out)
        tmp_list = []
        for row in res:
            tmp_list.append(int(row['version']))
        return tmp_list

    def __append_migration_version(self, db_name: str, version: int):
        """Добавить запись в базу данных об установленной версии миграции

        :param db_name: имя базы данных
        :param version: номер версии
        :return:
        """

        if not self.__check_migration_table(db_name):
            return
        db_adapter = DatabaseFactory.instance().create_database_adapter({'database': db_name})
        if not db_adapter:
            return
        show_out = ConsoleLogger.instance().show_out()
        ConsoleLogger.instance().set_show_out(False)
        db_adapter.query(f"INSERT INTO schema_migrations (version) VALUES ('{version}');")
        ConsoleLogger.instance().set_show_out(show_out)

    def __remove_migration_version(self, db_name: str, version: int):
        """Удалить запись из базы данных об установленной версии миграции

        :param db_name: имя базы данных
        :param version: номер версии
        :return:
        """

        if not self.__check_migration_table(db_name):
            return
        db_adapter = DatabaseFactory.instance().create_database_adapter({'database': db_name})
        if not db_adapter:
            return
        show_out = ConsoleLogger.instance().show_out()
        ConsoleLogger.instance().set_show_out(False)
        db_adapter.query(f"DELETE FROM schema_migrations WHERE version = '{version}';")
        ConsoleLogger.instance().set_show_out(show_out)

    def __execute_all_post_scripts(self, databases: list):
        """Установить все SQL post-скрипты на все измененные базы данных

        :param databases: список измененных бах данных
        :return:
        """

        # Execute post-scripts
        print("[MigrationsCore] Execute post-scripts:")
        post_scripts = PostScripts.instance().post_scripts()
        if len(post_scripts) == 0:
            print(f"[{ConsoleLogger.instance().make_color_string('Skip', 'info')}] List of post-scripts is Empty.")
        elif len(databases) == 0:
            print(f"[{ConsoleLogger.instance().make_color_string('Skip', 'info')}] List of changed databases is Empty.")
        else:
            is_ok = True
            for f in post_scripts:
                for db in databases:
                    db_title = str(db)
                    if db_title == "":
                        db_title = 'primary'

                    print(f"[{ConsoleLogger.instance().make_color_string('Install', 'ok')}][DB: {db_title}] Post-script: {f}")
                    is_ok = self.__execute_post_script("", f)
                    if not is_ok:
                        print(f"[{ConsoleLogger.instance().make_color_string('Install' + ' - FAILED', 'error')}][DB: {db_title}] Post-script: {f}")
                        break
                if not is_ok:
                    break

        print("[MigrationsCore] Finish execute post-scripts")

    def __execute_post_script(self, db_name: str, post_script_path: str) -> bool:
        """Установить SQL post-скрипт

        :param db_name: имя базы данных
        :param post_script_path: путь до post-скрипта
        :return:
        """

        db_adapter = DatabaseFactory.instance().create_database_adapter({'database': db_name})
        if not db_adapter:
            return False
        db_adapter.begin_transaction()
        try:
            db_adapter.query(Helper.read_file(post_script_path))
            result = db_adapter.commit_transaction()
        except Exception as err:
            print(ConsoleLogger.instance().make_color_string(f"[MigrationsCore] Execute post-script failed! Error: {err}",
                                                             'error'))
            db_adapter.rollback_transaction()
            result = False

        db_adapter.disconnect()
        return result
