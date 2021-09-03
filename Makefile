.PHONY: help

help: ## helper
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

.DEFAULT_GOAL := help

## - Setup completo:
##   make setup		
setup:
	chmod +x -R scripts setup.py && ./setup.py

##
## - Installazione delle dipendenze:
##   make update-depends		
update-depends:
	git pull && ./setup.sh --only-depends 

##
## - Installazione/Aggiornamento scripts aziona:
##   make update-scripts		
update-scripts:
	git pull && ./setup.sh --only-scripts 