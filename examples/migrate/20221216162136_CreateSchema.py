
#
# Created by FlyCubeMigration generator.
# User: anton
# Date: 16.12.2022
# Time: 16:21
#

from src.Migration.BaseMigration import BaseMigration


class CreateSchema(BaseMigration):
    #
    # NOTE: Uncomment if needed configure migration.
    #
    # def configuration(self):
    #     # Set here your code for configuration migration
    #     return

    def up(self):
        self.create_schema('test_schema')

    def down(self):
        self.drop_schema('test_schema')

        