POETRY=poetry
SOURCE_FOLDER=src/

lint: black mypy flake
lintfix: isort blackfix lint

mypy:
	$(POETRY) run mypy --ignore-missing-imports $(SOURCE_FOLDER)

flake:
	$(POETRY) run flake8 $(SOURCE_FOLDER)

black:
	$(POETRY) run black --check $(SOURCE_FOLDER)

blackfix:
	$(POETRY) run black $(SOURCE_FOLDER)

isort:
	$(POETRY) run isort --atomic $(SOURCE_FOLDER)
