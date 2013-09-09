FILES=\
	getSystemInfo \
	setSystemInfo \
	set_systeminfo \
	get_systeminfo \
	settings
all:
	@if [ ! "$$GLOBALROOT" ]; then  echo "GLOBALROOT variable is not set."; exit 1; fi 
	@for file in $(FILES); do echo $$file; svn export --force $$file $$GLOBALROOT/server/files/system_scripts/$$file; done
	@echo "To effectively check in this latest version, please execute:"
	@echo "   svn add --depth infinity $$GLOBALROOT/server/files/system_scripts"
	@echo "   svn commit $$GLOBALROOT/server/files/system_scripts"
