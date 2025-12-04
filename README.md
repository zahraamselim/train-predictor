# Intelligent Level Crossing Control System

High school capstone project implementing ML-based railway crossing control with comprehensive performance metrics.

## Project Overview

This system uses SUMO traffic simulation to design and test an intelligent railway level crossing control system. The system:

- Predicts train arrival time using machine learning
- Controls gates with optimal timing
- Notifies intersections for vehicle rerouting decisions
- Recommends engine-off periods to save fuel and reduce emissions
- Tracks comprehensive performance metrics
- Deploys to Arduino hardware for physical implementation

## System Architecture

```
.
├── docker
│   ├── docker-compose.yml
│   └── Dockerfile
├── hardware
│   ├── diagram.json
│   ├── exporters
│   ├── libraries.txt
│   ├── README.md
│   └── sketch.ino
├── Makefile
├── ml
│   ├── config.yaml
│   ├── data.py
│   ├── __init__.py
│   ├── model.py
│   ├── network.py
│   └── README.md
├── outputs
│   ├── data/
│   ├── metrics/
│   ├── models/
│   ├── plots/
│   └── results/
├── README.md
├── requirements.txt
├── simulation
│   ├── config.yaml
│   ├── controller.py
│   ├── __inti__.py
│   ├── metrics.py
│   ├── network.py
│   └── README.md
├── thresholds
│   ├── analyzer.py
│   ├── collector.py
│   ├── config.yaml
│   ├── __init__.py
│   ├── network.py
│   └── README.md
├── utils
│   ├── __init__.py
│   ├── logger.py
└── view.xml
```
