SRC = twc
DOCS = docs

.PHONY: docs

all: format lint build docs

format:
	poetry run black $(SRC)

lint:
	poetry run pylint $(SRC)

build:
	poetry build

docs:
	poetry run python mkdocs > $(DOCS)/ru/CLI_REFERENCE.md

publish-testpypi:
	poetry publish -r testpypi

publish-pypi:
	poetry publish

clean:
	find . -maxdepth 1 -type d -name .testenv -print -exec rm -rf {} \; > /dev/null 2>&1 || true
	find . -maxdepth 1 -type d -name dist -print -exec rm -rf {} \; > /dev/null 2>&1 || true
	find . -type d -name __pycache__ -print -exec rm -rf {} \; > /dev/null 2>&1 || true
