.PHONY: help clean clean-data venv install

PYTHON = python3
VENV = .venv
BIN = $(VENV)/bin

help:
	@echo "Level Crossing System - Makefile Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make venv            Create virtual environment"
	@echo "  make install         Install dependencies"
	@echo ""
	@echo "Train Dataset Generation:"
	@echo "  make gen-train-demo      Generate demo train data (10 scenarios)"
	@echo "  make gen-train-small     Generate small train data (50 scenarios)"
	@echo "  make gen-train-full      Generate full train data (100 scenarios)"
	@echo "  make vis-train-demo      Visualize demo dataset (plots/graphs)"
	@echo "  make vis-train-data      Visualize full dataset (plots/graphs)"
	@echo "  make vis-train-sim       Run live train simulation (pygame)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean               Remove virtual environment"
	@echo "  make clean-data          Remove generated data files"
	@echo "  make clean-all           Remove everything (venv + data)"

venv:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo "Virtual environment created. Activate with: source $(BIN)/activate"

install: venv
	@echo "Installing dependencies..."
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt
	@echo "Dependencies installed."

gen-train-demo:
	@echo "Generating demo train dataset (10 scenarios)..."
	$(BIN)/python -c "import sys; sys.path.insert(0, '.'); import importlib; m = importlib.import_module('01_train_dataset.generate_dataset'); m.generate_dataset(num_scenarios=10, output_file='01_train_dataset/train_data_demo.csv')"

gen-train-small:
	@echo "Generating small train dataset (50 scenarios)..."
	$(BIN)/python -c "import sys; sys.path.insert(0, '.'); import importlib; m = importlib.import_module('01_train_dataset.generate_dataset'); m.generate_dataset(num_scenarios=50, output_file='01_train_dataset/train_data_small.csv')"

gen-train-full:
	@echo "Generating full train dataset (100 scenarios)..."
	$(BIN)/python -c "import sys; sys.path.insert(0, '.'); import importlib; m = importlib.import_module('01_train_dataset.generate_dataset'); m.generate_dataset(num_scenarios=100, output_file='01_train_dataset/train_data.csv')"

vis-train-demo:
	@echo "Visualizing demo train dataset..."
	$(BIN)/python 01_train_dataset/visualize_dataset.py 01_train_dataset/train_data_demo.csv

vis-train-data:
	@echo "Visualizing train dataset..."
	$(BIN)/python 01_train_dataset/visualize_dataset.py 01_train_dataset/train_data.csv

vis-train-sim:
	@echo "Running live train simulation..."
	$(BIN)/python 01_train_dataset/simulate_train.py

clean:
	@echo "Removing virtual environment..."
	rm -rf $(VENV)
	@echo "Virtual environment removed."

clean-data:
	@echo "Removing generated data files..."
	rm -f 01_train_dataset/*.csv
	rm -f 01_train_dataset/*.png
	@echo "Data files removed."

clean-all: clean clean-data
	@echo "Cleanup complete."