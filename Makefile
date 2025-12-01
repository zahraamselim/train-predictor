.PHONY: help build up down shell clean
.PHONY: network data train export simulate gui
.PHONY: pipeline metrics

help:
	@echo "Level Crossing Control System"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make build       Build Docker image"
	@echo "  make up          Start container"
	@echo "  make down        Stop container"
	@echo "  make shell       Open shell in container"
	@echo ""
	@echo "Pipeline Commands:"
	@echo "  make pipeline    Run complete pipeline"
	@echo "  make network     Generate SUMO network"
	@echo "  make data        Collect training data"
	@echo "  make train       Train ML model"
	@echo "  make export      Export to Arduino"
	@echo ""
	@echo "Simulation Commands:"
	@echo "  make simulate    Run simulation (no GUI)"
	@echo "  make gui         Run simulation with GUI"
	@echo "  make metrics     View metrics report"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make clean       Clean all outputs"

build:
	cd docker && docker-compose build

up:
	cd docker && docker-compose up -d

down:
	cd docker && docker-compose down

shell:
	cd docker && docker-compose run --rm sumo /bin/bash

pipeline:
	cd docker && docker-compose run --rm sumo python3 scripts/pipeline.py --all

network:
	cd docker && docker-compose run --rm sumo python3 simulation/network/generator.py

data:
	cd docker && docker-compose run --rm sumo python3 simulation/data/collector.py

train:
	cd docker && docker-compose run --rm sumo python3 simulation/ml/train_eta.py --collect --train

export:
	cd docker && docker-compose run --rm sumo python3 simulation/ml/export.py --all

simulate:
	cd docker && docker-compose run --rm sumo python3 scripts/run_simulation.py

gui:
	xhost +local:docker
	cd docker && docker-compose run --rm sumo python3 scripts/run_simulation.py --gui

metrics:
	@echo "Metrics Summary:"
	@cat outputs/metrics/summary.csv 2>/dev/null || echo "No metrics available. Run simulation first."

clean:
	rm -rf outputs/data/* outputs/models/* outputs/metrics/*
	rm -rf sumo/*.xml
	rm -rf hardware/arduino/*.h
	rm -f config/thresholds.yaml
	cd docker && docker-compose down -v