.PHONY: help build up down shell clean
.PHONY: ml-data ml-features ml-train ml-export ml-evaluate ml-params ml-pipeline
.PHONY: th-network th-collect th-analyze th-export th-pipeline
.PHONY: sim-network sim-run sim-gui
.PHONY: pipeline

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

ml-data-quick:
	$(DOCKER_RUN) $(PYTHON) -m ml.data --samples 50

ml-train:
	$(DOCKER_RUN) $(PYTHON) -m ml.model

ml-pipeline: ml-data ml-train

ml-pipeline-quick: ml-data-quick ml-train


th-network:
	$(DOCKER_RUN) $(PYTHON) -m thresholds.network

th-collect:
	$(DOCKER_RUN) $(PYTHON) -m thresholds.collector

th-analyze:
	$(DOCKER_RUN) $(PYTHON) -m thresholds.analyzer

th-pipeline: th-network th-collect th-analyze


exp-ml:
	$(DOCKER_RUN) $(PYTHON) -m hardware.exporters.model

exp-th:
	$(DOCKER_RUN) $(PYTHON) -m hardware.exporters.thresholds


sim-network:
	$(DOCKER_RUN) $(PYTHON) -m simulation.network_generator

sim-run:
	$(DOCKER_RUN) $(PYTHON) -m simulation.runner

sim-run-quick:
	$(DOCKER_RUN) $(PYTHON) -m simulation.runner --duration 300

sim-gui:
	@command -v xhost >/dev/null 2>&1 && xhost +local:docker || true
	$(DOCKER_RUN) $(PYTHON) -m simulation.runner --gui

hard-scale:
	$(DOCKER_RUN) $(PYTHON) -m hardware.scale_config_generator

pipeline: ml-pipeline th-pipeline sim-network
	@echo ""
	@echo "Complete pipeline finished"
	@echo "ML models: outputs/models/train_models.h"
	@echo "Thresholds: outputs/models/thresholds_config.h"
	@echo "Train params: config/train_params.yaml"
	@echo "Simulation network ready"
	@echo ""
	@echo "Run 'make sim-run' to test the system"

pipeline-quick: ml-pipeline-quick th-pipeline-quick sim-network
	@echo ""
	@echo "Quick pipeline finished"
	@echo "Run 'make sim-run-quick' to test"

clean:
	@echo "Cleaning generated files..."
	rm -rf outputs/data/*
	rm -rf outputs/models/*
	rm -rf outputs/results/*
	rm -rf outputs/metrics/*
	rm -rf outputs/thresholds/*
	rm -rf sumo/training/*.xml
	rm -rf sumo/thresholds/*.xml
	rm -rf sumo/complete/*.xml
	rm -f config/thresholds_calculated.yaml
	rm -f config/train_params.yaml
	rm -f training.*.xml
	rm -f thresholds.*.xml
	rm -f thresholds_summary.xml
	@echo "Clean complete"