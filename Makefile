.PHONY: help setup install clean \
	data-traffic data-train data-decisions data-all \
	ml-train ml-test \
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
	@echo "  make data-train-small    Generate small dataset (50 scenarios)"
	@echo "  make data-decisions      Generate decision data for ML (500 scenarios)"
	@echo "  make data-all            Generate all datasets"
	@echo ""
	@echo "Machine Learning:"
	@echo "  make ml-train            Train route optimizer model"
	@echo "  make ml-test             Test trained model"
	@echo ""
	@echo "Simulation:"
	@echo "  make simulate            Run pygame simulation"
	@echo ""
	@echo "Validation:"
	@echo "  make validate-all        Validate all generated data"
	@echo ""
	@echo "Complete Workflow:"
	@echo "  make workflow            Run complete pipeline: data -> ml -> validate"
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

data-train-small:
	@echo "Generating small train dataset (50 scenarios)..."
	$(BIN)/python -m data_generation.generate_train small

data-decisions:
	@echo "Generating decision data for ML..."
	$(BIN)/python -m data_generation.generate_decisions

data-all: data-traffic data-train data-decisions
	@echo "All datasets generated"

ml-train:
	@echo "Training route optimizer..."
	$(BIN)/python -m ml.route_optimizer

ml-test:
	@echo "Testing route optimizer..."
	$(BIN)/python -c "from ml.route_optimizer import RouteOptimizer; \
		opt = RouteOptimizer('ml/models/route_optimizer.pkl'); \
		result = opt.predict(45, 5, 'medium', 500, 1200); \
		print(f'Test prediction: {result}')"

simulate:
	@echo "Starting simulation..."
	$(BIN)/python -m simulation.main

validate-traffic:
	@echo "Validating traffic data..."
	$(BIN)/python -m data_generation.generate_traffic validate

validate-train:
	@echo "Validating train data..."
	$(BIN)/python -m data_generation.generate_train validate

validate-decisions:
	@echo "Validating decision data..."
	$(BIN)/python -m data_generation.generate_decisions validate

validate-all: validate-traffic validate-train validate-decisions
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