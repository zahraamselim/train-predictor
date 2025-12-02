.PHONY: help build up down shell clean
.PHONY: pipeline network data analyze train export
.PHONY: simulate gui metrics test

DOCKER_RUN = cd docker && docker-compose run --rm sumo
PYTHON = python3

help:
	@echo "Level Crossing Control System"
	@echo ""
	@echo "Docker:"
	@echo "  make build       Build Docker image"
	@echo "  make up          Start container"
	@echo "  make down        Stop container"
	@echo "  make shell       Open shell in container"
	@echo ""
	@echo "Pipeline:"
	@echo "  make pipeline    Run complete pipeline"
	@echo "  make network     Generate SUMO network"
	@echo "  make data        Collect training data"
	@echo "  make analyze     Analyze thresholds"
	@echo "  make train       Train ML model"
	@echo "  make export      Export to Arduino"
	@echo ""
	@echo "Simulation:"
	@echo "  make simulate    Run simulation"
	@echo "  make gui         Run simulation with GUI"
	@echo "  make test        Quick test (60s)"
	@echo ""
	@echo "Output:"
	@echo "  make metrics     View metrics summary"
	@echo "  make clean       Clean all outputs"

build:
	cd docker && docker-compose build

up:
	cd docker && docker-compose up -d

down:
	cd docker && docker-compose down

shell:
	$(DOCKER_RUN) /bin/bash

pipeline:
	$(DOCKER_RUN) $(PYTHON) scripts/pipeline.py

network:
	$(DOCKER_RUN) $(PYTHON) -c "from simulation.network.generator import NetworkGenerator; NetworkGenerator(mode='complete').generate()"

data:
	$(DOCKER_RUN) $(PYTHON) simulation/data/collector.py

analyze:
	$(DOCKER_RUN) $(PYTHON) simulation/data/analyzer.py

train:
	$(DOCKER_RUN) $(PYTHON) -c "from simulation.ml.trainer import ETATrainer; t = ETATrainer(); t.collect_data(250); t.train_model()"

export:
	$(DOCKER_RUN) $(PYTHON) -c "from simulation.ml.exporter import ArduinoExporter; e = ArduinoExporter(); e.export_model(); e.export_config()"

simulate:
	$(DOCKER_RUN) $(PYTHON) scripts/simulate.py

gui:
	@command -v xhost >/dev/null 2>&1 && xhost +local:docker || true
	$(DOCKER_RUN) $(PYTHON) scripts/simulate.py --gui

test:
	$(DOCKER_RUN) $(PYTHON) scripts/simulate.py --duration 60

metrics:
	@if [ -f outputs/metrics/summary.csv ]; then \
		echo "Metrics Summary:"; \
		cat outputs/metrics/summary.csv; \
	else \
		echo "No metrics available. Run 'make simulate' first."; \
	fi

clean:
	rm -rf outputs/data/* outputs/models/* outputs/metrics/*
	rm -rf sumo/complete/*.xml sumo/training/*.xml
	rm -f hardware/*.h
	rm -f config/thresholds.yaml
	cd docker && docker-compose down -v