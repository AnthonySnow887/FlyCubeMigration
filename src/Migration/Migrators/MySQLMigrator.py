import re
from _thread import exit

from src.Migration.Migrators.BaseMigrator import BaseMigrator


class MySQLMigrator(BaseMigrator):
    def __init__(self, db_adapter, export_file: str = None):
        super().__init__(db_adapter, export_file)

    def create_database(self, name: str, props: dict = {}):
        """Создать новую базу данных

        :param name: название базы данных
        :type name: str
        :param props: свойства
        :type props: dict

        Supported Props:
          - [string] collation       - Set flag 'COLLATE'
          - [string] charset         - Set flag 'CHARACTER'
        """

        if name == "":
            raise Exception("[MySQLMigrator][create_database] Database name is Empty!")
        if not self._db_adapter:
            raise Exception("[MySQLMigrator][create_database] Database adapter is None!")
        str_option = ""
        if str(props.get('collation', '')) != "":
            str_option = f"DEFAULT COLLATE '{str(props.get('collation', ''))}'"
        elif str(props.get('charset', '')) != "":
            str_option = f"DEFAULT CHARACTER SET '{str(props.get('charset', ''))}'"
        else:
            str_option = f"DEFAULT CHARACTER SET utf8"
        self._exec_query_or_export(f"CREATE DATABASE `{name}` {str_option};")

    def drop_database(self, name: str):
        """Удалить базу данных

        :param name: название базы данных
        :type name: str
        """

        if name == "":
            raise Exception("[MySQLMigrator][drop_database] Database name is Empty!")
        if not self._db_adapter:
            raise Exception("[MySQLMigrator][drop_database] Database adapter is None!")
        self._exec_query_or_export(f"DROP DATABASE IF EXISTS `{name}`;")

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
        db_name = self._db_adapter.database()
        sql = f"SHOW INDEX FROM {self._db_adapter.quote_table_name(table_name)} FROM {self._db_adapter.quote_table_name(db_name)};"
        res = self._db_adapter.query(sql)
        if len(res) == 0:
            return {}
        tmp_indexes = {}
        for r in res:
            i_name = r['Key_name']
            unique = not bool(r['Non_unique'])
            i_columns = []
            if i_name in tmp_indexes:
                i_columns = tmp_indexes[i_name]['columns']
            i_columns.append(r['Column_name'])

            tmp_indexes[i_name] = {
                'index_name': i_name,
                'unique': unique,
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
        sql = f"SHOW COLUMNS FROM {self._db_adapter.quote_table_name(table_name)};"
        res = self._db_adapter.query(sql)
        if len(res) == 0:
            return {}
        tmp_columns = {}
        for r in res:
            is_not_null = False
            if str(r['Null']).lower() == 'no':
                is_not_null = True
            is_p_key = False
            if str(r['Key']).lower() == 'pri':
                is_p_key = True

            tmp_columns[r['Field']] = {
                'table': table_name,
                'column': r['Field'],
                'type': r['Type'],
                'is_pk': is_p_key,
                'is_not_null': is_not_null,
                'default': r['Default']
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
        # select table information
        sql = f"SHOW KEYS FROM {self._db_adapter.quote_table_name(table_name)} WHERE Key_name = 'PRIMARY';"
        res = self._db_adapter.query(sql)
        if len(res) == 0:
            return {}
        tmp_list = {}
        for r in res:
            t_columns = self.table_columns(table_name)
            if not r['Column_name'] in t_columns:
                continue
            tmp_list[r['Key_name']] = {
                'name': r['Key_name'],
                'table': table_name,
                'column': r['Column_name'],
                'type': t_columns[r['Column_name']]['type']
            }
        return tmp_list

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
        # select table information
        db_name = self._db_adapter.database()
        sql = f"""
        SELECT fk.referenced_table_name AS 'to_table',
               fk.referenced_column_name AS 'primary_key',
               fk.column_name AS 'column',
               fk.constraint_name AS 'name',
               rc.update_rule AS 'on_update',
               rc.delete_rule AS 'on_delete'
        FROM information_schema.referential_constraints rc
        JOIN information_schema.key_column_usage fk
        USING (constraint_schema, constraint_name)
        WHERE fk.referenced_column_name IS NOT NULL
        AND fk.table_schema = '{db_name}'
        AND fk.table_name = '{table_name}'
        AND rc.constraint_schema = '{db_name}'
        AND rc.table_name = '{table_name}'
        """
        res = self._db_adapter.query(sql)
        if len(res) == 0:
            return {}
        tmp_list = {}
        for r in res:
            tmp_list[r['name']] = {
                'name': r['name'],
                'table': table_name,
                'column': r['column'],
                'ref_table': r['to_table'],
                'ref_column': r['primary_key'],
                'on_update': r['on_update'],
                'on_delete': r['on_delete']
            }
        return tmp_list

    def rename_column(self, table_name: str, column_name: str, column_new_name: str):
        """Переименовать колонку в таблице

        :param table_name: название таблицы
        :param column_name: название колонки
        :param column_new_name: новое название колонки
        """

        if table_name == "" or column_name == "" or column_new_name == "":
            raise Exception("[MySQLMigrator][rename_column] Table name or column name or column new name is Empty!")
        if column_name == column_new_name:
            raise Exception("[MySQLMigrator][rename_column] Column name is the same as new column name!")
        if not self._db_adapter:
            raise Exception("[MySQLMigrator][rename_column] Database adapter is None!")
        tmp_indexes = self.table_indexes(table_name)
        tmp_columns = self.table_columns(table_name)
        if not column_name in tmp_columns:
            raise Exception(f"[MySQLMigrator][rename_column] Not found column \"{column_name}\" in table \"{table_name}\"!")

        tmp_table_name = self._db_adapter.quote_table_name(table_name)
        tmp_column_name = self._db_adapter.quote_table_name(column_name)
        tmp_column_new_name = self._db_adapter.quote_table_name(column_new_name)
        col_type = tmp_columns[column_name]['type']
        col_is_not_null = ""
        if tmp_columns[column_name]['is_not_null']:
            col_is_not_null = "NOT NULL"
        col_default = ""
        if tmp_columns[column_name]['default']:
            col_default = self.make_default_value(str(tmp_columns[column_name]['default']), col_type)

        self._exec_query_or_export(f"ALTER TABLE {tmp_table_name} CHANGE {tmp_column_name} {tmp_column_new_name} {col_type} {col_is_not_null} {col_default};")
        for k, v in tmp_indexes.items():
            if not column_name in v['columns']:
                continue
            index_new_name = f"{table_name}_{column_name}_index"
            self.rename_index(table_name, str(v['index_name']), index_new_name)

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
            raise Exception("[MySQLMigrator][change_column] Table name or column name or new type is Empty!")
        if not self._db_adapter:
            raise Exception("[MySQLMigrator][change_column] Database adapter is None!")
        table_name = self._db_adapter.quote_table_name(table_name)
        # drop default
        sql = f"ALTER TABLE {table_name} ALTER COLUMN {self._db_adapter.quote_table_name(column_name)} DROP DEFAULT;"
        self._exec_query_or_export(sql)
        # change type
        tmp_limit = props.get('limit', None)
        if tmp_limit:
            tmp_limit = int(tmp_limit)
        tmp_type = self.to_database_type(new_type, tmp_limit)
        tmp_type_using = str(tmp_type)
        col_is_not_null = ""
        if props.get('null', False):
            col_is_not_null = "NOT NULL"
        col_default = ""
        if props.get('default', None):
            col_default = self.make_default_value(str(props['default']), tmp_type)

        sql = f"ALTER TABLE {table_name} MODIFY {self._db_adapter.quote_table_name(column_name)} {tmp_type} {col_is_not_null} {col_default};"
        self._exec_query_or_export(sql)

    def change_column_null(self, table_name: str, column_name: str, not_null: bool = False):
        """Добавить/Удалить секцию NOT NULL у колонки

        :param table_name: название таблицы
        :param column_name: название колонки
        :param not_null: значение секции (если False - секция NOT NULL удаляется)
        """

        if table_name == "" or column_name == "":
            raise Exception("[MySQLMigrator][change_column_null] Table name or column name is Empty!")
        if not self._db_adapter:
            raise Exception("[MySQLMigrator][change_column_null] Database adapter is None!")
        tmp_columns = self.table_columns(table_name)
        if not column_name in tmp_columns:
            raise Exception(f"[MySQLMigrator][change_column_null] Not found column \"{column_name}\" in table \"{table_name}\"!")

        table_name = self._db_adapter.quote_table_name(table_name)
        col_type = tmp_columns[column_name]['type']
        col_is_not_null = ""
        if not_null:
            col_is_not_null = "NOT NULL"
        col_default = ""
        if tmp_columns[column_name]['default']:
            col_default = self.make_default_value(str(tmp_columns[column_name]['default']), col_type)

        self._exec_query_or_export(f"ALTER TABLE {table_name} MODIFY {self._db_adapter.quote_table_name(column_name)} {col_type} {col_is_not_null} {col_default};")

    def rename_index(self, table_name: str, old_name: str, new_name: str):
        """Переименовать индекс для таблицы

        :param table_name: название таблицы
        :param old_name: старое название
        :param new_name: новое название
        """

        if table_name == "" or old_name == "" or new_name == "":
            raise Exception("[MySQLMigrator][rename_index] Table name or old name or new name is Empty!")
        if not self._db_adapter:
            raise Exception("[MySQLMigrator][rename_index] Database adapter is None!")
        if old_name == new_name:
            raise Exception("[MySQLMigrator][rename_index] Old name is the same as new name!")
        t_indexes = self.table_indexes(table_name)
        if not old_name in t_indexes:
            raise Exception(f"[MySQLMigrator][rename_index] Not found old index name \"{old_name}\" for table \"{table_name}\"!")
        self.drop_index(table_name, {'name': old_name})
        self.add_index(table_name, t_indexes[old_name]['columns'], {'name': new_name, 'unique': t_indexes[old_name]['unique']})

    def drop_foreign_key(self, table_name: str, columns: list):
        """Удалить вторичный ключ таблицы

        :param table_name: название таблицы
        :param columns: названия колонок
        """

        if table_name == "" or len(columns) == 0:
            raise Exception("[MySQLMigrator][drop_foreign_key] Table name or columns is Empty!")
        if not self._db_adapter:
            raise Exception("[MySQLMigrator][drop_foreign_key] Database adapter is None!")
        columns = list(set(columns))  # get uniq list
        columns = list(filter(len, columns))  # remove empty
        if len(columns) == 0:
            raise Exception("[MySQLMigrator][drop_foreign_key] Columns is Empty!")
        # select f-keys list
        columns_names = str(", ").join(columns)
        tmp_name = ""
        tmp_f_key_dict = self.table_foreign_keys(table_name)
        for fk in tmp_f_key_dict.values():
            if fk['column'] == columns_names:
                tmp_name = fk['name']
                break
        if tmp_name == "":
            raise Exception(f"[MySQLMigrator][drop_foreign_key] Not found foreign key for columns \"{columns_names}\"!")
        self._exec_query_or_export(f"ALTER TABLE {self._db_adapter.quote_table_name(table_name)} DROP CONSTRAINT {self._db_adapter.quote_table_name(tmp_name)};")
        self.drop_index(table_name, {'name': tmp_name, 'if_exists': True})

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
            raise Exception("[MySQLMigrator][_drop_index_protected] Database adapter is None!")
        if len(args.keys()) == 0:
            raise Exception("[MySQLMigrator][_drop_index_protected] Args is Empty!")
        if not 'table' in args:
            raise Exception("[MySQLMigrator][_drop_index_protected] Not found 'table' in args!")
        if not 'columns' in args and not 'name' in args:
            raise Exception("[MySQLMigrator][_drop_index_protected] Not found 'columns' and 'name' in args!")
        tmp_name = ""
        if 'columns' in args:
            tmp_columns = list(set(args['columns']))  # get uniq list
            tmp_columns = list(filter(len, tmp_columns))  # remove empty
            if tmp_columns and len(tmp_columns) == 0:
                raise Exception("[MySQLMigrator][_drop_index_protected] Empty 'columns' in args!")
            tmp_columns_names = str("_").join(tmp_columns)
            table_lst = str(args['table']).split('.')
            tmp_name = f"{table_lst[len(table_lst) - 1]}_{tmp_columns_names}_index"
        if 'name' in args:
            tmp_name = args['name']

        if args.get('if_exists', False):
            t_indexes = self.table_indexes(str(args['table']))
            if not tmp_name in t_indexes:
                return  # not found -> ok -> exit

        self._exec_query_or_export(f"DROP INDEX {self._db_adapter.quote_table_name(tmp_name)} ON {self._db_adapter.quote_table_name(args['table'])};")
