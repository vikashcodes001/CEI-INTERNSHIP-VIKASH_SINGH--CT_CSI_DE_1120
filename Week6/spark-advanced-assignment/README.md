# ⚡ Apache Spark Architecture & Efficient Data Processing Assignment

An enterprise-grade Apache Spark pipeline and architectural exploration demonstrating key distributed computing concepts, explicit schema enforcement, transformation strategies, optimization techniques (Predicate Pushdown & Column Projection), and file format comparisons (CSV vs. Parquet).

---

## 📂 Project Folder Structure

```
spark-advanced-assignment/
│── data/
│   └── dataset.csv
│── notebook/
│   └── spark_architecture.ipynb
│── output/
│   ├── results_csv/
│   └── results_parquet/
│── README.md
```

---

## 🏗️ 1. Spark Architecture Overview

### Key Architectural Components

```
                +---------------------------------------+
                |             Driver Node               |
                |  (SparkSession, DAGScheduler, Task)   |
                +-------------------+-------------------+
                                    |
                        Allocates   |   Monitors
                        Resources   v   Executors
                +---------------------------------------+
                |            Cluster Manager            |
                |       (YARN / Mesos / K8s / Local)    |
                +-------------------+-------------------+
                                    |
                +-------------------+-------------------+
                |                                       |
                v                                       v
    +-----------------------+               +-----------------------+
    |     Executor 1        |               |     Executor 2        |
    |  (Task 1)  (Task 2)   |               |  (Task 3)  (Task 4)   |
    |  [ In-Memory Cache ]  |               |  [ In-Memory Cache ]  |
    +-----------------------+               +-----------------------+
```

1. **Driver Node**: The master process executing the application `main()` method and holding the `SparkSession`. It converts code into a logical execution plan, constructs the **DAG**, breaks it down into stages and tasks, and schedules work across executors.
2. **Cluster Manager**: Acquires compute hardware resources (CPU cores and RAM) across the cluster (Standalone, YARN, Kubernetes, Mesos).
3. **Executors**: Worker processes executing assigned tasks, managing in-memory caching/storage partitions, and reporting task progress metrics to the Driver.

---

### Lazy Evaluation & Lineage Graph (DAG)

- **Lazy Evaluation**: Transformations (`select`, `filter`, `withColumn`, `groupBy`) do not execute immediately when defined. Instead, Spark registers them in a logical query plan.
- **Directed Acyclic Graph (DAG)**: When an **Action** (`show`, `count`, `collect`, `write`) is called, Spark analyzes the DAG using the Catalyst Optimizer to optimize execution (reordering filters via Predicate Pushdown and eliminating unused columns via Projection Pruning).
- **Fault Tolerance**: If an executor crashes mid-job, Spark uses the lineage recorded in the DAG to recompute only the missing data partitions rather than restarting the entire pipeline.

---

### Transformations vs. Actions

| Metric | Transformations | Actions |
| :--- | :--- | :--- |
| **Evaluation** | **Lazy** (recorded in DAG) | **Eager** (triggers physical execution) |
| **Return Value** | Returns a new `DataFrame` or `RDD` | Returns concrete results or writes data to storage |
| **Examples** | `filter()`, `select()`, `withColumn()`, `groupBy()` | `show()`, `count()`, `collect()`, `write.parquet()` |

---

## ⚡ 2. Transformations & Performance Optimizations

### Narrow vs. Wide Transformations

- **Narrow Transformations**: Operations where each input partition contributes to at most one output partition (e.g., `filter()`, `select()`, `withColumn()`). Executed locally in executor memory with zero network overhead.
- **Wide Transformations**: Operations requiring data from multiple input partitions (e.g., `groupBy()`, `join()`, `distinct()`). Triggers a **Shuffle Operation**, serializing and transmitting data across the network to group matching keys.

### Predicate Pushdown & Column Projection

- **Predicate Pushdown**: Pushes filtering logic down to the file source reader. When reading Parquet files, non-matching data block groups are skipped entirely based on file metadata.
- **Column Projection**: Ensures only columns required for computation are loaded into memory, reducing network and memory usage.

### File Format Comparison: CSV vs. Parquet

| Metric | CSV (Row-Based) | Parquet (Columnar) |
| :--- | :--- | :--- |
| **Storage Format** | Text-based, row-by-row | Binary columnar layout with block metadata |
| **Compression** | Low efficiency | High efficiency (Snappy / Gzip) |
| **Read Performance** | Slow (must parse every row & column) | Fast (reads only target columns & skips blocks) |
| **Predicate Pushdown** | Not supported | Fully supported |

---

## 🚀 3. Execution & Workflow

### Prerequisites
- Python 3.8+
- PySpark 3.x / 4.x
- Jupyter Notebook / JupyterLab

### Running the Notebook
Navigate to the `notebook/` folder and launch Jupyter:
```bash
cd notebook
jupyter notebook spark_architecture.ipynb
```

### Data Pipeline Steps Implemented:
1. **Schema Definition**: Explicit `StructType` definition for strict type enforcement.
2. **Data Reading**: Ingestion of `data/dataset.csv`.
3. **Cleaning & Null Handling**: Imputation using `.fillna({"amount": 0.0, "quantity": 1})`.
4. **Column Operations**: Column renaming (`withColumnRenamed`), type casting (`cast`), and derived column creation (`when`).
5. **Filtering & Aggregation**: Electronics filtering (Narrow) and Category summary aggregation (Wide).
6. **Physical Plan Inspection**: Query plan verification using `.explain()`.
7. **Output Storage**: Saving results in parallel to `output/results_csv/` and `output/results_parquet/`.
