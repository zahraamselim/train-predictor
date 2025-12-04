.PHONY: help build up down shell clean
.PHONY: ml-data ml-train ml-pipeline
.PHONY: th-network th-collect th-analyze th-pipeline
.PHONY: sim-network sim-run sim-gui sim-pipeline

DOCKER_RUN = cd docker && docker-compose run --rm sumo
PYTHON = python3

build:
	cd docker && docker-compose build

up:
	cd docker && docker-compose up -d

down:
	cd docker && docker-compose down

shell:
	$(DOCKER_RUN) /bin/bash


ml-data:
	$(DOCKER_RUN) $(PYTHON) -m ml.data

ml-train:
	$(DOCKER_RUN) $(PYTHON) -m ml.model

ml-pipeline: ml-data ml-train


th-network:
	$(DOCKER_RUN) $(PYTHON) -m thresholds.network

th-collect:
	$(DOCKER_RUN) $(PYTHON) -m thresholds.collector

th-analyze:
	$(DOCKER_RUN) $(PYTHON) -m thresholds.analyzer

th-pipeline: th-network th-collect th-analyze


sim-network:
	$(DOCKER_RUN) $(PYTHON) -m simulation.network

sim-run:
	$(DOCKER_RUN) $(PYTHON) -m simulation.controller

sim-gui:
	@command -v xhost >/dev/null 2>&1 && xhost +local:docker || true
	$(DOCKER_RUN) $(PYTHON) -m simulation.controller --gui

sim-pipeline: sim-network sim-run

exp-ml:
	$(DOCKER_RUN) $(PYTHON) -m hardware.exporters.model

exp-th:
	$(DOCKER_RUN) $(PYTHON) -m hardware.exporters.thresholds
