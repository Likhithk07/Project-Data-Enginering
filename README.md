# Batch Data Processing Pipeline

A small, reproducible data-engineering project that demonstrates a batch-style taxi trip analytics pipeline using Kafka, Spark, Python, and Docker Compose.

The repository is intentionally compact, but it now goes beyond a skeleton: it includes a CSV dataset, a Kafka producer that publishes trip records, and a Spark batch job that cleans, enriches, aggregates, ranks, and exports analytical outputs.

## What this project is about

This project simulates a simplified batch-processing architecture for NYC-style taxi trip data:

1. **Ingestion**: a Python Kafka producer reads trip records from `data/sample_data.csv` and publishes them as JSON messages.
2. **Processing**: a Spark job reads the batch CSV input, validates the rows, creates derived features, and produces analytics-ready tables.
3. **Aggregation**: Spark calculates hourly demand, top pickup locations, route profitability, payment mix, and rolling revenue trends.
4. **Output**: generated CSV outputs are written to the local `output/` folder through a Docker volume.

This is suitable for demonstrating core batch data engineering concepts such as containerized services, reproducible execution, schema-based loading, data quality filtering, feature engineering, and business-focused aggregation.

## Architecture

```text
sample CSV data
      |
      |-- optional ingestion demo --> Kafka topic: taxi_trips
      |
      `-- batch processing -------> Spark job -------> output CSV datasets
```

The current implementation uses local files for Spark batch input so the processing job is easy to run and test. Kafka is included to demonstrate ingestion and service orchestration, while Spark performs the analytical batch processing.

## Repository structure

```text
.
├── Dockerfile                 # Python image used by the optional producer service
├── README.md                  # Project documentation
├── data/
│   └── sample_data.csv        # Taxi trip sample data
├── docker-compose.yml         # Kafka, Zookeeper, producer profile, and Spark services
├── kafka/
│   └── producer.py            # CSV-to-Kafka JSON producer
├── requirements.txt           # Python dependencies
└── spark/
    └── spark_job.py           # Spark cleaning, feature engineering, and aggregation job
```

## Prerequisites

Install the following before running the project:

- Docker
- Docker Compose v2
- Git, if cloning from a remote repository

You do **not** need to install Spark or Kafka locally. Docker Compose provides those services.

## Installation

Clone the repository and move into the project folder:

```bash
git clone <your-repository-url>
cd data-engineering-batch-pipeline
```

Or, if you already have the project folder locally, open a terminal in the repository root.

## How to run the Spark batch job

Run the main batch job with:

```bash
docker compose up spark
```

Spark will read `data/sample_data.csv`, process the dataset, print sample results to the terminal, and write CSV outputs into `output/`.

To remove previous containers and rerun from a clean state:

```bash
docker compose down
docker compose up spark
```

## How to run the Kafka ingestion demo

Kafka ingestion is optional because the Spark batch job reads from the sample CSV. To start Kafka and publish records into the `taxi_trips` topic, run:

```bash
docker compose --profile ingest up producer
```

The producer will:

- read `data/sample_data.csv`,
- convert each row to JSON,
- publish records to Kafka topic `taxi_trips`,
- print a confirmation for each sent record.

## What the Spark job does

The Spark job in `spark/spark_job.py` performs several non-trivial processing steps.

### 1. Schema-based loading

The job defines an explicit schema for trip timestamps, location IDs, passenger counts, distances, fares, tips, and payment types. This avoids relying on automatic type inference.

### 2. Data cleaning and validation

Invalid records are removed, including rows with:

- missing pickup or drop-off timestamps,
- non-positive fares,
- non-positive trip distances,
- invalid passenger counts,
- non-positive trip durations.

### 3. Feature engineering

The job creates analytics features such as:

- `trip_minutes`, calculated from pickup and drop-off timestamps,
- `total_amount`, combining fare and tip,
- `fare_per_mile`, showing trip revenue efficiency,
- `tip_rate`, showing tip as a proportion of fare,
- `pickup_date` and `pickup_hour`, for time-based analysis,
- `day_part`, such as morning, midday, evening peak, and late night,
- `trip_distance_band`, such as short, medium, and long.

### 4. Aggregations and analytics

The job produces multiple output datasets:

| Output folder | Description |
| --- | --- |
| `output/cleaned_trips/` | Cleaned and enriched trip-level records |
| `output/hourly_demand/` | Trip count, revenue, average fare per mile, and average duration by date and hour |
| `output/top_locations_by_day/` | Top pickup zones per day using Spark window ranking |
| `output/payment_mix/` | Payment behavior by payment type and trip distance band |
| `output/route_profitability/` | Route-level revenue and efficiency metrics |
| `output/rolling_hourly_revenue/` | Rolling three-period revenue trend over hourly demand results |

## Expected outputs

After running the Spark service, you should see an `output/` directory with Spark-generated CSV folders. Spark writes partitioned output directories, so each result will look similar to this:

```text
output/hourly_demand/
├── _SUCCESS
└── part-00000-....csv
```

Open the `part-*.csv` files to inspect the results.

## Running locally without Docker

For quick development, you can also run the Python components locally.

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the Spark job:

```bash
spark-submit spark/spark_job.py
```

For the Kafka producer, ensure Kafka is running and set the bootstrap server if needed:

```bash
export KAFKA_BOOTSTRAP_SERVERS=localhost:9092
python kafka/producer.py
```

## Configuration

The Kafka producer supports environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `KAFKA_BOOTSTRAP_SERVERS` | `localhost:9092` | Kafka broker address |
| `KAFKA_TOPIC` | `taxi_trips` | Topic to publish records to |
| `DATA_PATH` | `data/sample_data.csv` | CSV input path |
| `SEND_DELAY_SECONDS` | `0.1` | Delay between messages |

The Spark job uses these paths inside Docker:

| Path | Purpose |
| --- | --- |
| `/data/sample_data.csv` | Mounted input data |
| `/output` | Mounted analytics output folder |

## Troubleshooting

### Spark cannot find the input CSV

Make sure you are running Docker Compose from the repository root and that `data/sample_data.csv` exists.

### Kafka producer cannot connect

Kafka can take a short time to become ready. Re-run the producer command after the broker finishes starting. When running inside Docker Compose, use `KAFKA_BOOTSTRAP_SERVERS=kafka:9092`. When running from your host machine, use `localhost:9092` only if Kafka is configured for host access.

### Output folder contains many generated files

That is normal Spark behavior. Each output dataset is written as a folder containing one or more `part-*.csv` files and a `_SUCCESS` marker.

## Future improvements

Possible extensions include:

- replacing the local CSV batch source with scheduled HDFS or object storage input,
- adding a Kafka consumer that persists raw events before Spark processing,
- adding automated tests for data quality rules,
- adding Airflow or cron-based scheduling,
- publishing the aggregated outputs to a dashboard or database,
- adding a larger NYC Taxi dataset for more realistic performance testing.

## License

This project is for academic and learning purposes.
