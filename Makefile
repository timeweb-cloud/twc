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
	find . -maxdepth 1 -type d -name .testenv -exec rm -rf {} \; > /dev/null 2>&1 || true
	find . -maxdepth 1 -type d -name dist -exec rm -rf {} \; > /dev/null 2>&1 || true
	find . -type d -name __pycache__ -exec rm -rf {} \; > /dev/null 2>&1 || true

zipapp:
	mkdir -p $(ZIPAPP)
	python -m venv $(ZIPAPP)-env
	cp -ar twc $(ZIPAPP)
	poetry export --without-hashes -o $(ZIPAPP)/requirements.txt
	. $(ZIPAPP)-env/bin/activate; pip install --target $(ZIPAPP) -r $(ZIPAPP)/requirements.txt
	find $(ZIPAPP) -type d -name "*.dist-info" -exec rm -rf {} \; > /dev/null 2>&1 || true
	python -m zipapp -c -m twc.__main__:cli -p '/usr/bin/env python3' -o $(DIST)/twc_cli.pyz $(ZIPAPP)
	rm -rf $(ZIPAPP) $(ZIPAPP)-env
