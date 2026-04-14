from kafka import KafkaConsumer
import json
import pandas as pd
import os

consumer = KafkaConsumer(
    'taxi-data',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

data = []

for message in consumer:
    data.append(message.value)

    if len(data) >= 1000:
        df = pd.DataFrame(data)
        file_name = f"batch_{len(data)}.csv"
        df.to_csv(file_name, index=False)

        os.system(f"hdfs dfs -put {file_name} /data/raw/")
        data = []
