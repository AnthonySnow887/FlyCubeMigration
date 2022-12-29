
#
# Created by FlyCubeMigration generator.
# User: anton
# Date: 16.12.2022
# Time: 16:31
#

from src.Migration.BaseMigration import BaseMigration


class RenameTable(BaseMigration):
    #
    # NOTE: Uncomment if needed configure migration.
    #
    # def configuration(self):
    #     # Set here your code for configuration migration
    #     return

    def up(self):
        self.rename_table('test_schema.test_table', 'test_schema.test_table_renamed')

    def down(self):
        self.rename_table('test_schema.test_table_renamed', 'test_schema.test_table')

        