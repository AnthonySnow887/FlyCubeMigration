import os
import re
from src.Migration.Migrators.BaseMigrator import BaseMigrator


class SQLiteMigrator(BaseMigrator):
    def __init__(self, db_adapter, export_file: str = None):
        super().__init__(db_adapter, export_file)

    #
    # base methods to override if needed:
    #

    def create_database(self, name: str, props: dict = {}):
        """Создать новую базу данных

        :param name: название базы данных
        :type name: str
        :param props: свойства
        :type props: dict
        """

        if name == "":
            raise Exception("[SQLiteMigrator][create_database] Database name is Empty!")
        if not self._db_adapter:
            raise Exception("[SQLiteMigrator][create_database] Database adapter is None!")
        settings = self._db_adapter.settings()
        settings['database'] = name
        self._db_adapter.disconnect()
        self._db_adapter.set_settings(settings)
        self._db_adapter.connect()

    def drop_database(self, name: str):
        """Удалить базу данных

        :param name: название базы данных
        :type name: str

        NOTE: override this method for correct implementation.
        """

        if name == "":
            raise Exception("[SQLiteMigrator][drop_database] Database name is Empty!")
        if not self._db_adapter:
            raise Exception("[SQLiteMigrator][create_database] Database adapter is None!")
        if not os.path.exists(name):
            return
        os.remove(name)

    def table_indexes(self, table_name: str) -> dict:
        """Запросить список индексов для таблицы

        :param table_name: название таблицы
        :type table_name: str
        :rtype: dict

        Return example:
        {
            'index_1': {
                'index_name': 'index_1',
                'unique': True,
                'table': 'test_table',
                'columns': [ 'column_1', 'column_2']
            }
            'index_2': {
                'index_name': 'index_2',
                'unique': False,
                'table': 'test_table',
                'columns': [ 'column_2' ]
            }
            ...
        }
        """

        if not self._db_adapter:
            return {}
        # select table information
        res = self._db_adapter.query(f"PRAGMA INDEX_LIST(\"{table_name}\");")
        if len(res) == 0:
            return {}
        tmp_indexes = {}
        for r in res:
            i_name = r['name']
            i_res = self._db_adapter.query(f"PRAGMA index_info(\"{i_name}\");")
            if len(i_res) == 0:
                continue
            i_columns = []
            for info in i_res:
                i_columns.append(info['name'])

            tmp_indexes[i_name] = {
                'index_name': i_name,
                'unique': bool(r['unique']),  # TODO check is correct bool!
                'table': table_name,
                'columns': i_columns
            }
        return tmp_indexes

    def table_columns(self, table_name: str) -> dict:
        """Запросить список колонок таблицы и их типов

        :param table_name: название таблицы
        :type table_name: str
        :rtype: dict

        Return example:
        {
            'column_1': {
                'table': 'test_table',
                'column': 'column_1',
                'type': 'text',
                'is_pk': True,
                'is_not_null': True
                'default': None
            }
            'column_2': {
                'table': 'test_table',
                'column': 'column_2',
                'type': 'integer'
                'is_pk': False
                'is_not_null': False
                'default': 999
            }
            ...
        }
        """

        if not self._db_adapter:
            return {}
        # select table information
        res = self._db_adapter.query(f"PRAGMA table_info(\"{table_name}\");")
        if len(res) == 0:
            return {}
        tmp_columns = {}
        for r in res:
            tmp_columns[r['name']] = {
                'table': table_name,
                'column': r['name'],
                'type': r['type'],
                'is_pk': bool(r['pk']),
                'is_not_null': bool(r['notnull']),
                'default': r['dflt_value']
            }
        return tmp_columns

    def table_primary_keys(self, table_name: str) -> dict:
        """Запросить список первичных ключей таблицы

        :param table_name: название таблицы
        :type table_name: str
        :rtype: dict

        Return example:
        {
            'test_pkey': {
                'name':'test_pkey'
                'table': 'public.test',
                'column': 'my_id',
                'type': 'integer'
            }
        }
        """

        if not self._db_adapter:
            return {}
        # select table sql
        res = self._db_adapter.query(f"SELECT sql FROM sqlite_master WHERE name = \"{table_name}\";")
        if len(res) == 0:
            return {}
        t_sql = res[0]['sql']
        # select table information
        res = self._db_adapter.query(f"PRAGMA table_info(\"{table_name}\");")
        if len(res) == 0:
            return {}
        tmp_columns = {}
        for r in res:
            if not bool(r['pk']):
                continue
            tmp_name = ""
            column_name = r['name']
            reg = r'\bCONSTRAINT \"?([A-Za-z0-9_]+\_pkey)\"? PRIMARY KEY \(' + column_name + r'\)'
            result = re.search(reg, t_sql)
            if result:
                tmp_name = result.group(1).strip()
            if tmp_name == "":
                tmp_name = f"{table_name}_pkey"

            tmp_columns[tmp_name] = {
                'name': tmp_name,
                'table': table_name,
                'column': column_name,
                'type': r['type']
            }
        return tmp_columns

    def table_foreign_keys(self, table_name) -> dict:
        """Запросить список вторичных ключей для таблицы

        :param table_name: название таблицы
        :type table_name: str
        :rtype: dict

        Return example:
        {
            'fk_test_2_test_id': {
                'name':'fk_test_2_test_id',
                'table': 'public.test_2',
                'column': 'test_id',
                'ref_table': 'public.test',
                'ref_column': 'my_id'
                'on_update': 'NO ACTION',
                'on_delete': 'NO ACTION'
            }
            ...
        }
        """

        if not self._db_adapter:
            return {}
        # select table sql
        res = self._db_adapter.query(f"SELECT sql FROM sqlite_master WHERE name = \"{table_name}\";")
        if len(res) == 0:
            return {}
        t_sql = res[0]['sql']
        # select table information
        res = self._db_adapter.query(f"PRAGMA foreign_key_list(\"{table_name}\");")
        if len(res) == 0:
            return {}
        tmp_list = {}
        for r in res:
            tmp_columns_list = str(r['from']).split(',')
            tmp_columns = []
            for i in tmp_columns_list:
                tmp_columns.append(i.strip())

            tmp_name = ""
            columns_names = r['from']
            ref_table_name = r['table']
            ref_columns_names = r['to']
            reg = r'\bCONSTRAINT \"?([A-Za-z0-9_]+)\"? FOREIGN KEY \(' + columns_names + r'\) REFERENCES \"' + ref_table_name + r'\"\(' + ref_columns_names + r'\)'
            result = re.search(reg, t_sql)
            if result:
                tmp_name = result.group(1).strip()
            if tmp_name == "":
                tmp_columns_names = str("_").join(tmp_columns)
                tmp_name = f"fk_{table_name}_{tmp_columns_names}"

            tmp_list[tmp_name] = {
                'name': tmp_name,
                'table': table_name,
                'column': columns_names,
                'ref_table': ref_table_name,
                'ref_column': ref_columns_names,
                'on_update': r['on_update'],
                'on_delete': r['on_delete']
            }
        return tmp_list

    def add_column(self, table_name: str, column_name: str, props: dict = {}):
        """Добавить колонку в таблицу

        :param table_name: название таблицы
        :param column_name: название колонки
        :param props: свойства

        Supported Props:
            [bool]     if_not_exists  - добавить флаг 'IF NOT EXISTS'
            [string]   type           - тип данных колонки (обязательный)
            [integer]  limit          - размер данных колонки
            [bool]     null           - может ли быть NULL
            [string]   default        - базовое значение
        """

        if table_name == "" or column_name == "":
            raise Exception("[SQLiteMigrator][add_column] Table name or column name is Empty!")
        if not self._db_adapter:
            raise Exception("[SQLiteMigrator][add_column] Database adapter is None!")
        # select table information
        res = self._db_adapter.query(f"SELECT sql FROM sqlite_master WHERE name = \"{table_name}\";")
        if len(res) == 0:
            raise Exception("[SQLiteMigrator][add_column] SQL data in sqlite_master is Empty!")
        sql = str(res[0]['sql'])
        if sql.find(f"\"{column_name}\"") != -1:
            raise Exception(
                f"[SQLiteMigrator][add_column] Column \"{column_name}\" in table \"{table_name}\" already exists!")
        tmp_res = self._prepare_create_column(column_name, props)
        sql = tmp_res.get('sql', '')
        if sql == '':
            raise Exception("[SQLiteMigrator][add_column] Prepare create column return empty result!")
        self._exec_query_or_export(f"ALTER TABLE \"{table_name}\" ADD {sql};")

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

        if table_name == "" or column_name == "" or new_type == "":
            raise Exception("[SQLiteMigrator][change_column] Table name or column name or new type is Empty!")
        if not self._db_adapter:
            raise Exception("[SQLiteMigrator][change_column] Database adapter is None!")
        # select indexes
        tmp_indexes = self.table_indexes(table_name)
        # select table information
        res = self._db_adapter.query(f"SELECT sql FROM sqlite_master WHERE name = \"{table_name}\";")
        if len(res) == 0:
            raise Exception(
                f"[SQLiteMigrator][change_column] SQL data in sqlite_master fot table \"{table_name}\" is Empty!")
        sql = str(res[0]['sql'])
        pos = sql.find(f"\"{column_name}\"")
        if pos == -1:
            raise Exception(
                f"[SQLiteMigrator][change_column] Column \"{column_name}\" not found in table \"{table_name}\"!")
        new_sql = ""
        new_sql_part = ""
        use_skip = False
        for i in range(len(sql)):
            tmp_char = sql[i]
            if tmp_char == ',':
                if not use_skip:
                    new_sql_part = new_sql_part.strip()
                    if len(new_sql) == 0 and len(new_sql_part) > 0:
                        new_sql = str(new_sql_part)
                    elif len(new_sql) > 0 and len(new_sql_part) > 0:
                        new_sql += f",\n{str(new_sql_part)}"
                else:
                    props['type'] = new_type
                    tmp_res = self._prepare_create_column(column_name, props)
                    tmp_sql = tmp_res.get('sql', '')
                    if len(new_sql) == 0 and len(tmp_sql) > 0:
                        new_sql = str(tmp_sql)
                    elif len(new_sql) > 0 and len(tmp_sql) > 0:
                        new_sql += f",\n{str(tmp_sql)}"
                    use_skip = False

                new_sql_part = ""
                continue

            new_sql_part += str(tmp_char)
            if i == pos:
                use_skip = True

        if not use_skip:
            new_sql_part = new_sql_part.strip()
            if len(new_sql) == 0 and len(new_sql_part) > 0:
                new_sql = str(new_sql_part)
            elif len(new_sql) > 0 and len(new_sql_part) > 0:
                new_sql += f",\n{str(new_sql_part)}"

        # remove last ';'
        new_sql = str(new_sql).strip()
        if new_sql[len(new_sql) - 1] == ';':
            new_sql = str(new_sql[0:(len(new_sql) - 1)]).strip()
        # add last ')'
        if new_sql[len(new_sql) - 1] != ')':
            new_sql += " )"

        res = self._db_adapter.query(f"PRAGMA table_info(\"{table_name}\");")
        if len(res) == 0:
            raise Exception(f"[SQLiteMigrator][change_column] SQLite table_info(\"{table_name}\") return empty result!")
        tmp_columns = ""
        for r in res:
            if tmp_columns != "":
                tmp_columns += ","
            tmp_columns += f" {r['name']}"
        tmp_columns = str(tmp_columns).strip()

        # rename old table
        new_t_name = f"{table_name}_old"
        self._exec_query_or_export(f"ALTER TABLE \"{table_name}\" RENAME TO \"{new_t_name}\";")
        # create new table
        self._exec_query_or_export(new_sql)
        # insert new data
        if tmp_columns != "":
            self._exec_query_or_export(f"INSERT INTO \"{table_name}\" SELECT {tmp_columns} FROM \"{new_t_name}\";")
        # drop old table
        self._exec_query_or_export(f"DROP TABLE \"{new_t_name}\";")
        # append indexes
        tmp_indexes_upd = self.table_indexes(table_name)
        for index in tmp_indexes.values():
            if index['index_name'] in tmp_indexes_upd:
                continue  # skip - already added
            self.add_index(table_name, index['columns'], {'unique': index['unique']})

    def change_column_default(self, table_name: str, column_name: str, default=None):
        """Изменить/Удалить секцию DEFAULT у колонки

        :param table_name: название таблицы
        :param column_name: название колонки
        :param default: значение секции DEFAULT (если None - секция DEFAULT удаляется)
        """

        if table_name == "" or column_name == "":
            raise Exception("[SQLiteMigrator][change_column_default] Table name or column name is Empty!")
        if not self._db_adapter:
            raise Exception("[SQLiteMigrator][change_column_default] Database adapter is None!")
        # select indexes
        tmp_indexes = self.table_indexes(table_name)
        # select columns
        tmp_columns = self.table_columns(table_name)
        if not column_name in tmp_columns:
            raise Exception(
                f"[SQLiteMigrator][change_column_default] Column \"{column_name}\" not found in table columns list!")
        # select table information
        res = self._db_adapter.query(f"SELECT sql FROM sqlite_master WHERE name = \"{table_name}\";")
        if len(res) == 0:
            raise Exception(
                f"[SQLiteMigrator][change_column_default] SQL data in sqlite_master fot table \"{table_name}\" is Empty!")
        sql = str(res[0]['sql'])
        pos = sql.find(f"\"{column_name}\"")
        if pos == -1:
            raise Exception(
                f"[SQLiteMigrator][change_column_default] Column \"{column_name}\" not found in table \"{table_name}\"!")
        new_sql = ""
        new_sql_part = ""
        use_skip = False
        for i in range(len(sql)):
            tmp_char = sql[i]
            if tmp_char == ',':
                if not use_skip:
                    new_sql_part = new_sql_part.strip()
                    if len(new_sql) == 0 and len(new_sql_part) > 0:
                        new_sql = str(new_sql_part)
                    elif len(new_sql) > 0 and len(new_sql_part) > 0:
                        new_sql += f",\n{str(new_sql_part)}"
                else:
                    props = {
                        'type': tmp_columns[column_name]['type'],
                        'default': self.__prepare_default(default),
                        'null': not tmp_columns[column_name]['is_not_null']
                    }
                    tmp_res = self._prepare_create_column(column_name, props)
                    tmp_sql = tmp_res.get('sql', '')
                    if len(new_sql) == 0 and len(tmp_sql) > 0:
                        new_sql = str(tmp_sql)
                    elif len(new_sql) > 0 and len(tmp_sql) > 0:
                        new_sql += f",\n{str(tmp_sql)}"
                    use_skip = False

                new_sql_part = ""
                continue

            new_sql_part += str(tmp_char)
            if i == pos:
                use_skip = True

        if not use_skip:
            new_sql_part = new_sql_part.strip()
            if len(new_sql) == 0 and len(new_sql_part) > 0:
                new_sql = str(new_sql_part)
            elif len(new_sql) > 0 and len(new_sql_part) > 0:
                new_sql += f",\n{str(new_sql_part)}"

        # remove last ';'
        new_sql = str(new_sql).strip()
        if new_sql[len(new_sql) - 1] == ';':
            new_sql = str(new_sql[0:(len(new_sql) - 1)]).strip()
        # add last ')'
        if new_sql[len(new_sql) - 1] != ')':
            new_sql += " )"

        tmp_columns_names = str(", ").join(tmp_columns.keys())

        # rename old table
        new_t_name = f"{table_name}_old"
        self._exec_query_or_export(f"ALTER TABLE \"{table_name}\" RENAME TO \"{new_t_name}\";")
        # create new table
        self._exec_query_or_export(new_sql)
        # insert new data
        if tmp_columns_names != "":
            self._exec_query_or_export(f"INSERT INTO \"{table_name}\" SELECT {tmp_columns_names} FROM \"{new_t_name}\";")
        # drop old table
        self._exec_query_or_export(f"DROP TABLE \"{new_t_name}\";")
        # append indexes
        tmp_indexes_upd = self.table_indexes(table_name)
        for index in tmp_indexes.values():
            if index['index_name'] in tmp_indexes_upd:
                continue  # skip - already added
            self.add_index(table_name, index['columns'], {'unique': index['unique']})

    def change_column_null(self, table_name: str, column_name: str, not_null: bool = False):
        """Добавить/Удалить секцию NOT NULL у колонки

        :param table_name: название таблицы
        :param column_name: название колонки
        :param not_null: значение секции (если False - секция NOT NULL удаляется)
        """

        if table_name == "" or column_name == "":
            raise Exception("[SQLiteMigrator][change_column_null] Table name or column name is Empty!")
        if not self._db_adapter:
            raise Exception("[SQLiteMigrator][change_column_null] Database adapter is None!")
        # select indexes
        tmp_indexes = self.table_indexes(table_name)
        # select columns
        tmp_columns = self.table_columns(table_name)
        if not column_name in tmp_columns:
            raise Exception(
                f"[SQLiteMigrator][change_column_null] Column \"{column_name}\" not found in table columns list!")
        # select table information
        res = self._db_adapter.query(f"SELECT sql FROM sqlite_master WHERE name = \"{table_name}\";")
        if len(res) == 0:
            raise Exception(
                f"[SQLiteMigrator][change_column_null] SQL data in sqlite_master fot table \"{table_name}\" is Empty!")
        sql = str(res[0]['sql'])
        pos = sql.find(f"\"{column_name}\"")
        if pos == -1:
            raise Exception(
                f"[SQLiteMigrator][change_column_null] Column \"{column_name}\" not found in table \"{table_name}\"!")
        new_sql = ""
        new_sql_part = ""
        use_skip = False
        for i in range(len(sql)):
            tmp_char = sql[i]
            if tmp_char == ',':
                if not use_skip:
                    new_sql_part = new_sql_part.strip()
                    if len(new_sql) == 0 and len(new_sql_part) > 0:
                        new_sql = str(new_sql_part)
                    elif len(new_sql) > 0 and len(new_sql_part) > 0:
                        new_sql += f",\n{str(new_sql_part)}"
                else:
                    props = {
                        'type': tmp_columns[column_name]['type'],
                        'default': self.__prepare_default(tmp_columns[column_name]['default']),
                        'null': not not_null
                    }
                    tmp_res = self._prepare_create_column(column_name, props)
                    tmp_sql = tmp_res.get('sql', '')
                    if len(new_sql) == 0 and len(tmp_sql) > 0:
                        new_sql = str(tmp_sql)
                    elif len(new_sql) > 0 and len(tmp_sql) > 0:
                        new_sql += f",\n{str(tmp_sql)}"
                    use_skip = False

                new_sql_part = ""
                continue

            new_sql_part += str(tmp_char)
            if i == pos:
                use_skip = True

        if not use_skip:
            new_sql_part = new_sql_part.strip()
            if len(new_sql) == 0 and len(new_sql_part) > 0:
                new_sql = str(new_sql_part)
            elif len(new_sql) > 0 and len(new_sql_part) > 0:
                new_sql += f",\n{str(new_sql_part)}"

        # remove last ';'
        new_sql = str(new_sql).strip()
        if new_sql[len(new_sql) - 1] == ';':
            new_sql = str(new_sql[0:(len(new_sql) - 1)]).strip()
        # add last ')'
        if new_sql[len(new_sql) - 1] != ')':
            new_sql += " )"

        tmp_columns_names = str(", ").join(tmp_columns.keys())

        # rename old table
        new_t_name = f"{table_name}_old"
        self._exec_query_or_export(f"ALTER TABLE \"{table_name}\" RENAME TO \"{new_t_name}\";")
        # create new table
        self._exec_query_or_export(new_sql)
        # insert new data
        if tmp_columns_names != "":
            self._exec_query_or_export(f"INSERT INTO \"{table_name}\" SELECT {tmp_columns_names} FROM \"{new_t_name}\";")
        # drop old table
        self._exec_query_or_export(f"DROP TABLE \"{new_t_name}\";")
        # append indexes
        tmp_indexes_upd = self.table_indexes(table_name)
        for index in tmp_indexes.values():
            if index['index_name'] in tmp_indexes_upd:
                continue  # skip - already added
            self.add_index(table_name, index['columns'], {'unique': index['unique']})

    def drop_column(self, table_name: str, column_name: str):
        """Удалить колонку из таблицы

        :param table_name: название таблицы
        :param column_name: название колонки

        NOTE: not supported in SQLite -> override this method for correct implementation.
        """

        if table_name == "" or column_name == "":
            raise Exception("[SQLiteMigrator][drop_column] Table name or column name is Empty!")
        if not self._db_adapter:
            raise Exception("[SQLiteMigrator][drop_column] Database adapter is None!")
        # select table information
        res = self._db_adapter.query(f"SELECT sql FROM sqlite_master WHERE name = \"{table_name}\";")
        if len(res) == 0:
            raise Exception(
                f"[SQLiteMigrator][drop_column] SQL data in sqlite_master fot table \"{table_name}\" is Empty!")
        sql = str(res[0]['sql'])
        pos = sql.find(f"\"{column_name}\"")
        if pos == -1:
            raise Exception(
                f"[SQLiteMigrator][drop_column] Column \"{column_name}\" not found in table \"{table_name}\"!")
        new_sql = ""
        new_sql_part = ""
        use_skip = False
        for i in range(len(sql)):
            tmp_char = sql[i]
            if tmp_char == ',':
                if not use_skip:
                    new_sql_part = new_sql_part.strip()
                    if len(new_sql) == 0 and len(new_sql_part) > 0:
                        new_sql = str(new_sql_part)
                    elif len(new_sql) > 0 and len(new_sql_part) > 0:
                        new_sql += f",\n{str(new_sql_part)}"
                else:
                    use_skip = False

                new_sql_part = ""
                continue

            new_sql_part += str(tmp_char)
            if i == pos:
                use_skip = True

        if not use_skip:
            new_sql_part = new_sql_part.strip()
            if len(new_sql) == 0 and len(new_sql_part) > 0:
                new_sql = str(new_sql_part)
            elif len(new_sql) > 0 and len(new_sql_part) > 0:
                new_sql += f",\n{str(new_sql_part)}"

        # remove last ';'
        new_sql = str(new_sql).strip()
        if new_sql[len(new_sql) - 1] == ';':
            new_sql = str(new_sql[0:(len(new_sql) - 1)]).strip()
        # add last ')'
        if new_sql[len(new_sql) - 1] != ')':
            new_sql += " )"

        res = self._db_adapter.query(f"PRAGMA table_info(\"{table_name}\");")
        if len(res) == 0:
            raise Exception(f"[SQLiteMigrator][drop_column] SQLite table_info(\"{table_name}\") return empty result!")
        tmp_columns = ""
        for r in res:
            if r['name'] == column_name:
                continue
            if tmp_columns != "":
                tmp_columns += ","
            tmp_columns += f" {r['name']}"
        tmp_columns = str(tmp_columns).strip()

        # rename old table
        new_t_name = f"{table_name}_old"
        self._exec_query_or_export(f"ALTER TABLE \"{table_name}\" RENAME TO \"{new_t_name}\";")
        # create new table
        self._exec_query_or_export(new_sql)
        # insert new data
        if tmp_columns != "":
            self._exec_query_or_export(f"INSERT INTO \"{table_name}\" SELECT {tmp_columns} FROM \"{new_t_name}\";")
        # drop old table
        self._exec_query_or_export(f"DROP TABLE \"{new_t_name}\";")

    def rename_index(self, table_name: str, old_name: str, new_name: str):
        """Переименовать индекс для таблицы

        :param table_name: название таблицы
        :param old_name: старое название
        :param new_name: новое название
        """

        if table_name == "" or old_name == "" or new_name == "":
            raise Exception("[SQLiteMigrator][rename_index] Table name or old name or new name is Empty!")
        if not self._db_adapter:
            raise Exception("[SQLiteMigrator][rename_index] Database adapter is None!")
        if old_name == new_name:
            raise Exception("[SQLiteMigrator][rename_index] Old name is the same as new name!")
        tmp_indexes = self.table_indexes(table_name)
        if len(tmp_indexes) == 0:
            raise Exception(f"[SQLiteMigrator][rename_index] Table \"{table_name}\" has no indexes!")
        i_index_info = {}
        for info in tmp_indexes.values():
            if info['index_name'] == old_name:
                i_index_info = info
                break
        if len(i_index_info.keys()) == 0:
            if new_name in tmp_indexes:
                return  # Already added
            raise Exception(f"[SQLiteMigrator][rename_index] Not found info for table index \"{old_name}\"!")
        # drop old index
        self.drop_index(table_name, {'name': old_name})
        # add new index
        self.add_index(table_name, i_index_info['columns'], {'name': new_name, 'unique': i_index_info['unique']})

    def set_primary_key(self, table_name: str, column_name: str):
        """Установить новый первичный ключ таблицы

        :param table_name: название таблицы
        :param column_name: название колонки
        """

        if table_name == "" or column_name == "":
            raise Exception("[SQLiteMigrator][set_primary_key] Table name or column name is Empty!")
        if not self._db_adapter:
            raise Exception("[SQLiteMigrator][set_primary_key] Database adapter is None!")
        # drop old primary keys
        tmp_p_keys = self.table_primary_keys(table_name)
        for info in tmp_p_keys.values():
            self.drop_primary_key(table_name, info['column'])
        # select foreign_keys
        res = self._db_adapter.query("PRAGMA foreign_keys;")
        if len(res) == 0:
            raise Exception("[SQLiteMigrator][set_primary_key] \"PRAGMA foreign_keys\" is Empty!")
        foreign_keys = res[0]['foreign_keys']
        # select defer_foreign_keys
        res = self._db_adapter.query("PRAGMA defer_foreign_keys;")
        if len(res) == 0:
            raise Exception("[SQLiteMigrator][set_primary_key] \"PRAGMA defer_foreign_keys\" is Empty!")
        defer_foreign_keys = res[0]['defer_foreign_keys']
        # set new states
        self._db_adapter.query("PRAGMA defer_foreign_keys = ON;")
        self._db_adapter.query("PRAGMA foreign_keys = OFF;")
        # select indexes
        tmp_indexes = self.table_indexes(table_name)
        # select columns
        tmp_columns = self.table_columns(table_name)
        # select table information
        res = self._db_adapter.query(f"SELECT sql FROM sqlite_master WHERE name = \"{table_name}\";")
        if len(res) == 0:
            raise Exception(
                f"[SQLiteMigrator][set_primary_key] SQL data in sqlite_master fot table \"{table_name}\" is Empty!")
        sql = res[0]['sql']
        new_sql = ""
        new_sql_part = ""
        for i in range(len(sql)):
            tmp_char = sql[i]
            if tmp_char == ',':
                new_sql_part = new_sql_part.strip()
                if len(new_sql) == 0 and len(new_sql_part) > 0:
                    new_sql = str(new_sql_part)
                elif len(new_sql) > 0 and len(new_sql_part) > 0:
                    new_sql += f",\n{str(new_sql_part)}"
                new_sql_part = ""
                continue

            new_sql_part += str(tmp_char)

        # add end of sql
        new_sql_part = new_sql_part.strip()
        if len(new_sql) == 0 and len(new_sql_part) > 0:
            new_sql = str(new_sql_part)
        elif len(new_sql) > 0 and len(new_sql_part) > 0:
            new_sql += f",\n{str(new_sql_part)}"

        # remove last ';'
        new_sql = str(new_sql).strip()
        if new_sql[len(new_sql) - 1] == ';':
            new_sql = str(new_sql[0:(len(new_sql) - 1)]).strip()
        # remove last ')'
        if new_sql[len(new_sql) - 1] == ')':
            new_sql = str(new_sql[0:(len(new_sql) - 1)]).strip()
        # add primary key
        tmp_table_list = table_name.split('.')
        tmp_p_key_name = f"{tmp_table_list[len(tmp_table_list) - 1]}_pkey"
        f_sql = f"CONSTRAINT \"{tmp_p_key_name}\" PRIMARY KEY ({column_name})"
        if new_sql != "":
            f_sql = f", \n{f_sql}"
        new_sql += f_sql
        # add last ')'
        new_sql += " )"

        tmp_columns_names = str(', ').join(tmp_columns.keys())

        # rename old table
        new_t_name = f"{table_name}_old"
        self._exec_query_or_export(f"ALTER TABLE \"{table_name}\" RENAME TO \"{new_t_name}\";")
        # create new table
        self._exec_query_or_export(new_sql)
        # insert new data
        if tmp_columns != "":
            self._exec_query_or_export(f"INSERT INTO \"{table_name}\" SELECT {tmp_columns_names} FROM \"{new_t_name}\";")
        # drop old table
        self._exec_query_or_export(f"DROP TABLE \"{new_t_name}\";")
        # append indexes
        tmp_indexes_upd = self.table_indexes(table_name)
        for index in tmp_indexes.values():
            if index['index_name'] in tmp_indexes_upd:
                continue  # skip - already added
            self.add_index(table_name, index['columns'], {'unique': index['unique']})
        # set old states
        self._db_adapter.query(f"PRAGMA defer_foreign_keys = {defer_foreign_keys};")
        self._db_adapter.query(f"PRAGMA foreign_keys = {foreign_keys};")

    def drop_primary_key(self, table_name: str, column_name: str):
        """Удалить первичный ключ таблицы

        :param table_name: название таблицы
        :param column_name: название колонки
        """

        if table_name == "" or column_name == "":
            raise Exception("[SQLiteMigrator][drop_primary_key] Table name or column name is Empty!")
        if not self._db_adapter:
            raise Exception("[SQLiteMigrator][drop_primary_key] Database adapter is None!")
        tmp_p_key_name = ""
        tmp_p_keys = self.table_primary_keys(table_name)
        for info in tmp_p_keys.values():
            if info['column'] == column_name:
                tmp_p_key_name = info['name']
                break
        if tmp_p_key_name == "":
            raise Exception(
                f"[SQLiteMigrator][drop_primary_key] Not found primary key name for table \"{table_name}\"!")
        # select foreign_keys
        res = self._db_adapter.query("PRAGMA foreign_keys;")
        if len(res) == 0:
            raise Exception("[SQLiteMigrator][drop_primary_key] \"PRAGMA foreign_keys\" is Empty!")
        foreign_keys = res[0]['foreign_keys']
        # select defer_foreign_keys
        res = self._db_adapter.query("PRAGMA defer_foreign_keys;")
        if len(res) == 0:
            raise Exception("[SQLiteMigrator][drop_primary_key] \"PRAGMA defer_foreign_keys\" is Empty!")
        defer_foreign_keys = res[0]['defer_foreign_keys']
        # set new states
        self._db_adapter.query("PRAGMA defer_foreign_keys = ON;")
        self._db_adapter.query("PRAGMA foreign_keys = OFF;")
        # select indexes
        tmp_indexes = self.table_indexes(table_name)
        # select columns
        tmp_columns = self.table_columns(table_name)
        # select table information
        res = self._db_adapter.query(f"SELECT sql FROM sqlite_master WHERE name = \"{table_name}\";")
        if len(res) == 0:
            raise Exception(
                f"[SQLiteMigrator][drop_primary_key] SQL data in sqlite_master fot table \"{table_name}\" is Empty!")
        sql = str(res[0]['sql'])
        pos = sql.find(f"CONSTRAINT \"{tmp_p_key_name}\" PRIMARY KEY")
        if pos == -1:
            raise Exception(
                f"[SQLiteMigrator][drop_primary_key] Not found primary key section in SQL data fot table \"{table_name}\"!")
        new_sql = ""
        new_sql_part = ""
        use_skip = False
        for i in range(len(sql)):
            tmp_char = sql[i]
            if tmp_char == ',':
                if not use_skip:
                    new_sql_part = new_sql_part.strip()
                    if len(new_sql) == 0 and len(new_sql_part) > 0:
                        new_sql = str(new_sql_part)
                    elif len(new_sql) > 0 and len(new_sql_part) > 0:
                        new_sql += f",\n{str(new_sql_part)}"
                else:
                    use_skip = False

                new_sql_part = ""
                continue

            new_sql_part += str(tmp_char)
            if i == pos:
                use_skip = True

        if not use_skip:
            new_sql_part = new_sql_part.strip()
            if len(new_sql) == 0 and len(new_sql_part) > 0:
                new_sql = str(new_sql_part)
            elif len(new_sql) > 0 and len(new_sql_part) > 0:
                new_sql += f",\n{str(new_sql_part)}"

        # remove last ';'
        new_sql = str(new_sql).strip()
        if new_sql[len(new_sql) - 1] == ';':
            new_sql = str(new_sql[0:(len(new_sql) - 1)]).strip()
        # add last ')'
        if new_sql[len(new_sql) - 1] != ')':
            new_sql += " )"

        tmp_columns_names = str(', ').join(tmp_columns)

        # rename old table
        new_t_name = f"{table_name}_old"
        self._exec_query_or_export(f"ALTER TABLE \"{table_name}\" RENAME TO \"{new_t_name}\";")
        # create new table
        self._exec_query_or_export(new_sql)
        # insert new data
        if tmp_columns != "":
            self._exec_query_or_export(f"INSERT INTO \"{table_name}\" SELECT {tmp_columns_names} FROM \"{new_t_name}\";")
        # drop old table
        self._exec_query_or_export(f"DROP TABLE \"{new_t_name}\";")
        # append indexes
        tmp_indexes_upd = self.table_indexes(table_name)
        for index in tmp_indexes.values():
            if index['index_name'] in tmp_indexes_upd:
                continue  # skip - already added
            self.add_index(table_name, index['columns'], {'unique': index['unique']})
        # set old states
        self._db_adapter.query(f"PRAGMA defer_foreign_keys = {defer_foreign_keys};")
        self._db_adapter.query(f"PRAGMA foreign_keys = {foreign_keys};")

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

        if table_name == "" or len(columns) == 0:
            raise Exception("[SQLiteMigrator][add_foreign_key] Table name or columns is Empty!")
        if ref_table_name == "" or len(ref_columns) == 0:
            raise Exception("[SQLiteMigrator][add_foreign_key] Reference table name or reference columns is Empty!")
        if not self._db_adapter:
            raise Exception("[SQLiteMigrator][add_foreign_key] Database adapter is None!")
        columns = list(set(columns))  # get uniq list
        columns = list(filter(len, columns))  # remove empty
        if len(columns) == 0:
            raise Exception("[SQLiteMigrator][add_foreign_key] Columns is Empty!")
        ref_columns = list(set(ref_columns))  # get uniq list
        ref_columns = list(filter(len, ref_columns))  # remove empty
        if len(ref_columns) == 0:
            raise Exception("[SQLiteMigrator][add_foreign_key] Reference columns is Empty!")
        # select foreign_keys
        res = self._db_adapter.query("PRAGMA foreign_keys;")
        if len(res) == 0:
            raise Exception("[SQLiteMigrator][add_foreign_key] \"PRAGMA foreign_keys\" is Empty!")
        foreign_keys = res[0]['foreign_keys']
        # select defer_foreign_keys
        res = self._db_adapter.query("PRAGMA defer_foreign_keys;")
        if len(res) == 0:
            raise Exception("[SQLiteMigrator][add_foreign_key] \"PRAGMA defer_foreign_keys\" is Empty!")
        defer_foreign_keys = res[0]['defer_foreign_keys']
        # set new states
        self._db_adapter.query("PRAGMA defer_foreign_keys = ON;")
        self._db_adapter.query("PRAGMA foreign_keys = OFF;")
        # select indexes
        tmp_indexes = self.table_indexes(table_name)
        # select columns
        tmp_columns = self.table_columns(table_name)
        # select table information
        res = self._db_adapter.query(f"SELECT sql FROM sqlite_master WHERE name = \"{table_name}\";")
        if len(res) == 0:
            raise Exception(
                f"[SQLiteMigrator][add_foreign_key] SQL data in sqlite_master fot table \"{table_name}\" is Empty!")
        sql = str(res[0]['sql'])
        new_sql = ""
        new_sql_part = ""
        for i in range(len(sql)):
            tmp_char = sql[i]
            if tmp_char == ',':
                new_sql_part = new_sql_part.strip()
                if len(new_sql) == 0 and len(new_sql_part) > 0:
                    new_sql = str(new_sql_part)
                elif len(new_sql) > 0 and len(new_sql_part) > 0:
                    new_sql += f",\n{str(new_sql_part)}"
                new_sql_part = ""
                continue

            new_sql_part += str(tmp_char)

        # add end of sql
        new_sql_part = new_sql_part.strip()
        if len(new_sql) == 0 and len(new_sql_part) > 0:
            new_sql = str(new_sql_part)
        elif len(new_sql) > 0 and len(new_sql_part) > 0:
            new_sql += f",\n{str(new_sql_part)}"

        # remove last ';'
        new_sql = str(new_sql).strip()
        if new_sql[len(new_sql) - 1] == ';':
            new_sql = str(new_sql[0:(len(new_sql) - 1)]).strip()
        # remove last ')'
        if new_sql[len(new_sql) - 1] == ')':
            new_sql = str(new_sql[0:(len(new_sql) - 1)]).strip()
        # add foreign key
        columns_names = str(", ").join(columns)
        columns_names_2 = str("_").join(columns)
        ref_columns_names = str(", ").join(ref_columns)
        tmp_name = f"fk_{table_name}_{columns_names_2}"
        if len(str(props.get('name', ''))) > 0:
            tmp_name = str(props.get('name', ''))
        f_sql = f"CONSTRAINT \"{tmp_name}\" FOREIGN KEY ({columns_names}) REFERENCES \"{ref_table_name}\"({ref_columns_names})"
        add_next = False
        if props.get('on_update', False):
            f_sql += " ON UPDATE"
            add_next = True
        elif props.get('on_delete', False):
            f_sql += " ON DELETE"
            add_next = True
        if props.get('action', None) and add_next:
            f_sql += f" {self.make_reference_action(props['action'])}"
        elif add_next:
            f_sql += " NO ACTION"

        if new_sql != "":
            f_sql = f", \n{f_sql}"
        new_sql += f_sql
        # add last ')'
        new_sql += " )"

        tmp_columns_names = str(", ").join(tmp_columns)

        # rename old table
        new_t_name = f"{table_name}_old"
        self._exec_query_or_export(f"ALTER TABLE \"{table_name}\" RENAME TO \"{new_t_name}\";")
        # create new table
        self._exec_query_or_export(new_sql)
        # insert new data
        if tmp_columns != "":
            self._exec_query_or_export(f"INSERT INTO \"{table_name}\" SELECT {tmp_columns_names} FROM \"{new_t_name}\";")
        # drop old table
        self._exec_query_or_export(f"DROP TABLE \"{new_t_name}\";")
        # append indexes
        tmp_indexes_upd = self.table_indexes(table_name)
        for index in tmp_indexes.values():
            if index['index_name'] in tmp_indexes_upd:
                continue  # skip - already added
            self.add_index(table_name, index['columns'], {'unique': index['unique']})
        # set old states
        self._db_adapter.query(f"PRAGMA defer_foreign_keys = {defer_foreign_keys};")
        self._db_adapter.query(f"PRAGMA foreign_keys = {foreign_keys};")

    def drop_foreign_key(self, table_name: str, columns: list):
        """Удалить вторичный ключ таблицы

        :param table_name: название таблицы
        :param columns: названия колонок
        """

        if table_name == "" or len(columns) == 0:
            raise Exception("[SQLiteMigrator][drop_foreign_key] Table name or columns is Empty!")
        if not self._db_adapter:
            raise Exception("[SQLiteMigrator][drop_foreign_key] Database adapter is None!")
        columns = list(set(columns))  # get uniq list
        columns = list(filter(len, columns))  # remove empty
        if len(columns) == 0:
            raise Exception("[SQLiteMigrator][drop_foreign_key] Columns is Empty!")
        # select foreign_keys
        res = self._db_adapter.query("PRAGMA foreign_keys;")
        if len(res) == 0:
            raise Exception("[SQLiteMigrator][drop_foreign_key] \"PRAGMA foreign_keys\" is Empty!")
        foreign_keys = res[0]['foreign_keys']
        # select defer_foreign_keys
        res = self._db_adapter.query("PRAGMA defer_foreign_keys;")
        if len(res) == 0:
            raise Exception("[SQLiteMigrator][drop_foreign_key] \"PRAGMA defer_foreign_keys\" is Empty!")
        defer_foreign_keys = res[0]['defer_foreign_keys']
        # set new states
        self._db_adapter.query("PRAGMA defer_foreign_keys = ON;")
        self._db_adapter.query("PRAGMA foreign_keys = OFF;")
        # select indexes
        tmp_indexes = self.table_indexes(table_name)
        # select columns
        tmp_columns = self.table_columns(table_name)
        # select f-keys list
        tmp_foreign_keys_lst = self.table_foreign_keys(table_name)
        columns_names = str(", ").join(columns)
        tmp_name = ""
        for fk in tmp_foreign_keys_lst.values():
            if fk['column'] == columns_names:
                tmp_name = fk['name']
                break
        if tmp_name == "":
            raise Exception(
                f"[SQLiteMigrator][drop_foreign_key] Not found foreign key for columns \"{columns_names}\"!")
        # select table information
        res = self._db_adapter.query(f"SELECT sql FROM sqlite_master WHERE name = \"{table_name}\";")
        if len(res) == 0:
            raise Exception(
                f"[SQLiteMigrator][drop_foreign_key] SQL data in sqlite_master fot table \"{table_name}\" is Empty!")
        sql = str(res[0]['sql'])
        pos = sql.find(f"CONSTRAINT \"{tmp_name}\" FOREIGN KEY")
        if pos == -1:
            raise Exception(
                f"[SQLiteMigrator][drop_foreign_key] Not found foreign key section in SQL data fot table \"{table_name}\"!")
        new_sql = ""
        new_sql_part = ""
        use_skip = False
        for i in range(len(sql)):
            tmp_char = sql[i]
            if tmp_char == ',':
                if not use_skip:
                    new_sql_part = new_sql_part.strip()
                    if len(new_sql) == 0 and len(new_sql_part) > 0:
                        new_sql = str(new_sql_part)
                    elif len(new_sql) > 0 and len(new_sql_part) > 0:
                        new_sql += f",\n{str(new_sql_part)}"
                else:
                    use_skip = False

                new_sql_part = ""
                continue

            new_sql_part += str(tmp_char)
            if i == pos:
                use_skip = True

        if not use_skip:
            new_sql_part = new_sql_part.strip()
            if len(new_sql) == 0 and len(new_sql_part) > 0:
                new_sql = str(new_sql_part)
            elif len(new_sql) > 0 and len(new_sql_part) > 0:
                new_sql += f",\n{str(new_sql_part)}"

        # remove last ';'
        new_sql = str(new_sql).strip()
        if new_sql[len(new_sql) - 1] == ';':
            new_sql = str(new_sql[0:(len(new_sql) - 1)]).strip()
        # add last ')'
        new_sql += " )"

        tmp_columns_names = str(', ').join(tmp_columns)

        # rename old table
        new_t_name = f"{table_name}_old"
        self._exec_query_or_export(f"ALTER TABLE \"{table_name}\" RENAME TO \"{new_t_name}\";")
        # create new table
        self._exec_query_or_export(new_sql)
        # insert new data
        if tmp_columns != "":
            self._exec_query_or_export(f"INSERT INTO \"{table_name}\" SELECT {tmp_columns_names} FROM \"{new_t_name}\";")
        # drop old table
        self._exec_query_or_export(f"DROP TABLE \"{new_t_name}\";")
        # append indexes
        tmp_indexes_upd = self.table_indexes(table_name)
        for index in tmp_indexes.values():
            if index['index_name'] in tmp_indexes_upd:
                continue  # skip - already added
            self.add_index(table_name, index['columns'], {'unique': index['unique']})
        # set old states
        self._db_adapter.query(f"PRAGMA defer_foreign_keys = {defer_foreign_keys};")
        self._db_adapter.query(f"PRAGMA foreign_keys = {foreign_keys};")

    def to_database_type(self, name: str, limit: int = None) -> str:
        """Преобразование типа колонки в тип базы данных

        :param name: имя типа
        :type name: str
        :param limit: размер данных
        :type limit: int
        :rtype: str
        """

        if name == 'integer':
            name = 'int'
        return super().to_database_type(name, limit)

    def make_default_value(self, def_value: str, value_type: str) -> str:
        """Создать SQL подстроку с базовым значением

        :param def_value: базовое значение
        :type def_value: str
        :param value_type: тип данных колонки
        :type value_type: str
        :rtype: str
        """

        if value_type.find("text") != -1 or value_type.find("varchar") != -1 or value_type.find("character varying") != -1:
            return f"DEFAULT \"{def_value}\""
        return f"DEFAULT {def_value}"

    def _drop_index_protected(self, args: dict):
        """Удалить индекс у таблицы

        :param args: аргументы

        Supported Props:
          - [string] table      - имя таблицы
          - [list]   columns    - список имен колонок
          - [string] name       - имя индекса (необязательное)
          - [bool] if_exists - добавить флаг 'IF EXISTS' (может не поддерживаться) (default: False)
          - [bool] cascade   - добавить флаг 'CASCADE' (может не поддерживаться) (default: False)

        NOTE: Должен быть задан хотябы один!
        NOTE: Приоритет отдается name!
        """

        if not self._db_adapter:
            raise Exception("[SQLiteMigrator][_drop_index_protected] Database adapter is None!")
        if len(args.keys()) == 0:
            raise Exception("[SQLiteMigrator][_drop_index_protected] Args is Empty!")
        if not 'table' in args:
            raise Exception("[SQLiteMigrator][_drop_index_protected] Not found 'table' in args!")
        if not 'columns' in args and not 'name' in args:
            raise Exception("[SQLiteMigrator][_drop_index_protected] Not found 'columns' and 'name' in args!")
        tmp_name = ""
        if 'columns' in args:
            tmp_columns = list(set(args['columns']))  # get uniq list
            tmp_columns = list(filter(len, tmp_columns))  # remove empty
            if tmp_columns and len(tmp_columns) == 0:
                raise Exception("[SQLiteMigrator][_drop_index_protected] Empty 'columns' in args!")
            tmp_columns_names = str("_").join(tmp_columns)
            table_lst = str(args['table']).split('.')
            tmp_name = f"{table_lst[len(table_lst) - 1]}_{tmp_columns_names}_index"
        if 'name' in args:
            tmp_name = args['name']
        self._exec_query_or_export(f"DROP INDEX \"{tmp_name}\"")

    def __prepare_default(self, default):
        """Получить значение секции default без кавычек

        :param default:
        :return:
        """

        if not default:
            return None
        default = str(default)
        if len(default) == 0:
            return None
        if default[0] == "\"":
            if len(default) > 1:
                default = self.__prepare_default(str(default[1:len(default)]))
            else:
                default = ""
        elif default[len(default) - 1] == "\"":
            if len(default) > 1:
                default = self.__prepare_default(str(default[0:len(default) - 1]))
            else:
                default = ""
        return default
