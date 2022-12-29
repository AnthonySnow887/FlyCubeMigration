
#
# Created by FlyCubeMigration generator.
# User: anton
# Date: 16.12.2022
# Time: 16:22
#

from src.Migration.BaseMigration import BaseMigration


class CreateTable(BaseMigration):
    #
    # NOTE: Uncomment if needed configure migration.
    #
    # def configuration(self):
    #     # Set here your code for configuration migration
    #     return

    def up(self):
        self.create_table('test_schema.test_table', {
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
            })

    def down(self):
        self.drop_table('test_schema.test_table')

        