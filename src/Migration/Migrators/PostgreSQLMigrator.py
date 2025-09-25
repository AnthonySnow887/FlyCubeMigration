import re
from src.Migration.Migrators.BaseMigrator import BaseMigrator


class PostgreSQLMigrator(BaseMigrator):
    def __init__(self, db_adapter, export_file: str = None):
        super().__init__(db_adapter, export_file)

    def create_database(self, name: str, props: dict = {}):
        """Создать новую базу данных

        :param name: название базы данных
        :type name: str
        :param props: свойства
        :type props: dict

        Supported Props:
          - [string] encoding        - Set flag 'ENCODING' (default: utf8)
          - [string] owner           - Set flag 'OWNER'
          - [string] template        - Set flag 'TEMPLATE'
          - [string] collation       - Set flag 'LC_COLLATE'
          - [string] ctype           - Set flag 'LC_CTYPE'
          - [string] tablespace      - Set flag 'TABLESPACE'
          - [int] connection_limit   - Set flag 'CONNECTION LIMIT'
        """

        if name == "":
            raise Exception("[PostgreSQLMigrator][create_database] Database name is Empty!")
        if not self._db_adapter:
            raise Exception("[PostgreSQLMigrator][create_database] Database adapter is None!")
        if not 'encoding' in props:
            props['encoding'] = 'utf8'
        str_option = ""
        if str(props.get('owner', '')) != "":
            str_option += f" OWNER = \"{str(props.get('owner', ''))}\""
        if str(props.get('template', '')) != "":
            str_option += f" TEMPLATE = \"{str(props.get('template', ''))}\""
        if str(props.get('encoding', '')) != "":
            str_option += f" ENCODING = '{str(props.get('encoding', ''))}'"
        if str(props.get('collation', '')) != "":
            str_option += f" LC_COLLATE = '{str(props.get('collation', ''))}'"
        if str(props.get('ctype', '')) != "":
            str_option += f" LC_CTYPE = '{str(props.get('ctype', ''))}'"
        if str(props.get('tablespace', '')) != "":
            str_option += f" TABLESPACE = \"{str(props.get('tablespace', ''))}\""
        if str(props.get('connection_limit', '')) != "":
            str_option += f" CONNECTION LIMIT = {str(int(props.get('connection_limit', 0)))}"
        self._exec_query_or_export(f"CREATE DATABASE \"{name}\" {str_option};")

    def drop_database(self, name: str):
        """Удалить базу данных

        :param name: название базы данных
        :type name: str
        """

        if name == "":
            raise Exception("[PostgreSQLMigrator][drop_database] Database name is Empty!")
        if not self._db_adapter:
            raise Exception("[PostgreSQLMigrator][drop_database] Database adapter is None!")
        self._exec_query_or_export(f"DROP DATABASE IF EXISTS \"{name}\";")

    def create_extension(self, name: str, props: dict = {}):
        """Подключить расширение базы данных

        :param name: название
        :type name: str
        :param props: свойства
        :type props: dict

        Supported Props:
          - [bool] if_not_exists - добавить флаг 'IF NOT EXISTS'
        """

        if name == "":
            raise Exception("[PostgreSQLMigrator][create_extension] Extension name is Empty!")
        if not self._db_adapter:
            raise Exception("[PostgreSQLMigrator][create_extension] Database adapter is None!")
        if_not_exists = ""
        if props.get('if_not_exists', False):
            if_not_exists = 'IF NOT EXISTS'
        self._exec_query_or_export(f"CREATE EXTENSION {if_not_exists} \"{name}\";")

    def drop_extension(self, name: str, props: dict = {}):
        """Удалить расширение базы данных

        :param name: название
        :type name: str
        :param props: свойства
        :type props: dict

        Supported Props:
          - [bool] if_exists - добавить флаг 'IF EXISTS'
        """

        if name == "":
            raise Exception("[PostgreSQLMigrator][drop_extension] Extension name is Empty!")
        if not self._db_adapter:
            raise Exception("[PostgreSQLMigrator][drop_extension] Database adapter is None!")
        if_exists = ""
        if props.get('if_exists', False):
            if_exists = 'IF EXISTS'
        self._exec_query_or_export(f"DROP EXTENSION {if_exists} \"{name}\" CASCADE;")

    def create_schema(self, name: str, props: dict = {}):
        """Создать новую схему данных

        :param name: название
        :type name: str
        :param props: свойства
        :type props: dict

        Supported Props:
          - [bool] if_not_exists - добавить флаг 'IF NOT EXISTS'
        """

        if name == "":
            raise Exception("[PostgreSQLMigrator][create_schema] Schema name is Empty!")
        if not self._db_adapter:
            raise Exception("[PostgreSQLMigrator][create_schema] Database adapter is None!")
        if_not_exists = ""
        if props.get('if_not_exists', False):
            if_not_exists = 'IF NOT EXISTS'
        self._exec_query_or_export(f"CREATE SCHEMA {if_not_exists} \"{name}\";")

    def drop_schema(self, name: str, props: dict = {}):
        """Удалить схему данных

        :param name: название
        :type name: str
        :param props: свойства
        :type props: dict

        Supported Props:
          - [bool] if_exists - добавить флаг 'IF EXISTS'
        """

        if name == "":
            raise Exception("[PostgreSQLMigrator][drop_schema] Schema name is Empty!")
        if not self._db_adapter:
            raise Exception("[PostgreSQLMigrator][drop_schema] Database adapter is None!")
        if_exists = ""
        if props.get('if_exists', False):
            if_exists = 'IF EXISTS'
        self._exec_query_or_export(f"DROP SCHEMA {if_exists} \"{name}\" CASCADE;")

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
        table_lst = table_name.split('.')
        sql = ""
        if len(table_lst) == 1:
            sql = f"SELECT indexname, indexdef FROM pg_indexes WHERE tablename = '{table_name}';"
        elif len(table_lst) == 2:
            sql = f"SELECT indexname, indexdef FROM pg_indexes WHERE schemaname = '{table_lst[0]}' AND tablename = '{table_lst[1]}';"
        else:
            raise Exception(f"[PostgreSQLMigrator][table_indexes] Invalid table name (name: \"{table_name}\")!")

        res = self._db_adapter.query(sql)
        if len(res) == 0:
            return {}
        tmp_indexes = {}
        for r in res:
            info = self.__parse_table_index(table_name, r['indexname'], r['indexdef'])
            if 'index_name' in info:
                tmp_indexes[info['index_name']] = info
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
        table_lst = table_name.split('.')
        sql = ""
        if len(table_lst) == 1:
            sql = f"""
            SELECT table_schema, table_name, column_name, column_default, is_nullable, data_type, character_maximum_length 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}';
            """
        elif len(table_lst) == 2:
            sql = f"""
            SELECT table_schema, table_name, column_name, column_default, is_nullable, data_type, character_maximum_length 
            FROM information_schema.columns 
            WHERE table_schema = '{table_lst[0]}' AND table_name = '{table_lst[1]}';
            """
        else:
            raise Exception(f"[PostgreSQLMigrator][table_columns] Invalid table name (name: \"{table_name}\")!")

        tmp_p_keys = self.table_primary_keys(table_name)
        res = self._db_adapter.query(sql)
        if len(res) == 0:
            return {}
        tmp_columns = {}
        for r in res:
            is_pk = self.__column_is_p_key(r['column_name'], tmp_p_keys)
            is_not_null = False
            if str(r['is_nullable']).lower() == 'no':
                is_not_null = True
            tmp_columns[r['column_name']] = {
                'table': f"{r['table_schema']}.{r['table_name']}",
                'column': r['column_name'],
                'type': self.to_database_type(str(r['data_type']), r['character_maximum_length']),
                'is_pk': is_pk,
                'is_not_null': is_not_null,
                'default': r['column_default']
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
        table_lst = table_name.split('.')
        sql = ""
        if len(table_lst) == 1:
            sql = f"""
            SELECT
              pg_namespace.nspname,      
              pg_class.relname,
              pg_attribute.attname, 
              format_type(pg_attribute.atttypid, pg_attribute.atttypmod) AS data_type,
              tc.constraint_name
            FROM pg_index, pg_class, pg_attribute, pg_namespace
            JOIN information_schema.table_constraints AS tc 
            ON tc.table_schema = pg_namespace.nspname
            AND tc.table_name = '{table_name}'
            AND tc.constraint_type = 'PRIMARY KEY'
            WHERE pg_class.oid = '{table_name}'::regclass
            AND indrelid = pg_class.oid 
            AND pg_class.relnamespace = pg_namespace.oid
            AND pg_attribute.attrelid = pg_class.oid 
            AND pg_attribute.attnum = any(pg_index.indkey)
            AND indisprimary
            """
        elif len(table_lst) == 2:
            sql = f"""
            SELECT
              pg_namespace.nspname,      
              pg_class.relname,
              pg_attribute.attname, 
              format_type(pg_attribute.atttypid, pg_attribute.atttypmod) AS data_type,
              tc.constraint_name
            FROM pg_index, pg_class, pg_attribute, pg_namespace
            JOIN information_schema.table_constraints AS tc 
            ON tc.table_schema = pg_namespace.nspname
            AND tc.table_schema = '{table_lst[0]}'
            AND tc.table_name = '{table_lst[1]}'
            AND tc.constraint_type = 'PRIMARY KEY'
            WHERE pg_class.oid = '{table_lst[0]}.{table_lst[1]}'::regclass
            AND indrelid = pg_class.oid 
            AND pg_class.relnamespace = pg_namespace.oid
            AND pg_attribute.attrelid = pg_class.oid 
            AND pg_attribute.attnum = any(pg_index.indkey)
            AND indisprimary
            """
        else:
            raise Exception(f"[PostgreSQLMigrator][table_primary_keys] Invalid table name (name: \"{table_name}\")!")

        res = self._db_adapter.query(sql)
        if len(res) == 0:
            return {}
        tmp_list = {}
        for r in res:
            tmp_list[r['constraint_name']] = {
                'name': r['constraint_name'],
                'table': f"{r['nspname']}.{r['relname']}",
                'column': r['attname'],
                'type': r['data_type']
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
        table_lst = table_name.split('.')
        sql = ""
        if len(table_lst) == 1:
            sql = f"""
            SELECT
              tc.table_schema, 
              tc.constraint_name, 
              tc.table_name, 
              kcu.column_name, 
              ccu.table_schema AS foreign_table_schema,
              ccu.table_name AS foreign_table_name,
              ccu.column_name AS foreign_column_name,
              rc.update_rule AS on_update,
              rc.delete_rule AS on_delete
            FROM 
              information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
            JOIN information_schema.referential_constraints rc
            ON tc.constraint_catalog = rc.constraint_catalog
            AND tc.constraint_schema = rc.constraint_schema
            AND tc.constraint_name = rc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = '{table_name}';
            """
        elif len(table_lst) == 2:
            sql = f"""
            SELECT
              tc.table_schema, 
              tc.constraint_name, 
              tc.table_name, 
              kcu.column_name, 
              ccu.table_schema AS foreign_table_schema,
              ccu.table_name AS foreign_table_name,
              ccu.column_name AS foreign_column_name,
              rc.update_rule AS on_update,
              rc.delete_rule AS on_delete
            FROM 
              information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
            JOIN information_schema.referential_constraints rc
            ON tc.constraint_catalog = rc.constraint_catalog
            AND tc.constraint_schema = rc.constraint_schema
            AND tc.constraint_name = rc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = '{table_lst[0]}' AND tc.table_name = '{table_lst[1]}';
            """
        else:
            raise Exception(f"[PostgreSQLMigrator][table_foreign_keys] Invalid table name (name: \"{table_name}\")!")

        res = self._db_adapter.query(sql)
        if len(res) == 0:
            return {}
        tmp_list = {}
        for r in res:
            tmp_list[r['constraint_name']] = {
                'name': r['constraint_name'],
                'table': f"{r['table_schema']}.{r['table_name']}",
                'column': r['column_name'],
                'ref_table': f"{r['foreign_table_schema']}.{r['foreign_table_name']}",
                'ref_column': r['foreign_column_name'],
                'on_update': r['on_update'],
                'on_delete': r['on_delete']
            }
        return tmp_list

    def to_database_type(self, name: str, limit: int = None) -> str:
        """Преобразование типа колонки в тип базы данных

        :param name: имя типа
        :type name: str
        :param limit: размер данных
        :type limit: int
        :rtype: str
        """

        name = name.replace('unsigned', '')
        name = name.replace('UNSIGNED', '')
        name = name.strip()
        if name == 'string':
            if limit:
                return f"varchar ({limit})"
            else:
                return "text"
        if limit and name != 'text':
            return f"{name} ({limit})"
        return name

    def rename_table(self, name: str, new_name: str):
        """Переименовать таблицу

        :param name: имя
        :param new_name: новое имя
        :return:
        """

        if name == "" or new_name == "":
            raise Exception("[PostgreSQLMigrator][rename_table] Table name or new table name is Empty!")
        if not self._db_adapter:
            raise Exception("[PostgreSQLMigrator][rename_table] Database adapter is None!")
        tmp_indexes = self.table_indexes(name)
        tmp_name = self._db_adapter.quote_table_name(name)
        # for postgresql without scheme name
        tmp_new_name = f"\"{self.__name_without_scheme_name(new_name)}\""
        # exec query
        self._exec_query_or_export(f"ALTER TABLE {tmp_name} RENAME TO {tmp_new_name};")
        for k, v in tmp_indexes.items():
            index_new_name = str(v['index_name']).replace(name, new_name)
            if str(v['index_name']) == index_new_name:
                continue
            self.rename_index(new_name, str(v['index_name']), index_new_name)

    def rename_index(self, table_name: str, old_name: str, new_name: str):
        """Переименовать индекс для таблицы

        :param table_name: название таблицы
        :param old_name: старое название
        :param new_name: новое название
        """

        if table_name == "" or old_name == "" or new_name == "":
            raise Exception("[PostgreSQLMigrator][rename_index] Table name or old name or new name is Empty!")
        if not self._db_adapter:
            raise Exception("[PostgreSQLMigrator][rename_index] Database adapter is None!")
        if old_name == new_name:
            raise Exception("[PostgreSQLMigrator][rename_index] Old name is the same as new name!")
        # for postgresql without scheme name
        table_scheme_name = self.__scheme_name(table_name)
        old_name_scheme_name = self.__scheme_name(old_name, table_scheme_name)
        if table_scheme_name != old_name_scheme_name:
            raise Exception("[PostgreSQLMigrator][rename_index] Scheme name in old name is not equal table scheme name!")
        tmp_old_name = self._db_adapter.quote_table_name(self.__name_with_scheme_name(old_name, old_name_scheme_name))
        tmp_new_name = f"\"{self.__name_without_scheme_name(new_name)}\""
        self._exec_query_or_export(f"ALTER INDEX {tmp_old_name} RENAME TO {tmp_new_name};")

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
            raise Exception("[PostgreSQLMigrator][_drop_index_protected] Database adapter is None!")
        if len(args.keys()) == 0:
            raise Exception("[PostgreSQLMigrator][_drop_index_protected] Args is Empty!")
        if not 'table' in args:
            raise Exception("[PostgreSQLMigrator][_drop_index_protected] Not found 'table' in args!")
        if not 'columns' in args and not 'name' in args:
            raise Exception("[PostgreSQLMigrator][_drop_index_protected] Not found 'columns' and 'name' in args!")
        tmp_name = ""
        if 'columns' in args:
            tmp_columns = list(set(args['columns']))  # get uniq list
            tmp_columns = list(filter(len, tmp_columns))  # remove empty
            if tmp_columns and len(tmp_columns) == 0:
                raise Exception("[PostgreSQLMigrator][_drop_index_protected] Empty 'columns' in args!")
            tmp_columns_names = str("_").join(tmp_columns)
            table_lst = str(args['table']).split('.')
            tmp_name = f"{table_lst[len(table_lst) - 1]}_{tmp_columns_names}_index"
        if 'name' in args:
            tmp_name = args['name']

        table_scheme_name = self.__scheme_name(str(args['table']))
        tmp_name_scheme_name = self.__scheme_name(tmp_name, table_scheme_name)
        if table_scheme_name != tmp_name_scheme_name:
            raise Exception("[PostgreSQLMigrator][_drop_index_protected] Scheme name in index name is not equal table scheme name!")
        tmp_name = self._db_adapter.quote_table_name(self.__name_with_scheme_name(tmp_name, tmp_name_scheme_name))

        sql = "DROP INDEX"
        if args.get('if_exists', False):
            sql += " IF EXISTS"
        sql += f" {tmp_name}"
        if args.get('cascade', False):
            sql += " CASCADE"
        self._exec_query_or_export(f"{sql};")

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
            raise Exception("[PostgreSQLMigrator][add_foreign_key] Table name or columns is Empty!")
        if ref_table_name == "" or len(ref_columns) == 0:
            raise Exception("[PostgreSQLMigrator][add_foreign_key] Reference table name or reference columns is Empty!")
        if not self._db_adapter:
            raise Exception("[PostgreSQLMigrator][add_foreign_key] Database adapter is None!")
        columns = list(set(columns))  # get uniq list
        columns = list(filter(len, columns))  # remove empty
        if len(columns) == 0:
            raise Exception("[PostgreSQLMigrator][add_foreign_key] Columns is Empty!")
        ref_columns = list(set(ref_columns))  # get uniq list
        ref_columns = list(filter(len, ref_columns))  # remove empty
        if len(ref_columns) == 0:
            raise Exception("[PostgreSQLMigrator][add_foreign_key] Reference columns is Empty!")
        columns_names = str(", ").join(columns)
        columns_names_2 = str("_").join(columns)
        ref_columns_names = str(", ").join(ref_columns)
        tmp_name = f"fk_{self.__name_without_scheme_name(table_name)}_{columns_names_2}"
        if 'name' in props:
            tmp_name = props['name']  # TODO name to underscore?
        table_name = self._db_adapter.quote_table_name(table_name)
        ref_table_name = self._db_adapter.quote_table_name(ref_table_name)
        sql = f"ALTER TABLE {table_name} ADD CONSTRAINT {self._db_adapter.quote_table_name(tmp_name)} FOREIGN KEY ({columns_names}) REFERENCES {ref_table_name} ({ref_columns_names})"
        add_next = False
        if props.get('on_update', False):
            sql += " ON UPDATE"
            add_next = True
        elif props.get('on_delete', False):
            sql += " ON DELETE"
            add_next = True
        if props.get('action', None) and add_next:
            sql += f" {self.make_reference_action(props['action'])}"
        elif add_next:
            sql += " NO ACTION"
        self._exec_query_or_export(f"{sql};")

    def __parse_table_index(self, table_name: str, name: str, row: str) -> dict:
        """Разобрать строку SQL по созданию индекса для получения аргументов

        :param table_name: название таблицы
        :param name: название индекса
        :param row: строка SQL
        :rtype: dict
        """

        if name == "" or row == "":
            return {}
        is_unique = False
        if row.find(' UNIQUE ') != -1:
            is_unique = True
        tmp_columns = []
        reg = r'.*\(([A-Za-z0-9_,\s]+)\).*'
        result = re.search(reg, row)
        if result:
            tmp_column_lst = result.group(1).strip().split(',')
            for c in tmp_column_lst:
                tmp_columns.append(c.strip())
        return {
            'index_name': name,
            'unique': is_unique,
            'table': table_name,
            'columns': tmp_columns
        }

    def __column_is_p_key(self, column: str, p_keys: dict) -> bool:
        """Проверка, является ли колонка первичным ключом

        :param column: название колонки
        :param p_keys: массив первичных ключей
        :rtype: bool
        """

        for pk in p_keys.values():
            if column == pk['column']:
                return True
        return False

    def __scheme_name(self, name: str, scheme_name: str = None) -> str:
        name_lst = name.split('.')
        if len(name_lst) == 1:
            if not scheme_name:
                return 'public'
            return scheme_name
        return name_lst[0]

    def __name_with_scheme_name(self, name: str, scheme_name: str = None) -> str:
        name_lst = name.split('.')
        if len(name_lst) == 1:
            if not scheme_name:
                return name
            return f"{scheme_name}.{name}"
        return ".".join(name_lst)

    def __name_without_scheme_name(self, name: str) -> str:
        name_lst = name.split('.')
        if len(name_lst) == 1:
            return name
        name_lst.pop(0)
        return ".".join(name_lst)
