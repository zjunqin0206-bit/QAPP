# QAPP

QAPP is organized as a multi-module project with separate backend, frontend, and deep learning components.

## Structure

- `back/`: Java backend module
- `front/`: Vue frontend module
- `dl/`: Python deep learning module
- `dl/service/`: deployable training and prediction API
- `dl/prototype/`: local prototype scripts used during model exploration

## Frontend Module

The `front/` module contains the web interface for:

- user authentication
- Iris data management
- training task submission and progress tracking
- training result viewing and plot display
- saved model selection and prediction

The current frontend stack is based on Vue 3 and Vite.

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

- `back/` provides authentication and Iris data APIs.
- `dl/service/` provides training and prediction APIs.
- `front/` consumes both services and should be configured with the proper proxy targets or environment variables.
