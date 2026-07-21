import os
import sys
import time
import shutil
import urllib.request


def setup_windows_hadoop():
    """Auto-configures Hadoop winutils for Windows execution if missing."""
    if sys.platform.startswith("win"):
        hadoop_dir = os.environ.get("HADOOP_HOME") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "hadoop")
        bin_dir = os.path.join(hadoop_dir, "bin")
        winutils_path = os.path.join(bin_dir, "winutils.exe")

        if not os.path.exists(winutils_path):
            os.makedirs(bin_dir, exist_ok=True)
            print("Windows OS detected. Auto-downloading winutils for local Spark file operations...")
            winutils_url = "https://raw.githubusercontent.com/cdarlint/winutils/master/hadoop-3.3.5/bin/winutils.exe"
            hadoop_dll_url = "https://raw.githubusercontent.com/cdarlint/winutils/master/hadoop-3.3.5/bin/hadoop.dll"
            try:
                urllib.request.urlretrieve(winutils_url, winutils_path)
                urllib.request.urlretrieve(hadoop_dll_url, os.path.join(bin_dir, "hadoop.dll"))
            except Exception as e:
                print(f"Note: winutils auto-download skipped ({e}).")

        os.environ["HADOOP_HOME"] = hadoop_dir
        os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")


setup_windows_hadoop()
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, DoubleType, TimestampType
)
from pyspark.sql.functions import (
    col, when, lit, round as _round, year, month, sum as _sum, avg, count,
    rand, concat, element_at, array, from_unixtime, date_format
)


def get_spark_session():
    spark = SparkSession.builder \
        .appName("SparkArchitectureAndOptimizationDemo") \
        .master("local[*]") \
        .config("spark.sql.shuffle.partitions", "8") \
        .config("spark.driver.memory", "2g") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    print(f"Spark Version: {spark.version} | Master: {spark.sparkContext.master}")
    return spark


def generate_dataset(spark, raw_dir, num_records=100000):
    os.makedirs(raw_dir, exist_ok=True)
    csv_path = os.path.join(raw_dir, "transactions.csv")
    parquet_path = os.path.join(raw_dir, "transactions.parquet")

    categories = array(lit("Electronics"), lit("Clothing"), lit("Home & Kitchen"), lit("Books"), lit("Beauty"), lit("Sports"))
    payment_methods = array(lit("Credit Card"), lit("PayPal"), lit("Debit Card"), lit("UPI"))
    cities = array(lit("New York"), lit("San Francisco"), lit("London"), lit("Tokyo"), lit("Berlin"), lit("Sydney"), lit("Mumbai"))

    base_epoch = 1735689600  # 2025-01-01 00:00:00

    df = spark.range(1, num_records + 1) \
        .withColumn("transaction_id", concat(lit("TXN-"), (col("id") + 1000000).cast(StringType()))) \
        .withColumn("customer_id", (rand(seed=42) * 9500 + 1001).cast(IntegerType())) \
        .withColumn("timestamp_str", date_format(from_unixtime(lit(base_epoch) + (rand(seed=43) * 31536000).cast(IntegerType())), "yyyy-MM-dd HH:mm:ss")) \
        .withColumn("category", element_at(categories, (rand(seed=44) * 6 + 1).cast(IntegerType()))) \
        .withColumn("amount", when(rand(seed=45) > 0.05, _round(rand(seed=46) * 1495 + 5, 2)).otherwise(lit(None).cast(DoubleType()))) \
        .withColumn("quantity", when(rand(seed=47) > 0.05, (rand(seed=48) * 9 + 1).cast(IntegerType())).otherwise(lit(None).cast(IntegerType()))) \
        .withColumn("payment_method", when(rand(seed=49) < 0.1, lit(None).cast(StringType())).otherwise(element_at(payment_methods, (rand(seed=50) * 4 + 1).cast(IntegerType())))) \
        .withColumn("city", element_at(cities, (rand(seed=51) * 7 + 1).cast(IntegerType()))) \
        .drop("id")

    if os.path.exists(csv_path):
        shutil.rmtree(csv_path)
    print(f"Writing raw CSV dataset to: {csv_path}")
    df.write.option("header", "true").csv(csv_path)

    if os.path.exists(parquet_path):
        shutil.rmtree(parquet_path)
    print(f"Writing raw Parquet dataset to: {parquet_path}")
    df.write.parquet(parquet_path)

    return csv_path, parquet_path


def read_data(spark, csv_path, parquet_path):
    schema = StructType([
        StructField("transaction_id", StringType(), True),
        StructField("customer_id", IntegerType(), True),
        StructField("timestamp_str", StringType(), True),
        StructField("category", StringType(), True),
        StructField("amount", DoubleType(), True),
        StructField("quantity", IntegerType(), True),
        StructField("payment_method", StringType(), True),
        StructField("city", StringType(), True)
    ])

    t0 = time.time()
    count_csv = spark.read.option("header", "true").option("inferSchema", "true").csv(csv_path).count()
    csv_infer_time = time.time() - t0

    t0 = time.time()
    spark.read.option("header", "true").schema(schema).csv(csv_path).count()
    csv_explicit_time = time.time() - t0

    t0 = time.time()
    df_parquet = spark.read.parquet(parquet_path)
    df_parquet.count()
    parquet_time = time.time() - t0

    print(f"Read performance ({count_csv:,} rows):")
    print(f"  - CSV with inferSchema:     {csv_infer_time:.4f}s")
    print(f"  - CSV with explicit schema: {csv_explicit_time:.4f}s")
    print(f"  - Parquet (schema-on-read): {parquet_time:.4f}s")

    print("\nParquet Schema:")
    df_parquet.printSchema()

    return df_parquet


def clean_and_transform(df):
    print("Initial null value counts:")
    df.select([count(when(col(c).isNull(), c)).alias(c) for c in ["amount", "quantity", "payment_method"]]).show()

    df_cleaned = df.fillna({
        "amount": 0.0,
        "quantity": 1,
        "payment_method": "Unknown"
    })

    df_transformed = df_cleaned \
        .withColumnRenamed("amount", "total_amount") \
        .withColumnRenamed("city", "location") \
        .withColumn("timestamp", col("timestamp_str").cast(TimestampType())) \
        .drop("timestamp_str") \
        .withColumn("unit_price", _round(col("total_amount") / col("quantity"), 2)) \
        .withColumn("order_size_category",
                    when(col("quantity") >= 8, "Bulk")
                    .when(col("quantity") >= 4, "Medium")
                    .otherwise("Small")) \
        .withColumn("is_high_value", when(col("total_amount") > 500, True).otherwise(False)) \
        .withColumn("tx_year", year(col("timestamp"))) \
        .withColumn("tx_month", month(col("timestamp")))

    print("Transformed DataFrame Sample:")
    df_transformed.show(5, truncate=False)

    return df_transformed


def aggregate_data(spark, df):
    sf_high_val = df.filter((col("total_amount") > 100) & (col("location") == "San Francisco"))
    print(f"Narrow Filter Result (SF orders > $100): {sf_high_val.count():,} rows")

    category_summary = df.groupBy("category", "order_size_category") \
        .agg(
            count("transaction_id").alias("total_transactions"),
            _round(_sum("total_amount"), 2).alias("revenue"),
            _round(avg("total_amount"), 2).alias("avg_order_value")
        ) \
        .orderBy(col("revenue").desc())

    print("\n--- Category Revenue Summary (GroupBy Shuffle) ---")
    category_summary.show(5, truncate=False)

    tiers = array(lit("Gold"), lit("Silver"), lit("Bronze"), lit("Platinum"))
    df_tiers = spark.range(1001, 11001) \
        .withColumnRenamed("id", "customer_id") \
        .withColumn("customer_id", col("customer_id").cast(IntegerType())) \
        .withColumn("membership_tier", concat(lit("Tier_"), element_at(tiers, (rand(seed=99) * 4 + 1).cast(IntegerType()))))

    tier_revenue = df.join(df_tiers, on="customer_id", how="inner") \
        .groupBy("membership_tier") \
        .agg(_round(_sum("total_amount"), 2).alias("total_revenue")) \
        .orderBy(col("total_revenue").desc())

    print("\n--- Customer Tier Revenue (Join Shuffle) ---")
    tier_revenue.show()


def explain_physical_plans(spark, csv_path, parquet_path):
    print("Parquet Query Physical Plan (Predicate & Projection Pushdown):")
    spark.read.parquet(parquet_path) \
        .filter(col("category") == "Electronics") \
        .select("transaction_id", "category", "amount") \
        .explain(mode="formatted")


def benchmark_formats(spark, csv_path, parquet_path):
    def get_dir_size(path):
        return sum(os.path.getsize(os.path.join(dp, f)) for dp, dn, fn in os.walk(path) for f in fn) / (1024 * 1024)

    csv_size = get_dir_size(csv_path)
    parquet_size = get_dir_size(parquet_path)

    print(f"Storage Footprint -> CSV: {csv_size:.2f} MB | Parquet: {parquet_size:.2f} MB (Compression: {csv_size/parquet_size:.2f}x)")

    t0 = time.time()
    c_csv = spark.read.option("header", "true").csv(csv_path).filter((col("category") == "Electronics") & (col("amount").cast("double") > 500)).count()
    csv_time = time.time() - t0

    t0 = time.time()
    c_pq = spark.read.parquet(parquet_path).filter((col("category") == "Electronics") & (col("amount") > 500)).count()
    parquet_time = time.time() - t0

    print(f"Query Filter Speed ({c_pq:,} matching rows):")
    print(f"  - CSV Query Time:     {csv_time:.4f}s")
    print(f"  - Parquet Query Time: {parquet_time:.4f}s (Speedup: {csv_time/parquet_time:.2f}x faster)")


def save_output(df, output_dir):
    out_parquet = os.path.join(output_dir, "transformed_transactions_parquet")
    out_csv = os.path.join(output_dir, "transformed_transactions_csv")

    if os.path.exists(out_parquet):
        shutil.rmtree(out_parquet)
    if os.path.exists(out_csv):
        shutil.rmtree(out_csv)

    print(f"Saving partitioned Parquet data to: {out_parquet}")
    df.write.partitionBy("category").parquet(out_parquet)

    print(f"Saving coalesced CSV data to: {out_csv}")
    df.coalesce(2).write.option("header", "true").csv(out_csv)


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    raw_dir = os.path.join(base_dir, "data", "raw")
    output_dir = os.path.join(base_dir, "data", "output")

    print("Step 1: Initializing Spark Session")
    spark = get_spark_session()
    
    try:
        print("\nStep 2: Generating Synthetic Dataset (100,000 records)")
        csv_path, parquet_path = generate_dataset(spark, raw_dir)

        print("\nStep 3: Reading Data & Schema Verification")
        df_raw = read_data(spark, csv_path, parquet_path)

        print("\nStep 4: Data Cleaning & Transformations")
        df_clean = clean_and_transform(df_raw)

        print("\nStep 5: Aggregations & Shuffle Transformations")
        aggregate_data(spark, df_clean)

        print("\nStep 6: Catalyst Physical Plan Analysis")
        explain_physical_plans(spark, csv_path, parquet_path)

        print("\nStep 7: Benchmarking CSV vs Parquet Performance")
        benchmark_formats(spark, csv_path, parquet_path)

        print("\nStep 8: Exporting Pipeline Output")
        save_output(df_clean, output_dir)

        print("\nPipeline execution completed successfully.")

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
