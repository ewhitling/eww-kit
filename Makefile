.PHONY: help test lint

help:
	@echo "make test   run the install and launcher tests in a temporary home folder"
	@echo "make lint   run shellcheck on every script"

test:
	@sh tests/run.sh

lint:
	@shellcheck setup.sh bin/eww bin/eww-install bin/eww-update bin/eww-doctor hooks/pre-commit tests/run.sh
