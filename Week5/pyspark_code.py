from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, avg, min, max, count, when
from pyspark.sql.types import IntegerType

spark = SparkSession.builder \
    .appName("SparkFundamentals") \
    .getOrCreate()

data = [
    (1, "Alice", 28, "Sales", "North", 50000.0, "2023-01-15"),
    (2, "Bob", None, "Marketing", "South", 60000.0, "2023-02-20"),
    (3, "Charlie", 35, "IT", "East", 75000.0, "2023-03-10"),
    (4, "Diana", 42, "Sales", "West", 80000.0, None),
    (5, "Eve", 28, "IT", "North", 70000.0, "2023-05-05"),
    (1, "Alice", 28, "Sales", "North", 50000.0, "2023-01-15"),
    (6, "Frank", 50, "HR", "South", None, "2023-06-12"),
    (7, "Grace", 22, "Marketing", "", 45000.0, "2023-07-01"),
    (8, "Hank", 38, None, "East", 65000.0, "2023-08-22")
]

columns = ["id", "name", "age", "department", "region", "salary", "join_date"]

df = spark.createDataFrame(data, columns)

print("--- Original DataFrame ---")
df.show()

print("--- 1. Schema Modification ---")
df_mod = df.withColumn("age", col("age").cast(IntegerType())) \
           .withColumnRenamed("join_date", "hiring_date")
df_mod.printSchema()

print("--- 2. Data Cleaning ---")
df_clean = df_mod.dropDuplicates()

df_clean = df_clean.withColumn("region", when(col("region") == "", "Unknown").otherwise(col("region")))

df_clean = df_clean.fillna({
    "age": 30,
    "department": "Unassigned",
    "salary": 0.0,
    "hiring_date": "1900-01-01"
})
df_clean.show()

print("--- 3. Filtering Conditions ---")
df_filtered = df_clean.filter(
    (col("age") >= 25) & 
    (col("age") <= 40) & 
    (col("department") != "Unassigned")
)
df_filtered.show()

print("--- 4. Aggregation and Grouping ---")
agg_df = df_clean.groupBy("department").agg(
    avg("salary").alias("avg_salary"),
    count("id").alias("employee_count"),
    max("salary").alias("max_salary"),
    min("salary").alias("min_salary")
)

agg_filtered_df = agg_df.filter(col("employee_count") > 1)
agg_filtered_df.show()

print("--- 5. Complete Pipeline Execution ---")
final_pipeline_df = df \
    .dropDuplicates() \
    .withColumnRenamed("join_date", "hiring_date") \
    .withColumn("region", when(col("region") == "", "Unknown").otherwise(col("region"))) \
    .fillna({"age": 30, "department": "Unassigned", "salary": 0.0, "hiring_date": "1900-01-01"}) \
    .filter(col("salary") > 0) \
    .groupBy("region") \
    .agg(sum("salary").alias("total_regional_salary")) \
    .orderBy(col("total_regional_salary").desc())

final_pipeline_df.show()

print("--- Writing output to CSV ---")
final_pipeline_df.write.mode("overwrite").csv("pyspark_output.csv", header=True)
print("Data successfully written to pyspark_output.csv")

spark.stop()
