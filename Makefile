.PHONY: help build up down shell clean
.PHONY: ml-data ml-features ml-train ml-export ml-evaluate ml-params ml-pipeline
.PHONY: th-network th-collect th-analyze th-export th-pipeline
.PHONY: sim-network sim-run sim-gui
.PHONY: pipeline

DOCKER_RUN = cd docker && docker-compose run --rm sumo
PYTHON = python3

help:
	@echo "Level Crossing Control System"
	@echo ""
	@echo "Docker:"
	@echo "  make build            Build Docker image"
	@echo "  make up               Start container"
	@echo "  make down             Stop container"
	@echo "  make shell            Open shell in container"
	@echo ""
	@echo "ML Training Pipeline:"
	@echo "  make ml-data          Generate training trajectories (2000 samples)"
	@echo "  make ml-data-quick    Quick data generation (50 samples)"
	@echo "  make ml-features      Extract features from trajectories"
	@echo "  make ml-train         Train ETA/ETD prediction models"
	@echo "  make ml-export        Export models for Arduino"
	@echo "  make ml-params        Export train parameters"
	@echo "  make ml-evaluate      Evaluate trained models"
	@echo "  make ml-pipeline      Run complete ML pipeline"
	@echo "  make ml-pipeline-quick Quick ML pipeline (testing)"
	@echo ""
	@echo "Threshold Analysis Pipeline:"
	@echo "  make th-network       Generate threshold collection network"
	@echo "  make th-collect       Collect threshold data (30 min)"
	@echo "  make th-collect-quick Quick data collection (5 min)"
	@echo "  make th-analyze       Calculate control thresholds"
	@echo "  make th-export        Export thresholds for Arduino"
	@echo "  make th-pipeline      Run complete threshold pipeline"
	@echo "  make th-pipeline-quick Quick threshold pipeline"
	@echo ""
	@echo "Simulation Pipeline:"
	@echo "  make sim-network      Generate simulation network"
	@echo "  make sim-run          Run simulation (1 hour)"
	@echo "  make sim-run-quick    Quick simulation (5 min)"
	@echo "  make sim-gui          Run simulation with GUI"
	@echo ""
	@echo "Complete Pipeline:"
	@echo "  make pipeline         Run everything (ML + Thresholds + Sim network)"
	@echo "  make pipeline-quick   Quick complete pipeline"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            Remove all generated files"

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


exp-ml:
	$(DOCKER_RUN) $(PYTHON) -m hardware.exporters.model

th-network:
	$(DOCKER_RUN) $(PYTHON) -m thresholds.network_generator

th-collect:
	$(DOCKER_RUN) $(PYTHON) -m thresholds.data_collector

th-collect-quick:
	$(DOCKER_RUN) $(PYTHON) -m thresholds.data_collector --duration 300

th-analyze:
	$(DOCKER_RUN) $(PYTHON) -m thresholds.analyzer

th-export:
	$(DOCKER_RUN) $(PYTHON) -m thresholds.exporter

th-pipeline:
	@echo "=== Running Threshold Pipeline ==="
	$(DOCKER_RUN) $(PYTHON) -m thresholds.network_generator
	$(DOCKER_RUN) $(PYTHON) -m thresholds.data_collector
	$(DOCKER_RUN) $(PYTHON) -m thresholds.analyzer
	$(DOCKER_RUN) $(PYTHON) -m thresholds.exporter
	@echo "=== Threshold Pipeline Complete ==="

th-pipeline-quick:
	@echo "=== Running Quick Threshold Pipeline ==="
	$(DOCKER_RUN) $(PYTHON) -m thresholds.network_generator
	$(DOCKER_RUN) $(PYTHON) -m thresholds.data_collector --duration 300
	$(DOCKER_RUN) $(PYTHON) -m thresholds.analyzer
	$(DOCKER_RUN) $(PYTHON) -m thresholds.exporter
	@echo "=== Quick Threshold Pipeline Complete ==="

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