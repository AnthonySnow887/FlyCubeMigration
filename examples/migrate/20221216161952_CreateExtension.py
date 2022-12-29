
#
# Created by FlyCubeMigration generator.
# User: anton
# Date: 16.12.2022
# Time: 16:19
#

from src.Migration.BaseMigration import BaseMigration


class CreateExtension(BaseMigration):
    #
    # NOTE: Uncomment if needed configure migration.
    #
    # def configuration(self):
    #     # Set here your code for configuration migration
    #     return

    def up(self):
        self.create_extension('uuid-ossp')

    def down(self):
        self.drop_extension('uuid-ossp')

        