.PHONY: help setup install clean \
	data-traffic data-train data-train-full data-all \
	ml-train ml-test ml-export \
	arduino-config arduino-export \
	simulate \
	validate-all \
	scale-demo scale-real

PYTHON = python3
VENV = .venv
BIN = $(VENV)/bin

help:
	@echo "Level Crossing Notification System"
	@echo ""
	@echo "Setup:"
	@echo "  make setup               Create venv and install dependencies"
	@echo "  make scale-demo          Switch to demo scale (75cm board)"
	@echo "  make scale-real          Switch to real scale (3km distances)"
	@echo ""
	@echo "Data Generation:"
	@echo "  make data-traffic        Generate traffic clearance data"
	@echo "  make data-train          Generate train approach data (100 scenarios)"
	@echo "  make data-train-full     Generate full dataset (500 scenarios)"
	@echo "  make data-all            Generate all datasets"
	@echo ""
	@echo "Machine Learning:"
	@echo "  make ml-train            Train ETA predictor model"
	@echo "  make ml-test             Test trained ETA predictor"
	@echo "  make ml-export           Export model to Arduino header"
	@echo ""
	@echo "Arduino:"
	@echo "  make arduino-config      Generate crossing_config.h"
	@echo "  make arduino-export      Export both headers (model + config)"
	@echo "  make hardware            Complete hardware pipeline"
	@echo ""
	@echo "Simulation:"
	@echo "  make simulate            Run pygame simulation"
	@echo ""
	@echo "Validation:"
	@echo "  make validate-all        Validate all generated data"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean               Remove venv"
	@echo "  make clean-data          Remove generated data"
	@echo "  make clean-all           Remove everything"

setup: venv install
	@echo "Setup complete. Activate with: source $(BIN)/activate"

venv:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)

install:
	@echo "Installing dependencies..."
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt

scale-demo:
	@echo "Switching to demo scale (cm)..."
	$(BIN)/python -m config.utils demo

scale-real:
	@echo "Switching to real scale (m)..."
	$(BIN)/python -m config.utils real

data-traffic:
	@echo "Generating traffic clearance data..."
	$(BIN)/python -m data_generation.generate_traffic

data-train:
	@echo "Generating train approach data (100 scenarios)..."
	$(BIN)/python -m data_generation.generate_train

data-train-full:
	@echo "Generating full train dataset (500 scenarios)..."
	$(BIN)/python -m data_generation.generate_train full

data-all: data-traffic data-train-full
	@echo "All datasets generated"

ml-train:
	@echo "Training ETA predictor..."
	$(BIN)/python -m ml.eta_predictor

ml-test:
	@echo "Testing ETA predictor..."
	$(BIN)/python -c "from ml.eta_predictor import ETAPredictor; \
		predictor = ETAPredictor('ml/models/eta_predictor.pkl'); \
		result = predictor.predict(8.5, 6.2, 25.5, 28.3, 0.45, 81); \
		print(f'Test prediction: {result}')"

ml-export:
	@echo "Exporting model to Arduino..."
	$(BIN)/python arduino/export_model_to_arduino.py

arduino-config:
	@echo "Generating crossing configuration..."
	$(BIN)/python arduino/update_crossing_config.py

arduino-export: arduino-config ml-export
	@echo ""
	@echo "Arduino headers exported:"
	@echo "  - arduino/eta_model.h"
	@echo "  - arduino/crossing_config.h"

hardware: data-traffic data-train-full ml-train arduino-export
	@echo ""
	@echo "Hardware pipeline complete"
	@echo "Upload arduino/sketch.ino to your board"

simulate:
	@echo "Starting simulation..."
	$(BIN)/python -m simulation.main

validate-traffic:
	@echo "Validating traffic data..."
	$(BIN)/python -m data_generation.generate_traffic validate

validate-train:
	@echo "Validating train data..."
	$(BIN)/python -m data_generation.generate_train validate

validate-all: validate-traffic validate-train
	@echo "All validations complete"

workflow: data-all ml-train validate-all
	@echo "Complete workflow finished"
	@echo "Ready to run: make simulate"

clean:
	@echo "Removing virtual environment..."
	rm -rf $(VENV)

clean-data:
	@echo "Removing generated data..."
	rm -rf data_generation/data/*.csv
	rm -rf ml/models/*.pkl

clean-all: clean clean-data
	@echo "Complete cleanup finished"

.DEFAULT_GOAL := help