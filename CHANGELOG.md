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
