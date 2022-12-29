
#
# Created by FlyCubeMigration generator.
# User: anton
# Date: 16.12.2022
# Time: 17:05
#

from src.Migration.BaseMigration import BaseMigration


class RenameIndex(BaseMigration):
    #
    # NOTE: Uncomment if needed configure migration.
    #
    # def configuration(self):
    #     # Set here your code for configuration migration
    #     return

    def up(self):
        self.rename_index('test_schema.test_table_2', 'my_test_index', 'my_test_index_renamed')

    def down(self):
        self.rename_index('test_schema.test_table_2', 'my_test_index_renamed', 'my_test_index')

        