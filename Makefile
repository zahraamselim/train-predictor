.PHONY: help setup install clean clean-data clean-all \
	train-demo train-small train-full \
	traffic-generate traffic-analyze \
	validate-train validate-traffic \
	visualize-train-demo visualize-train-small visualize-train-full \
	visualize-traffic simulate-train \
	scale-demo scale-real \
	lint format test docs

PYTHON = python3
VENV = .venv
BIN = $(VENV)/bin

help:
	@echo "Level Crossing Notification System"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make setup               Create virtual environment and install dependencies"
	@echo "  make install             Install dependencies (venv must exist)"
	@echo "  make scale-demo          Set scale to demo mode (75x75cm board)"
	@echo "  make scale-real          Set scale to real mode (2000m distances)"
	@echo ""
	@echo "Data Generation:"
	@echo "  make train-demo          Generate demo train dataset (10 scenarios)"
	@echo "  make train-small         Generate small train dataset (50 scenarios)"
	@echo "  make train-full          Generate full train dataset (100 scenarios)"
	@echo "  make train-all           Generate all train datasets"
	@echo ""
	@echo "  make traffic-generate    Generate traffic parameters from config"
	@echo "  make traffic-analyze     Analyze gate timing and notification scenarios"
	@echo ""
	@echo "Validation & Analysis:"
	@echo "  make validate-train      Validate train dataset integrity"
	@echo "  make validate-traffic    Validate traffic dataset integrity"
	@echo ""
	@echo "Visualization:"
	@echo "  make visualize-train-demo    Visualize demo train dataset"
	@echo "  make visualize-train-small   Visualize small train dataset"
	@echo "  make visualize-train-full    Visualize full train dataset"
	@echo "  make visualize-traffic       Visualize traffic parameters"
	@echo "  make visualize-all           Generate all visualizations"
	@echo ""
	@echo "Simulation:"
	@echo "  make simulate-train      Run live train simulation (pygame)"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint                Run code linter (pylint)"
	@echo "  make format              Format code with black"
	@echo "  make test                Run tests (if available)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean               Remove virtual environment"
	@echo "  make clean-data          Remove generated datasets and plots"
	@echo "  make clean-all           Remove venv and all generated data"

setup: venv install
	@echo "Setup complete. Activate venv with: source $(BIN)/activate"

venv:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo "Virtual environment created."

install:
	@echo "Installing dependencies..."
	$(BIN)/pip install --upgrade pip setuptools wheel
	$(BIN)/pip install -r requirements.txt
	@echo "Dependencies installed."

scale-demo:
	@echo "Setting scale to demo mode..."
	$(BIN)/python -m config.utils demo
	@echo "Scale set to demo (cm)"

scale-real:
	@echo "Setting scale to real mode..."
	$(BIN)/python -m config.utils real
	@echo "Scale set to real (m)"

train-demo:
	@echo "Generating demo train dataset (10 scenarios)..."
	@mkdir -p 01_train_dataset/data
	$(BIN)/python -m 01_train_dataset.generate_dataset demo

train-small:
	@echo "Generating small train dataset (50 scenarios)..."
	@mkdir -p 01_train_dataset/data
	$(BIN)/python -m 01_train_dataset.generate_dataset small

train-full:
	@echo "Generating full train dataset (100 scenarios)..."
	@mkdir -p 01_train_dataset/data
	$(BIN)/python -m 01_train_dataset.generate_dataset full

train-all: train-demo train-small train-full
	@echo "All train datasets generated."

traffic-generate:
	@echo "Generating traffic parameters..."
	@mkdir -p 02_traffic_parameters/data
	$(BIN)/python -m 02_traffic_parameters.generate_parameters generate

traffic-analyze:
	@echo "Analyzing intersection timing scenarios..."
	$(BIN)/python -m 02_traffic_parameters.generate_parameters analyze

validate-train:
	@echo "Validating train datasets..."
	$(BIN)/python -m 06_validation.validate_data train

validate-traffic:
	@echo "Validating traffic datasets..."
	$(BIN)/python -m 06_validation.validate_data traffic

visualize-train-demo:
	@echo "Visualizing demo train dataset..."
	@mkdir -p 06_validation/plots
	$(BIN)/python -m 06_validation.visualize_dataset 01_train_dataset/data/train_data_demo.csv

visualize-train-small:
	@echo "Visualizing small train dataset..."
	@mkdir -p 06_validation/plots
	$(BIN)/python -m 06_validation.visualize_dataset 01_train_dataset/data/train_data_small.csv

visualize-train-full:
	@echo "Visualizing full train dataset..."
	@mkdir -p 06_validation/plots
	$(BIN)/python -m 06_validation.visualize_dataset 01_train_dataset/data/train_data.csv

visualize-traffic:
	@echo "Visualizing traffic parameters..."
	@mkdir -p 06_validation/plots
	$(BIN)/python -m 06_validation.visualize_traffic 02_traffic_parameters/data/traffic_parameters.csv

visualize-all: visualize-train-demo visualize-train-small visualize-train-full visualize-traffic
	@echo "All visualizations generated."

simulate-train:
	@echo "Running live train simulation..."
	$(BIN)/python -m 05_simulation.train_visualization

lint:
	@echo "Running code linter..."
	$(BIN)/pylint 01_train_dataset/ 02_traffic_parameters/ config/ || true

format:
	@echo "Formatting code with black..."
	$(BIN)/black 01_train_dataset/ 02_traffic_parameters/ config/

test:
	@echo "Running tests..."
	$(BIN)/pytest tests/ -v || true

clean:
	@echo "Removing virtual environment..."
	rm -rf $(VENV)
	@echo "Virtual environment removed."

clean-data:
	@echo "Removing generated data and visualizations..."
	rm -f 01_train_dataset/data/*.csv
	rm -f 02_traffic_parameters/data/*.csv
	rm -f 06_validation/plots/*.png
	@echo "Data files removed."

clean-all: clean clean-data
	@echo "Complete cleanup finished."

.DEFAULT_GOAL := help