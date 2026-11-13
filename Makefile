.PHONY: help test lint themes

help:
	@echo "make test     run the install and launcher tests, and check the theme exports"
	@echo "make lint     run shellcheck on every script"
	@echo "make themes   regenerate every theme export from the house-style token file"

test:
	@sh tests/run.sh
	@uv run --no-project tools/themes/build.py --check
	@uv run --no-project --with pytest pytest -q -p no:cacheprovider tools/themes

themes:
	@uv run --no-project tools/themes/build.py

lint:
	@shellcheck setup.sh bin/eww bin/eww-install bin/eww-update bin/eww-doctor bin/eww-h bin/eww-context hooks/pre-commit tests/run.sh
	@zsh -n home/.config/eww/eww.zsh
