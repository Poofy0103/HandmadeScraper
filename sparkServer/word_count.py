from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, split

# Kafka and Spark configurations
KAFKA_BROKER = "172.18.0.8:9092"  # Replace with your Kafka broker address
KAFKA_TOPIC = "wordcount"       # Replace with your Kafka topic name
SPARK_SERVER = "172.18.0.10"

if __name__ == "__main__":
    # Create a SparkSession
    spark = SparkSession.builder \
        .appName("KafkaWordCount").master(f"spark://{SPARK_SERVER}:7077").getOrCreate()
        #.master(f"spark://{SPARK_SERVER}:7077").getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")

    # Read data from Kafka
    kafka_stream = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKER) \
        .option("subscribe", KAFKA_TOPIC) \
	.option("startingOffsets", "earliest") \
        .load()
    kafka_stream.printSchema()

    # Extract the message (value) from Kafka as a string
    messages = kafka_stream.selectExpr("CAST(value AS STRING) as message")
    messages.printSchema()

    # Split messages into words and count them
    words = messages.select(explode(split(messages.message, " ")).alias("word"))
    word_counts = words.groupBy("word").count()

    print(word_counts)
    # Write the word counts to the console (for debugging purposes)
    query = word_counts.writeStream \
        .outputMode("update") \
        .format("console") \
        .start()

    # Wait for the streaming query to finish
    query.awaitTermination()

