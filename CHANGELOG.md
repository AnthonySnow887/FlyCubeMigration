# 1.3.1 (20.11.2025)

 * Added command ```--re-create-dir``` to set re-create directory for export migration files (optional; default: False).

# 1.3.0 (06.11.2025)

 * Added command ```--db-settings``` to display current database connection settings.
 * Added application execution result code (1 is returned in case of errors)

# 1.2.1 (15.10.2025)

 * Fix SyntaxWarning: invalid escape sequence

# 1.2.0 (25.09.2025)

 * Added support for export migrations (install and rollback) to standard SQL files
   * Added command ```--db-migrate-export``` - export migrations for all databases (section: up)
   * Added command ```--db-rollback-export``` - export migrations for all databases (section: down)
   * Added file ```tools/migrate.sh``` - a script for installing migrations into the database
   * Added file ```tools/rollback.sh``` - a script for deleting migrations from the database
 * Minor improvements and code refactoring
 * Updated files for build RPM/DEB packages

# 1.1.0 (14.11.2023)

 * Added support for creating FlyCubeMigration projects
 * Added support for POST-scripts
 * Added command ```--make-migration-number``` for create and output new migration version number
 * Minor improvements and code refactorings
 * Updated files for build RPM/DEB packages

# 1.0.2 (26.10.2023)

 * Fix fly-cube-migration main (abspath -> realpath)
 * Added check and disable application running is root user 
 * Added files for build RPM/DEB packages

# 1.0.1 (14.06.2023)

 * Fix psycopg2 user warning
 * Fix fly-cube-migration create migration name:
   * add Helper.to_underscore 
   * fix Helper.to_camelcase (added conversion first to underscore and then to camelcase)
 * Fix requirements.txt

# 1.0.0 (29.12.2022)

 * Release first version.
