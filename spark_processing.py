from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg

spark = SparkSession.builder.appName("Taxi Batch Processing").getOrCreate()

df = spark.read.csv("hdfs://localhost:9000/data/raw/", header=True, inferSchema=True)

df = df.dropna()

df = df.withColumn("trip_duration",
                   col("dropoff_datetime").cast("long") - col("pickup_datetime").cast("long"))

agg_df = df.groupBy("passenger_count").agg(
    avg("trip_distance").alias("avg_distance"),
    avg("fare_amount").alias("avg_fare")
)

agg_df.write.mode("overwrite").parquet("hdfs://localhost:9000/data/processed/")

print("Batch processing complete")
