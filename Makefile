SRC = twc

all: format lint build

format:
	poetry run black $(SRC)

lint:
	poetry run pylint $(SRC)

build:
	poetry build

publish-testpypi:
	poetry publish -r testpypi

publish-pypi:
	poetry publish
