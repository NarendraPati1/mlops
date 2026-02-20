import argparse
import logging
import sys
import time
import json
import os
import yaml
import numpy as np
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(description="Mini MLOps Pipeline")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--config", required=True, help="Path to config YAML")
    parser.add_argument("--output", required=True, help="Path to output JSON")
    parser.add_argument("--log-file", required=True, help="Path to log file")
    return parser.parse_args()


def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def load_config(config_path):
    if not os.path.exists(config_path):
        raise FileNotFoundError("Config file not found")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    if config is None:
        raise ValueError("Config file is empty")

    required_keys = ["seed", "window", "version"]

    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing config key: {key}")

    if not isinstance(config["seed"], int):
        raise ValueError("Seed must be integer")

    if not isinstance(config["window"], int) or config["window"] <= 0:
        raise ValueError("Window must be positive integer")

    if not isinstance(config["version"], str):
        raise ValueError("Version must be string")

    return config


def load_data(input_path):
    if not os.path.exists(input_path):
        raise FileNotFoundError("Input CSV file not found")

    try:
        df = pd.read_csv(input_path)
    except Exception:
        raise ValueError("Invalid CSV file format")

    if df.empty:
        raise ValueError("Input CSV file is empty")

    if "close" not in df.columns:
        raise ValueError("Missing required column: close")

    return df


def write_error(output_path, version, message):
    error_output = {
        "version": version,
        "status": "error",
        "error_message": message
    }
    with open(output_path, "w") as f:
        json.dump(error_output, f, indent=2)


def main():
    start_time = time.time()
    args = parse_args()
    setup_logging(args.log_file)

    logging.info("Job started")

    try:
        # 1. Load Config
        config = load_config(args.config)
        seed = config["seed"]
        window = config["window"]
        version = config["version"]

        np.random.seed(seed)

        logging.info(f"Config loaded: seed={seed}, window={window}, version={version}")

        # 2. Load Data
        df = load_data(args.input)
        rows_processed = len(df)

        logging.info(f"Data loaded: {rows_processed} rows")

        # 3. Rolling Mean
        df["rolling_mean"] = df["close"].rolling(window=window).mean()
        logging.info(f"Rolling mean calculated with window={window}")

        # 4. Signal Generation
        df["signal"] = (df["close"] > df["rolling_mean"]).astype(int)
        logging.info("Signals generated")

        # 5. Metrics Calculation
        signal_rate = df["signal"].mean()

        latency_ms = int((time.time() - start_time) * 1000)

        logging.info(
            f"Metrics: signal_rate={signal_rate:.4f}, rows_processed={rows_processed}"
        )

        output = {
            "version": version,
            "rows_processed": rows_processed,
            "metric": "signal_rate",
            "value": round(float(signal_rate), 4),
            "latency_ms": latency_ms,
            "seed": seed,
            "status": "success"
        }

        with open(args.output, "w") as f:
            json.dump(output, f, indent=2)

        print(json.dumps(output, indent=2))
        logging.info(f"Job completed successfully in {latency_ms}ms")

        sys.exit(0)

    except Exception as e:
        logging.error(str(e))

        version = "unknown"
        if os.path.exists(args.config):
            try:
                version = yaml.safe_load(open(args.config))["version"]
            except Exception:
                pass

        write_error(args.output, version, str(e))
        print(f"Error: {e}")

        sys.exit(1)


if __name__ == "__main__":
    main()
