#!/bin/bash

#
# URL:      https://github.com/AnthonySnow887/FlyCubeMigration
# AUTHOR:   AnthonySnow887
# VERSION:  1.2.0
# LICENSE:  GPL-3.0
#
# NOTE: This file is part of the FlyCubeMigration (database migration system) helper tools.
#       This version of the file only supports work with the PostgreSQL DBMS.
#

#
# Function for show help
#
# Input args:
# 1 - current app
#
function show_help() {
    local app=$1

    printf "\nHelp:"
    printf "\n  -d,  --dir          - set sql migrations directory"
    printf "\n  -tv, --to-version   - set max sql migration version (default: None)"
    printf "\n  -dh, --dbhost       - set database host address"
    printf "\n  -db, --dbname       - set database name"
    printf "\n  -u,  --username     - set user name for connect to database"
    printf "\n  -p,  --password     - set user password for connect to database"
    printf "\n"
    printf "\nExample usage:"
    printf "\n"
    printf "\n  #> sh $app --dir export/primary/ -db test -u postgres -p 12345678"
    printf "\n"
    printf "\n  or"
    printf "\n"
    printf "\n  #> sh $app -d export/primary/ -tv 20250714155400 -db test -u postgres -p 12345678"
    printf "\n\n"
}

#
# Function for get current db version
# Input args:
# 1 - db host
# 2 - db name
# 3 - db user
#
function get_current_db_version() {
    local host=$1
    local name=$2
    local user=$3
    local cur_db_version=`psql $host -d $name -U $user -c "SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 1;" | grep -oP "\d\d\d\d\d\d\d\d\d\d\d\d\d\d"`
    echo "$cur_db_version"
}

#
# Function for install migration
# Input args:
# 1 - db host
# 2 - db name
# 3 - db user
# 4 - sql file path
# 5 - migration version
#
function install_migration() {
    local host=$1
    local name=$2
    local user=$3
    local file=$4
    local version=$5
    if [ -f psql_stderr.txt ]
    then
        rm psql_stderr.txt
    fi
    psql $host -d $name -U $user -v "ON_ERROR_STOP=1" -f $file &> psql_stderr.txt
    result_code=$?
    if [ "$result_code" -eq "0" ]
    then
        psql $host -d $name -U $user -c "INSERT INTO schema_migrations (version) VALUES ('$version');" &> /dev/null
    fi
    echo "$result_code"
}

#
# main
#

MAX_INT=9223372036854775807

dir=""
to_version=$MAX_INT
db_host=""
db_name=""
db_user=""
db_pass=""

is_dir=false
is_to_version=false
is_db_host=false
is_db=false
is_db_user=false
is_db_pass=false
for var in "$@"
do
    if [ $is_dir == true ]
    then
        dir=$var
        is_dir=false
    elif [ $is_to_version == true ]
    then
        to_version=$var
        is_to_version=false
    elif [ $is_db_host == true ]
    then
        db_host=$var
        is_db_host=false
    elif [ $is_db == true ]
    then
        db_name=$var
        is_db=false
    elif [ $is_db_user == true ]
    then
        db_user=$var
        is_db_user=false
    elif [ $is_db_pass == true ]
    then
        db_pass=$var
        is_db_pass=false
    elif [ "$var" == "--dir" ] || [ "$var" == "-d" ]
    then
        is_dir=true
    elif [ "$var" == "--to-version" ] || [ "$var" == "-tv" ]
    then
        is_to_version=true
    elif [ "$var" == "--dbhost" ] || [ "$var" == "-dh" ]
    then
        is_db_host=true
    elif [ "$var" == "--dbname" ] || [ "$var" == "-db" ]
    then
        is_db=true
    elif [ "$var" == "--username" ] || [ "$var" == "-u" ]
    then
        is_db_user=true
    elif [ "$var" == "--password" ] || [ "$var" == "-p" ]
    then
        is_db_pass=true
    elif [ "$var" == "--help" ] || [ "$var" == "-h" ] || [ "$var" == "-?" ]
    then
        show_help "$0"
        exit 0;
    fi
done

# Check migrations directory
if [ "$dir" == "" ]
then
    printf "\nNot set sql migrations directory! See help (--help)!"
    printf "\n\n"
    exit 1;
fi

if [ ! -d "$dir" ]
then
    printf "\nInvalid sql migrations directory!"
    printf "\n\n"
    exit 1;
fi

# Check migration files
num_migrations=`ls -l $dir | grep ".sql$" | wc -l`
if [ $num_migrations -eq 0 ]
then
    printf "\nNot found sql migrations in directory!"
    printf "\n\n"
    exit 1;
fi

# Check database name
if [ "$db_name" == "" ]
then
    printf "\nNot set database name! See help (--help)!"
    printf "\n\n"
    exit 1;
fi

# Check database user
if [ "$db_user" == "" ]
then
    printf "\nNot set database user! See help (--help)!"
    printf "\n\n"
    exit 1;
fi

pwd=`pwd`
cd $dir

# Check database host
db_host_arg=""
if [[ -n "$db_host" ]]
then
    db_host_arg="-h $db_host"
fi

# Check database password and export
if [[ -n "$db_pass" ]]
then
    export PGPASSWORD=$db_pass
fi

# get current database version
current_db_version="$(get_current_db_version "$db_host_arg" "$db_name" "$db_user")"
printf "\nCurrent database version: $current_db_version"

# install migrations
for i in `ls *.sql | sort -n -t _ -k 1`
do
    m_number=`echo $i | grep -oP "\d\d\d\d\d\d\d\d\d\d\d\d\d\d"`
    if [ $m_number -gt $to_version ]
    then
        break
    fi
    if [ $current_db_version -gt $m_number ]
    then
        continue
    fi
    if [ $current_db_version -eq $m_number ]
    then
        continue
    fi

    printf "\n[Up] $i"
    result_code="$(install_migration "$db_host_arg" "$db_name" "$db_user" "./$i" "$m_number")"
    if [ $result_code -ne 0 ]
    then
        printf "\n\nMigrate failed! Error:\n\n"
        cat psql_stderr.txt
        break
    fi
done

# remove psql_stderr.txt file if exist
if [ -f psql_stderr.txt ]
then
    rm psql_stderr.txt
fi

# get current database version
current_db_version="$(get_current_db_version "$db_host_arg" "$db_name" "$db_user")"
printf "\nMigrate finished"
printf "\nNew database version: $current_db_version\n\n"

# Check database password and unset
if [[ -n "$db_pass" ]]
then
    unset PGPASSWORD
fi
