from pyspark.sql import SparkSession
from pyspark.ml.regression import LinearRegression
from pyspark.ml.feature import VectorAssembler

spark = SparkSession.builder.appName("ML Training").getOrCreate()

df = spark.read.parquet("hdfs://localhost:9000/data/processed/")

assembler = VectorAssembler(
    inputCols=["passenger_count", "avg_distance"],
    outputCol="features"
)

data = assembler.transform(df).select("features", "avg_fare")

train_data, test_data = data.randomSplit([0.8, 0.2])

lr = LinearRegression(labelCol="avg_fare")
model = lr.fit(train_data)

print("Model trained successfully")
