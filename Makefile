.PHONY: help

help: ## helper
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

.DEFAULT_GOAL := help

exec-setenv:
	python scripts/setenv.py

exec-bin:
	python scripts/bin.py

exec-dependencies:
	python scripts/dependencies.py