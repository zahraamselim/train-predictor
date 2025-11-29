.PHONY: help setup install clean clean-data clean-all \
	traffic-generate traffic-analyze \
	sensors-calculate sensors-apply \
	train-demo train-small train-full \
	model-train-demo model-train-small model-train-full \
	validate-traffic validate-train validate-model validate-all \
	workflow-demo workflow-full \
	simulate \
	scale-demo scale-real \
	lint format test

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
	@echo "CORRECT WORKFLOW (run in this order):"
	@echo "  1. make traffic-generate      Generate traffic clearance data"
	@echo "  2. make sensors-calculate     Calculate sensor positions (view only)"
	@echo "  3. make sensors-apply         Apply sensor positions to config"
	@echo "  4. make train-[demo|small|full]  Generate train dataset"
	@echo "  5. make model-train-[demo|small|full]  Train ML models"
	@echo "  6. make validate-all          Validate all outputs"
	@echo ""
	@echo "Quick Commands:"
	@echo "  make workflow-demo       Run full workflow with demo dataset"
	@echo "  make workflow-full       Run full workflow with full dataset"
	@echo ""
	@echo "Individual Steps:"
	@echo "  make traffic-generate    Generate traffic parameters"
	@echo "  make traffic-analyze     Analyze gate timing scenarios"
	@echo "  make sensors-calculate   Calculate optimal sensor positions"
	@echo "  make sensors-apply       Apply calculated positions to config"
	@echo ""
	@echo "  make train-demo          Generate demo train dataset (10 scenarios)"
	@echo "  make train-small         Generate small train dataset (50 scenarios)"
	@echo "  make train-full          Generate full train dataset (100 scenarios)"
	@echo ""
	@echo "  make model-train-demo    Train models on demo dataset"
	@echo "  make model-train-small   Train models on small dataset"
	@echo "  make model-train-full    Train models on full dataset"
	@echo ""
	@echo "Validation Commands:"
	@echo "  make validate-traffic    Validate traffic module output"
	@echo "  make validate-train      Validate train dataset output"
	@echo "  make validate-model      Validate model training output"
	@echo "  make validate-all        Run all validations"
	@echo ""
	@echo "Simulation:"
	@echo "  make simulate            Run crossing simulation (pygame)"
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

traffic-generate:
	@echo "Generating traffic parameters..."
	$(BIN)/python -m 01_traffic.generate_parameters generate

traffic-analyze:
	@echo "Analyzing intersection timing scenarios..."
	$(BIN)/python -m 01_traffic.generate_parameters analyze

sensors-calculate:
	@echo "Calculating optimal sensor positions..."
	$(BIN)/python -m 01_traffic.calculate_sensor_positions

sensors-apply:
	@echo "Applying sensor positions to config..."
	$(BIN)/python -m 01_traffic.calculate_sensor_positions --apply

train-demo:
	@echo "Generating demo train dataset (10 scenarios)..."
	$(BIN)/python -m 02_train.generate_dataset demo

train-small:
	@echo "Generating small train dataset (50 scenarios)..."
	$(BIN)/python -m 02_train.generate_dataset small

train-full:
	@echo "Generating full train dataset (100 scenarios)..."
	$(BIN)/python -m 02_train.generate_dataset full

model-train-demo:
	@echo "Training models on demo dataset..."
	$(BIN)/python -m 03_model.train_model 02_train/data/train_data_demo.csv

model-train-small:
	@echo "Training models on small dataset..."
	$(BIN)/python -m 03_model.train_model 02_train/data/train_data_small.csv

model-train-full:
	@echo "Training models on full dataset..."
	$(BIN)/python -m 03_model.train_model

validate-traffic:
	@echo "Validating traffic module..."
	$(BIN)/python -m 06_validation.validate_traffic

validate-train:
	@echo "Validating train dataset module..."
	$(BIN)/python -m 06_validation.validate_train

validate-model:
	@echo "Validating model training module..."
	$(BIN)/python -m 06_validation.validate_model

validate-all:
	@echo "Running all validations..."
	$(BIN)/python -m 06_validation.validate_all

workflow-demo: traffic-generate sensors-apply train-demo model-train-demo validate-all
	@echo "Demo workflow complete!"

workflow-full: traffic-generate sensors-apply train-full model-train-full validate-all
	@echo "Full workflow complete!"

simulate:
	@echo "Running crossing simulation..."
	$(BIN)/python -m 05_simulation.simulator

lint:
	@echo "Running code linter..."
	$(BIN)/pylint 01_traffic/ 02_train/ 03_model/ config/ 06_validation/ || true

format:
	@echo "Formatting code with black..."
	$(BIN)/black 01_traffic/ 02_train/ 03_model/ config/ 06_validation/

test:
	@echo "Running tests..."
	$(BIN)/pytest tests/ -v || true

clean:
	@echo "Removing virtual environment..."
	rm -rf $(VENV)
	@echo "Virtual environment removed."

clean-data:
	@echo "Removing generated data and visualizations..."
	rm -f 01_traffic/data/*.csv
	rm -f 02_train/data/*.csv
	rm -f 03_model/models/*.json
	rm -f 03_model/models/*.h
	rm -f 03_model/plots/*.png
	rm -f 06_validation/plots/*.png
	@echo "Data files removed."

clean-all: clean clean-data
	@echo "Complete cleanup finished."

.DEFAULT_GOAL := help