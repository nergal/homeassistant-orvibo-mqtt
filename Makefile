RUNNER=pipenv
SOURCE_FOLDER=rootfs/

.PHONY: lint
lint: black mypy flake

.PHONY: lintfix
lintfix: isort blackfix lint

.DEFAULT_GOAL := lint

.PHONY: run
run:
	cd $(SOURCE_FOLDER) && $(RUNNER) run \
		python usr/lib/orvibo_mqtt_daemon.py \
		--config=usr/etc/daemon_config.json

.PHONY: mypy
mypy:
	$(RUNNER) run mypy --ignore-missing-imports $(SOURCE_FOLDER)

.PHONY: flake
flake:
	$(RUNNER) run flake8 $(SOURCE_FOLDER)

.PHONY: black
black:
	$(RUNNER) run black --check $(SOURCE_FOLDER)

.PHONY: blackfix
blackfix:
	$(RUNNER) run black $(SOURCE_FOLDER)

.PHONY: isort
isort:
	$(RUNNER) run isort --atomic $(SOURCE_FOLDER)
