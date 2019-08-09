lint:
	yapf --in-place --parallel --recursive .
	isort -rc bubblegum
	flake8

tests:
	pytest
	yapf --parallel --diff --recursive bubblegum
	isort -rc -c bubblegum
	flake8

.PHONY: lint tests
