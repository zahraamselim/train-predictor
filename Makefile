.PHONY: help build up down shell clean
.PHONY: th-network th-collect th-analyze th-export th-pipeline th-quick th-clean
.PHONY: ml-data ml-train ml-export ml-pipeline ml-quick ml-clean
.PHONY: sim-network sim-run sim-gui sim-pipeline sim-clean
.PHONY: all test

DOCKER_RUN = cd docker && docker-compose run --rm sumo
PYTHON = python3

help:
	@echo "Railroad Crossing Control System - Makefile"
	@echo ""
	@echo "Complete Pipeline:"
	@echo "  make all           - Run complete system (thresholds + ML + simulation)"
	@echo "  make test          - Quick test of all modules"
	@echo ""
	@echo "Thresholds Module:"
	@echo "  make th-pipeline   - Generate thresholds (network + collect + analyze + export)"
	@echo "  make th-network    - Generate SUMO network"
	@echo "  make th-collect    - Collect traffic data (1 hour)"
	@echo "  make th-analyze    - Calculate thresholds from data"
	@echo "  make th-export     - Export thresholds to Arduino header"
	@echo "  make th-quick      - Quick test (5 min simulation)"
	@echo "  make th-clean      - Remove generated files"
	@echo ""
	@echo "ML Module:"
	@echo "  make ml-pipeline   - Train models (data + train + export)"
	@echo "  make ml-data       - Generate training data (1000 samples)"
	@echo "  make ml-train      - Train ETA/ETD models"
	@echo "  make ml-export     - Export models for Arduino"
	@echo "  make ml-quick      - Quick test (50 samples)"
	@echo "  make ml-clean      - Remove generated files"
	@echo ""
	@echo "Simulation Module:"
	@echo "  make sim-pipeline  - Run simulation (network + both phases)"
	@echo "  make sim-network   - Generate simulation network"
	@echo "  make sim-run       - Run two-phase simulation"
	@echo "  make sim-gui       - Run with GUI visualization"
	@echo "  make sim-clean     - Remove generated files"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make build         - Build Docker container"
	@echo "  make up            - Start Docker container"
	@echo "  make down          - Stop Docker container"
	@echo "  make shell         - Open shell in container"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean         - Clean all generated files"

build:
	cd docker && docker-compose build

up:
	cd docker && docker-compose up -d

down:
	cd docker && docker-compose down

shell:
	$(DOCKER_RUN) /bin/bash

th-network:
	$(DOCKER_RUN) $(PYTHON) -m thresholds.network

th-collect:
	$(DOCKER_RUN) $(PYTHON) -m thresholds.collector

th-analyze:
	$(DOCKER_RUN) $(PYTHON) -m thresholds.analyzer

th-export:
	$(DOCKER_RUN) $(PYTHON) -m hardware.exporters.threshold

th-pipeline: th-network th-collect th-analyze th-export
	@echo ""
	@echo "Thresholds pipeline complete"
	@echo "Results in outputs/results/thresholds.yaml"
	@echo "Arduino header in hardware/thresholds.h"

th-quick:
	$(DOCKER_RUN) $(PYTHON) -m thresholds.network
	$(DOCKER_RUN) $(PYTHON) -m thresholds.collector --duration 300
	$(DOCKER_RUN) $(PYTHON) -m thresholds.analyzer
	$(DOCKER_RUN) $(PYTHON) -m hardware.exporters.threshold

th-clean:
	rm -rf outputs/data/clearances.csv outputs/data/travels.csv
	rm -rf outputs/plots/thresholds_analysis.png
	rm -rf outputs/results/thresholds.yaml outputs/results/thresholds.json
	rm -f thresholds.*.xml temp_* *.net.xml *.rou.xml *.sumocfg

ml-data:
	$(DOCKER_RUN) $(PYTHON) -m ml.data

ml-train:
	$(DOCKER_RUN) $(PYTHON) -m ml.model

ml-export:
	$(DOCKER_RUN) $(PYTHON) -m hardware.exporters.model

ml-pipeline: ml-data ml-train ml-export
	@echo ""
	@echo "ML pipeline complete"
	@echo "Models in outputs/models/"
	@echo "Evaluation in outputs/results/evaluation_results.json"
	@echo "Arduino headers in hardware/eta_model.h and hardware/etd_model.h"

ml-quick:
	$(DOCKER_RUN) $(PYTHON) -m ml.data --samples 50
	$(DOCKER_RUN) $(PYTHON) -m ml.model
	@echo ""
	@echo "Quick ML test complete (results less accurate with 50 samples)"

ml-clean:
	rm -rf outputs/data/raw_trajectories.csv outputs/data/features.csv
	rm -rf outputs/models/
	rm -rf outputs/plots/train_trajectories.png outputs/plots/feature_*.png
	rm -rf outputs/plots/physics_comparison.png outputs/plots/eta_*.png outputs/plots/etd_*.png
	rm -rf outputs/results/evaluation_results.json
	rm -f training.*.xml temp_* *.net.xml *.rou.xml *.sumocfg

sim-network:
	$(DOCKER_RUN) $(PYTHON) -m simulation.network

sim-run:
	$(DOCKER_RUN) $(PYTHON) -m simulation.controller

sim-gui:
	@command -v xhost >/dev/null 2>&1 && xhost +local:docker || true
	$(DOCKER_RUN) $(PYTHON) -m simulation.controller --gui

sim-pipeline: sim-network sim-run
	@echo ""
	@echo "Simulation pipeline complete"
	@echo "Vehicle data in outputs/data/*_vehicles.csv"
	@echo "Metrics in outputs/results/*_metrics.json"
	@echo "Comparison in outputs/results/comparison.json"

sim-clean:
	rm -rf outputs/data/phase1_vehicles.csv outputs/data/phase2_vehicles.csv
	rm -rf outputs/results/phase1_metrics.json outputs/results/phase2_metrics.json
	rm -rf outputs/results/optimized_metrics.json outputs/results/comparison.json
	rm -f simulation.*.xml temp_* *.net.xml *.rou.xml *.sumocfg view.xml

all: th-pipeline ml-pipeline sim-pipeline
	@echo ""
	@echo "==============================================="
	@echo "Complete pipeline finished successfully"
	@echo "==============================================="
	@echo ""
	@echo "Thresholds:"
	@echo "  - outputs/results/thresholds.yaml"
	@echo "  - hardware/thresholds.h"
	@echo ""
	@echo "ML Models:"
	@echo "  - outputs/models/eta_model.pkl"
	@echo "  - outputs/models/etd_model.pkl"
	@echo "  - outputs/results/evaluation_results.json"
	@echo "  - hardware/eta_model.h"
	@echo "  - hardware/etd_model.h"
	@echo ""
	@echo "Simulation:"
	@echo "  - outputs/results/comparison.json"
	@echo "  - outputs/data/phase1_vehicles.csv"
	@echo "  - outputs/data/phase2_vehicles.csv"
	@echo ""
	@echo "Ready for hardware deployment!"

test: th-quick ml-quick sim-network
	@echo ""
	@echo "Quick test complete - all modules functional"
	@echo "Run 'make all' for full pipeline with accurate results"

clean: th-clean ml-clean sim-clean
	rm -rf outputs/
	rm -f *.xml temp_* *.net.xml *.rou.xml *.sumocfg view.xml
	@echo "All generated files cleaned"