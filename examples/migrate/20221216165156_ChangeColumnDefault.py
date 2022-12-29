
#
# Created by FlyCubeMigration generator.
# User: anton
# Date: 16.12.2022
# Time: 16:51
#

from src.Migration.BaseMigration import BaseMigration


class ChangeColumnDefault(BaseMigration):
    #
    # NOTE: Uncomment if needed configure migration.
    #
    # def configuration(self):
    #     # Set here your code for configuration migration
    #     return

    def up(self):
        self.change_column_default('test_schema.test_table_renamed', 'my_new_column_renamed', '???')

    def down(self):
        self.change_column_default('test_schema.test_table_renamed', 'my_new_column_renamed', '---???---')

        