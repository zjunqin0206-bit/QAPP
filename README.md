# QAPP

QAPP is organized as a multi-module project with separate backend and deep learning components.

## Structure

- `back/`: Java backend module
- `dl/`: Python deep learning module
- `dl/service/`: deployable training and prediction API
- `dl/prototype/`: local prototype scripts used during model exploration

## DL Module

The Python DL module contains two layers:

1. `prototype`
   Used for local experimentation with data loading, model training, and result validation.

2. `service`
   Used for the production-style training service. It supports:
   - loading data from MySQL
   - configurable hyperparameters
   - training job submission and polling
   - prediction
   - scientific-style plot generation

## Runtime Notes

The deployable Python service runs with FastAPI and PyTorch.
The current service entry script is `dl/service/entrypoint.sh`.
