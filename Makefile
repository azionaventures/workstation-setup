.PHONY: help

help: ## helper
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

.DEFAULT_GOAL := help

## - Setup completo:
##   make setup		
setup:
	chmod -R +x scripts setup.py && ./setup.py

##
## - Installazione delle dipendenze:
##   make update-depends		
update-depends:
	git pull && ./setup.py --only-depends 

##
## - Installazione/Aggiornamento scripts aziona:
##   make update-scripts		
update-scripts:
	git pull && ./setup.py --only-scripts 