## Zoom Car Data Processing Pipeline (PySpark + Docker + Jenkins)

This repo simulates a **Zoom Car**-style data engineering pipeline, but instead of Databricks it uses:

- **PySpark (local mode)** inside **Docker**
- **Jenkins Declarative Pipeline** for full automation
- **Single daily JSON file** as the source (bookings + customers together)

Jenkins is responsible for **everything**:

- Building the Docker image
- Running the PySpark ETL with a given date
- Producing final Parquet tables
- Cleaning the Jenkins workspace at the end (no manual cleanup)

---

## 1. Data Model (Single JSON File)

Daily data lands in `data/raw/` as a single JSON file:

- **Pattern**: `zoom_car_events_yyyymmdd.json`
- **Example**: `zoom_car_events_20260101.json`

Each JSON record contains **both booking and customer fields**:

- **Booking fields**: `booking_id`, `customer_id`, `start_time`, `end_time`, `booking_status`, `booking_date`, `car_type`, `pickup_city`
- **Customer fields**: `customer_name`, `email`, `phone`, `customer_status`, `signup_date`

---

## 2. Processing Steps (PySpark Scripts)

All logic lives in `src/` and runs inside Docker.

- **`main_pipeline.py`**
  - Entry point called by Jenkins / Docker.
  - Accepts `--run-date` (format `YYYY-MM-DD`). If empty → uses **today**.
  - Figures out the correct raw JSON filename and orchestrates steps.

- **`process_data.py`**
  - Reads the daily JSON from `data/raw/`.
  - **Validations & Cleaning**:
    - Drops records with null `booking_id` / `customer_id`.
    - Validates `booking_date` and `signup_date` formats.
    - Enforces valid booking statuses: `['created', 'in_progress', 'completed', 'cancelled']`.
    - Validates email with a regex.
    - Standardizes `customer_status` values (e.g. `ACTIVE`, `active`, `Active` → `ACTIVE`).
  - Writes **staging Parquet tables**:
    - `data/staging/bookings`
    - `data/staging/customers`

- **`transform_merge.py`**
  - **Transformations**:
    - Parses `start_time` and `end_time`.
    - Calculates `booking_duration_minutes`.
    - Normalizes phone numbers to `+91XXXXXXXXXX` style (for Indian numbers).
    - Calculates `customer_tenure_days` using `signup_date` and current date.
  - **Merge / Upsert logic (Parquet-based, Databricks-like)**:
    - **Bookings**
      - If `booking_id` already exists → **update** with the latest record.
      - If new `booking_id` → **insert**.
      - If `booking_status == 'cancelled'` → **delete** that booking.
      - Final table: `data/final/bookings`
    - **Customers**
      - Upsert on `customer_id` (no deletes here).
      - Final table: `data/final/customers`

---

## 3. Docker Setup

- **`Dockerfile`**
  - Uses `python:3.11-slim`.
  - Installs `pyspark` and dependencies from `requirements.txt`.
  - Default command: runs `src/main_pipeline.py` (you can override in Jenkins).

- **Local test (optional)**:

```bash
docker build -t zoomcar-etl .
docker run --rm -v %cd%:/app zoomcar-etl python src/main_pipeline.py --run-date 2026-01-01
```

> On Windows PowerShell you may need: `-v ${PWD}:/app` or run from Git Bash with `$(pwd)`.

---

## 4. Jenkins CI/CD Pipeline (Full Automation)

The **`Jenkinsfile`** defines a declarative pipeline that:

- Has a parameter **`RUN_DATE`** (`YYYY-MM-DD`). If left empty, the pipeline uses today’s date.
- **Stages**:
  1. **Checkout**: Gets this repo.
  2. **Build Docker Image**: Builds `zoomcar-etl`.
  3. **Run ETL**: Runs the Docker container with `RUN_DATE`.
  4. (Optional) Archive output Parquet files as build artifacts.

- **Post Actions**:
  - Uses `cleanWs()` so that **Jenkins clears the workspace at the end**.
  - That means code/data are removed from the workspace; on the next run Jenkins checks out fresh code again.

---

## 5. Folder Structure

```text
.
├── Dockerfile
├── Jenkinsfile
├── README.md
├── requirements.txt
├── data
│   ├── raw
│   │   └── zoom_car_events_20260101.json     # sample daily file (bookings + customers)
│   ├── staging
│   │   ├── bookings                          # created by Spark
│   │   └── customers                         # created by Spark
│   └── final
│       ├── bookings                          # created by Spark
│       └── customers                         # created by Spark
└── src
    ├── __init__.py
    ├── config.py
    ├── utils.py
    ├── process_data.py
    ├── transform_merge.py
    └── main_pipeline.py
```

---

## 6. How Jenkins Runs Everything (Step by Step)

1. **You trigger the Jenkins job** (manually or via schedule) and give a `RUN_DATE` (or leave it empty).
2. **Jenkins checks out** this repo into its workspace.
3. Jenkins **builds the Docker image** using `Dockerfile`.
4. Jenkins **runs the container**, mounting the workspace and calling:

   ```bash
   python src/main_pipeline.py --run-date ${RUN_DATE}
   ```

5. The PySpark job:
   - Reads `data/raw/zoom_car_events_yyyymmdd.json`.
   - Validates and loads into staging tables.
   - Applies transformations and merge logic.
   - Writes updated Parquet tables into `data/final`.
6. Jenkins (optionally) archives the `data/final` folder as build artifacts.
7. Jenkins **cleans the workspace** with `cleanWs()` so your folders are empty at the end.

---

## 7. Notes / Customization

- If you want to change the raw file pattern or data schema, update:
  - `src/config.py` (paths, file pattern)
  - `src/process_data.py` (schema + validations)
- If you later move to **Delta Lake** or **Databricks**, most PySpark logic can stay the same; you would mainly switch the write/merge code.

