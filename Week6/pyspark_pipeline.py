import os
import sys

# Configure HADOOP_HOME for Windows local execution
hadoop_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hadoop")
os.environ["HADOOP_HOME"] = hadoop_dir
os.environ["PATH"] = os.path.join(hadoop_dir, "bin") + os.pathsep + os.environ.get("PATH", "")
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
from pyspark.sql.functions import col, when

# 1. Initialize SparkSession (Driver Node & Local Execution Mode)
spark = SparkSession.builder \
    .appName("StudentSparkLab") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")
print("Spark Session created successfully.")

# 2. Define Explicit Schema (Best practice for untyped inputs)
schema = StructType([
    StructField("transaction_id", StringType(), True),
    StructField("customer_id", IntegerType(), True),
    StructField("category", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("quantity", IntegerType(), True),
    StructField("city", StringType(), True),
    StructField("transaction_date", StringType(), True)
])

# Sample Dataset with Nulls
data = [
    ("T101", 101, "Electronics", 1200.50, 2, "San Francisco", "2025-01-15"),
    ("T102", 102, "Clothing", 45.00, 1, "New York", "2025-01-16"),
    ("T103", 103, "Electronics", None, 3, "London", "2025-01-17"),
    ("T104", 104, "Books", 15.99, None, "San Francisco", "2025-01-18"),
    ("T105", 105, "Home", 250.00, 1, "Tokyo", "2025-01-19"),
    ("T106", 106, "Clothing", 89.90, 2, "New York", "2025-01-20"),
    ("T107", 107, "Electronics", 650.00, 1, "San Francisco", "2025-01-21"),
    ("T108", 108, "Books", None, None, "London", "2025-01-22"),
]

# Create Initial DataFrame
raw_df = spark.createDataFrame(data, schema=schema)

# Save Raw Data to Files (CSV & Parquet)
raw_df.write.mode("overwrite").option("header", "true").csv("data/raw_csv")
raw_df.write.mode("overwrite").parquet("data/raw_parquet")

# 3. Read Data Files with Schema Handling
df_csv = spark.read.schema(schema).option("header", "true").csv("data/raw_csv")
df_parquet = spark.read.parquet("data/raw_parquet")

print("\n--- DataFrame Schema ---")
df_parquet.printSchema()

# 4. Handle Null Values
cleaned_df = df_parquet.fillna({
    "amount": 0.0,
    "quantity": 1
})

# 5. Modify DataFrame (Rename columns, cast data types, add new columns)
transformed_df = cleaned_df \
    .withColumnRenamed("amount", "total_amount") \
    .withColumnRenamed("city", "location") \
    .withColumn("quantity", col("quantity").cast("integer")) \
    .withColumn("total_price", col("total_amount") * col("quantity")) \
    .withColumn("is_expensive", when(col("total_amount") > 500, "Yes").otherwise("No"))

print("\n--- Transformed DataFrame ---")
transformed_df.show()

# 6. Narrow Transformation (Filtering & Column Selection)
filtered_df = transformed_df \
    .filter((col("category") == "Electronics") & (col("total_amount") > 100)) \
    .select("transaction_id", "category", "total_amount", "location")

print("\n--- Filtered Electronics Orders ---")
filtered_df.show()

# 7. Wide Transformation (GroupBy & Aggregation requiring Data Shuffle)
summary_df = transformed_df \
    .groupBy("category") \
    .sum("total_amount") \
    .withColumnRenamed("sum(total_amount)", "category_total_sales")

print("\n--- Wide Transformation: Category Sales Summary ---")
summary_df.show()

# 8. Explain Physical Plan (Predicate Pushdown & DAG execution)
print("\n--- Physical Execution Plan ---")
filtered_df.explain()

# 9. Save Processed Output Data
transformed_df.write.mode("overwrite").option("header", "true").csv("data/processed_csv")
transformed_df.write.mode("overwrite").parquet("data/processed_parquet")

print("\nProcessing completed successfully.")
spark.stop()
