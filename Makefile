lint:
	poetry run yapf --in-place --parallel --recursive .
	poetry run isort -rc bubblegum
	poetry run flake8
tests:
	poetry run pytest
	poetry run yapf --parallel --diff --recursive bubblegum
	poetry run isort -rc -c bubblegum
	poetry run flake8
.PHONY: lint tests
