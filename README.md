# 🏦 Banking Modern Data Stack – Real-Time Data Engineering Project

![Snowflake](https://img.shields.io/badge/Snowflake-29B5E8?logo=snowflake\&logoColor=white)
![dbt](https://img.shields.io/badge/dbt-FF694B?logo=dbt\&logoColor=white)
![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?logo=apacheairflow\&logoColor=white)
![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-231F20?logo=apachekafka\&logoColor=white)
![Debezium](https://img.shields.io/badge/Debezium-EF3B2D?logo=apache\&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python\&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker\&logoColor=white)
![CI/CD](https://img.shields.io/badge/CI%2FCD-000000?logo=githubactions\&logoColor=white)

---

## 📌 Project Overview

This project implements an **end-to-end real-time banking data platform** using a **modern data stack**. It is designed to **mirror how real financial institutions ingest, process, store, and analyze transactional data at scale**.

Instead of relying on static datasets, the system **generates live banking activity**, captures database changes in real time, and processes them through **streaming, warehousing, orchestration, and analytics layers**.

**Key goals of the project:**

* Simulate a realistic banking OLTP system
* Capture **Change Data Capture (CDC)** in real time
* Apply **Medallion Architecture (Bronze → Silver → Gold)**
* Build **analytics-ready fact & dimension models**
* Track historical changes using **SCD Type 2**
* Automate everything with **Airflow & CI/CD**

---

## 🏗️ High-Level Architecture

<img alt="Architecture" src="https://github.com/user-attachments/assets/7521ea8a-451e-46ff-9db0-71dd6ddf8181" />

### 🔄 End-to-End Flow

1. **PostgreSQL (OLTP)** – Simulated banking system (customers, accounts, transactions)
2. **Kafka + Debezium** – Capture inserts, updates, deletes via CDC
3. **MinIO (S3-compatible)** – Durable raw data landing zone (Parquet)
4. **Apache Airflow** – Orchestrates ingestion, snapshots, transformations
5. **Snowflake** – Cloud data warehouse (Bronze / Silver / Gold)
6. **dbt** – Transformations, tests, incremental models, SCD Type 2
7. **Power BI** – Real-time analytics via DirectQuery

---

## 🏦 1. Data Source – OLTP Banking System (PostgreSQL)

The pipeline begins with a **PostgreSQL transactional database**, simulating a real banking core system:

* 👥 **customers**
* 💼 **accounts**
* 💸 **transactions**

Synthetic data is generated using **Python + Faker**, mimicking real banking behavior such as deposits, withdrawals, transfers, and account updates.

**Why PostgreSQL?**

* ACID-compliant transactions
* Strong consistency guarantees
* Relational schema suitable for financial data

---

## ⚡ 2. Real-Time Streaming – Kafka + Debezium (CDC)

To avoid batch polling and data loss, the project uses **Change Data Capture**:

* **Debezium** listens to PostgreSQL WAL logs
* **Kafka** streams every insert, update, and delete event

This ensures:

* Near real-time data availability
* No missed changes
* Exactly-once processing semantics downstream

---

## 🪣 3. Object Storage – MinIO (S3-Compatible)

A Kafka consumer writes CDC events into **MinIO**, acting as a **durable landing zone**:

* Parquet format for efficient storage
* Separate folders per table
* Acts as the **Bronze layer entry point**

This decouples streaming from warehousing and allows replayability.

---

## 🔁 4. Orchestration – Apache Airflow

Apache Airflow automates the entire data lifecycle:

* Ingests data from MinIO → Snowflake (Bronze)
* Runs incremental and snapshot-based pipelines
* Handles retries, failures, and scheduling

DAGs are fully containerized and production-oriented.

---

## ❄️ 5. Data Warehouse – Snowflake (Medallion Architecture)

The warehouse follows the **Medallion Architecture**:

### 🥉 Bronze Layer

* Raw ingested data
* Minimal transformations
* Preserves source fidelity

### 🥈 Silver Layer

* Cleaned and typed data
* Deduplicated CDC events
* Business logic applied

### 🥇 Gold Layer

* Star schema
* Fact & dimension tables
* Optimized for BI & analytics

---

## 🛠 6. Transformations – dbt & SCD Type 2

dbt is responsible for all transformations:

* Staging models
* Incremental fact tables
* Snapshot-based **Slowly Changing Dimensions (Type 2)**
* Data quality tests

### 📘 SCD Type 2 Explained

When a customer or account attribute changes:

* Old record → `is_current = false`
* New record → inserted with new validity range

This allows **full historical analysis**, a critical banking requirement.

---

## 🚀 7. CI/CD & DevOps

The project follows production-grade DevOps practices:

* 🐳 **Docker & Docker Compose** – Fully containerized stack
* 🔐 **Secrets management** – `.env` + GitHub Secrets
* 🤖 **GitHub Actions**

  * CI: dbt compile, tests
  * CD: Deploy DAGs and dbt models

---

## 📊 8. Analytics – Power BI


<img alt="Dashboard" src="" />

Power BI connects directly to Snowflake using **DirectQuery**:

* Real-time dashboards
* No manual refresh
* Queries Gold models directly

### Dashboard Metrics

* Total customers
* Account balances
* Transaction volumes
* Customer activity ranking
* Fraud-like behavior patterns

---

## 📂 Repository Structure

```text
realtime-banking-project/
├── banking_dbt/              # dbt models, marts, snapshots
├── docker/                   # Airflow DAGs
├── consumer/                 # Kafka → MinIO consumer
├── data-generator/           # Faker-based OLTP simulator
├── kafka-debezium/           # CDC connectors
├── postgres/                 # OLTP schema
├── .github/workflows/        # CI/CD pipelines
├── docker-compose.yml
└── README.md
```

---

## 🧠 Skills Demonstrated

**Data Engineering**

* Kafka streaming & CDC
* Snowflake warehousing
* Airflow orchestration
* dbt modeling

**Data Modeling**

* Star schema
* Fact & dimension tables
* SCD Type 2

**DevOps**

* Docker
* CI/CD pipelines
* Secrets management

**Programming & Analytics**

* Python
* SQL
* Jinja / dbt
* Power BI

---

## 👤 Author

**Eric Tchindje**
🔗 LinkedIn: [https://www.linkedin.com/in/eric-tchindje/](https://www.linkedin.com/in/eric-tchindje/)
📧 Email: [tchindjeeric61@gmail.com](mailto:tchindjeeric61@gmail.com)
