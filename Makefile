.PHONY: help test lint themes obsidian-snapshot

help:
	@echo "make test     run the install and launcher tests, and check the theme exports"
	@echo "make lint     run shellcheck on every script"
	@echo "make themes   regenerate every theme export from the house-style token file"
	@echo "make obsidian-snapshot   copy this vault's Obsidian settings into obsidian/defaults"

test:
	@sh tests/run.sh
	@uv run --no-project tools/themes/build.py --check
	@uv run --no-project --with pytest pytest -q -p no:cacheprovider tools/themes tools/obsidian tests/test_daily.py tests/test_define.py tests/test_weekly.py

themes:
	@uv run --no-project tools/themes/build.py

lint:
	@shellcheck setup.sh bin/eww bin/eww-install bin/eww-update bin/eww-doctor bin/eww-h bin/eww-context hooks/pre-commit tests/run.sh
	@zsh -n home/.config/eww/eww.zsh

obsidian-snapshot:
	@uv run --no-project tools/obsidian/snapshot.py
