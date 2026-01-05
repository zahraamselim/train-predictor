.PHONY: help train simulate arduino quick clean all

DOCKER = cd docker && docker-compose run --rm sumo
PYTHON = python3

help:
	@echo "Railway Crossing Control System"
	@echo ""
	@echo "Complete Pipeline:"
	@echo "  make all           - Run complete system (train + simulate + arduino)"
	@echo "  make quick         - Quick test (50 samples, no simulation)"
	@echo ""
	@echo "Individual Steps:"
	@echo "  make train         - Generate training data and train models (5 min)"
	@echo "  make simulate      - Run traffic simulation (30 min, needed for poster)"
	@echo "  make arduino       - Export models/config to Arduino"
	@echo ""
	@echo "Docker:"
	@echo "  make build         - Build Docker container"
	@echo "  make shell         - Open shell in container"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean         - Remove all generated files"

build:
	cd docker && docker-compose build

shell:
	$(DOCKER) /bin/bash

train:
	@echo "Generating training data and training models..."
	$(DOCKER) $(PYTHON) train_data.py
	$(DOCKER) $(PYTHON) train_models.py
	@echo ""
	@echo "Training complete!"
	@echo "Results:"
	@echo "  outputs/features.csv"
	@echo "  outputs/eta_model.pkl"
	@echo "  outputs/etd_model.pkl"
	@echo "  outputs/model_results.json"

simulate:
	@echo "Running traffic simulation (Phase 1 + Phase 2)..."
	$(DOCKER) $(PYTHON) run_simulation.py
	@echo ""
	@echo "Simulation complete!"
	@echo "Results:"
	@echo "  outputs/phase1_vehicles.csv"
	@echo "  outputs/phase2_vehicles.csv"
	@echo "  outputs/comparison.json"

simulate-gui:
	@echo "Running simulation with GUI..."
	@command -v xhost >/dev/null 2>&1 && xhost +local:docker || true
	$(DOCKER) $(PYTHON) run_simulation.py --gui

arduino:
	@echo "Exporting to Arduino..."
	$(DOCKER) $(PYTHON) export_arduino.py
	@echo ""
	@echo "Arduino export complete!"
	@echo "Generated files:"
	@echo "  arduino/model.h"
	@echo "  arduino/thresholds.h"
	@echo "  arduino/config.h"
	@echo ""
	@echo "Ready to upload arduino/sketch.ino"

quick:
	@echo "Quick test (50 samples, no simulation)..."
	$(DOCKER) $(PYTHON) train_data.py --samples 50
	$(DOCKER) $(PYTHON) train_models.py
	$(DOCKER) $(PYTHON) export_arduino.py
	@echo ""
	@echo "Quick test complete!"

all: train simulate arduino
	@echo ""
	@echo "Complete pipeline finished!"
	@echo ""
	@echo "ML Models:"
	@echo "  outputs/eta_model.pkl"
	@echo "  outputs/etd_model.pkl"
	@echo "  outputs/model_results.json"
	@echo ""
	@echo "Simulation:"
	@echo "  outputs/phase1_vehicles.csv"
	@echo "  outputs/phase2_vehicles.csv"
	@echo "  outputs/comparison.json"
	@echo ""
	@echo "Arduino:"
	@echo "  arduino/model.h"
	@echo "  arduino/thresholds.h"
	@echo "  arduino/config.h"
	@echo ""
	@echo "Ready for Arduino deployment!"

clean:
	rm -rf outputs/
	rm -f *.xml temp_*
	rm -f simulation.sumocfg
	rm -f arduino/model.h arduino/thresholds.h arduino/config.h
	@echo "All generated files cleaned"