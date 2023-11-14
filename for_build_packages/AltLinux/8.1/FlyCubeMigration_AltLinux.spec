%global __find_debuginfo_files %nil
%define _verify_elf_method skip
AutoReq: no
%define _unpackaged_files_terminate_build 0


Name:       fly-cube-migration
Version: 	1.1.0
Release: 	alt1
Group:      Development/Python
Packager: 	AnthonySnow887
Vendor: 	AnthonySnow887
License: 	GPLv3
URL:        https://github.com/AnthonySnow887/FlyCubeMigration
Buildroot:  %{_tmppath}/%{name}-%{version}-%{release}-root

Source0: %{name}-%{version}.tar.gz

Summary: Tool for creating, installing, reverting database migrations
Requires: python3
Requires: python3-module-psycopg2
Requires: python3-module-yaml
Requires: python3-modules-sqlite3
Requires: python3-module-urllib3
Requires: python3-module-requests
Requires: python3-module-mysql
Requires: python3-module-chardet

%description
FlyCubeMigration is a tool developed in Python that follows the ideology and principles of database migration found in Ruby on Rails.
FlyCubeMigration completely repeats the functionality of the migration core implemented in the MVC Web Framework FlyCubePHP.
Installation of each migration is performed in transactional mode and in case of errors, rolls back the state of the database to the stage before installation.

%prep
%setup -q

%install
mkdir -p %{buildroot}/usr/local/FlyCubeMigration/
cp -r config %{buildroot}/usr/local/FlyCubeMigration/
cp -r db %{buildroot}/usr/local/FlyCubeMigration/
cp -r examples %{buildroot}/usr/local/FlyCubeMigration/
cp -r src %{buildroot}/usr/local/FlyCubeMigration/
cp -r *.* %{buildroot}/usr/local/FlyCubeMigration/
install -Dm 0755 -p fly-cube-migration %{buildroot}/usr/local/FlyCubeMigration/fly-cube-migration
install -Dm 0755 -p LICENSE %{buildroot}/usr/local/FlyCubeMigration/LICENSE
exit 0

%clean
rm -rf * %{buildroot}

%post
ln -s /usr/local/FlyCubeMigration/fly-cube-migration /usr/bin/fly-cube-migration

%postun
rm -f -R /usr/local/FlyCubeMigration/
rm /usr/bin/fly-cube-migration

%files
%defattr(-,root,root, 755)
/usr/local/FlyCubeMigration/


