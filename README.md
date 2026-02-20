# Setup Instructions

## Install Dependencies
```bash
pip install -r requirements.txt
```

### Required Python Packages

- `pandas`
- `numpy`
- `pyyaml`

---

## Local Execution Instructions

### Run Locally
```bash
python run.py --input data.csv --config config.yaml \
  --output metrics.json --log-file run.log
```

### I have create my own data so if you want to test this on your choice of data please change the csv name.
This command:

- Loads configuration from `config.yaml`
- Sets the random seed for reproducibility
- Loads and validates `data.csv`
- Computes rolling mean using configured window
- Generates trading signals
- Calculates signal rate
- Writes results to `metrics.json`
- Logs execution details to `run.log`
- Prints final metrics to stdout

---

## Docker Instructions

### Build the Docker Image
```bash
docker build -t mlops-task .
```

### Run the Container
```bash
docker run --rm mlops-task
```

# Expected Output

## `metrics.json` Structure
```json
{
  "version": "v1",
  "rows_processed": 10000,
  "metric": "signal_rate",
  "value": 0.4990,
  "latency_ms": 127,
  "seed": 42,
  "status": "success"
}
```

### Field Descriptions

| Field | Description |
|---|---|
| `version` | Value extracted from `config.yaml` |
| `rows_processed` | Total number of rows in the dataset |
| `metric` | Always `"signal_rate"` |
| `value` | Computed signal rate (between 0 and 1) |
| `latency_ms` | Total execution time in milliseconds |
| `seed` | Seed value from configuration |
| `status` | `"success"` or `"error"` |

---
## Dependencies

The project requires the following Python packages:

| Package | Purpose |
|---|---|
| `pandas` | Loading the CSV dataset, validating data, computing rolling mean, and performing signal calculations |
| `numpy` | Setting a deterministic random seed and performing numerical operations |
| `pyyaml` | Reading and validating the `config.yaml` configuration file |

All dependencies are listed in `requirements.txt`.
