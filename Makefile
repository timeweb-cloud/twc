SRC = twc
DOCS = docs
DIST = dist
ZIPAPP = .zipapp

.PHONY: docs

all: format lint build zipapp docs

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
	[ -d .testenv/ ] && rm -rf .testenv/ || true
	[ -d dist/ ] && rm -rf dist/ || true
	find . -type d -name __pycache__ -exec rm -rf {} \; > /dev/null 2>&1 || true
	[ -d $(ZIPAPP) ] && rm -rf $(ZIPAPP) || true
	[ -d $(ZIPAPP)-env ] && rm -rf $(ZIPAPP)-env || true

zipapp:
	mkdir -p $(DIST)
	mkdir -p $(ZIPAPP)
	python -m venv $(ZIPAPP)-env
	cp -ar twc $(ZIPAPP)
	poetry export --without-hashes -o $(ZIPAPP)/requirements.txt
	. $(ZIPAPP)-env/bin/activate; pip install --target $(ZIPAPP) -r $(ZIPAPP)/requirements.txt > /dev/null
	find $(ZIPAPP) -type d -name "*.dist-info" -exec rm -rf {} \; > /dev/null 2>&1 || true
	version=$$(awk '/version/{print substr($$3, 2, 5)}' pyproject.toml); python -m zipapp -c -m twc.__main__:cli -p '/usr/bin/env python3' -o $(DIST)/twc_cli-$${version}.pyz $(ZIPAPP)
