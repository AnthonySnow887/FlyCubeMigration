UPGRADE FROM 1.0.0/1.0.1/1.0.2 to 1.1.0
=======================================

Global FlyCubeMigration config ```fly-cube-migration.yml```
-----------------------------------------------------------

 * The key ```FLY_CUBE_MIGRATION_DB_CONFIG_DIR``` has been renamed to ```FLY_CUBE_MIGRATION_CONFIG_DIR```
 
 Before:
 ```yaml
 #
 # Directory for database config file 'database.yml'
 #
 FLY_CUBE_MIGRATION_DB_CONFIG_DIR: "config/"
 ```
 
 After:
 ```yaml
 #
 # Directory for config files: 'fly-cube-migration.yml', 'database.yml' and 'post-scripts.yml'
 #
 FLY_CUBE_MIGRATION_CONFIG_DIR: "config/"
 ```
 