RUNNER=pipenv
SOURCE_FOLDER=src/

lint: black mypy flake
lintfix: isort blackfix lint

mypy:
	$(RUNNER) run mypy --ignore-missing-imports $(SOURCE_FOLDER)

flake:
	$(RUNNER) run flake8 $(SOURCE_FOLDER)

black:
	$(RUNNER) run black --check $(SOURCE_FOLDER)

blackfix:
	$(RUNNER) run black $(SOURCE_FOLDER)

isort:
	$(RUNNER) run isort --atomic $(SOURCE_FOLDER)
