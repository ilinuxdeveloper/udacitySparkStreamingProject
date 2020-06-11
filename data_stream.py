import logging
import json
from pyspark.sql import SparkSession
from pyspark.sql.types import *
import pyspark.sql.functions as psf

#/usr/bin/zookeeper-server-start ./config/zookeeper.properties 
#/usr/bin/kafka-server-start ./config/server.properties

#From knowledge to start the UI port
#spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.3.4 --master local[*] --conf spark.ui.port=3000 data_stream.py

#kafka-console-consumer --topic "sfcrime" --bootstrap-server localhost:9092 --from-beginning


# TODO Create a schema for incoming resources
schema = StructType([
    StructField("crime_id", StringType(), True),
    StructField("original_crime_type_name", StringType(), True),
    StructField("report_date", StringType(), True),
    StructField("call_date", StringType(), True),    
    StructField("offense_date", StringType(), True),
    StructField("call_time", StringType(), True),
    StructField("call_date_time", StringType(), True),
    StructField("disposition", StringType(), True),
    StructField("address", StringType(), True),
    StructField("city", StringType(), True),
    StructField("state", StringType(), True),
    StructField("agency_id", StringType(), True),
    StructField("address_type", StringType(), True),
    StructField("common_location", StringType(), True) 
])

def run_spark_job(spark):

    # TODO Create Spark Configuration
    # Create Spark configurations with max offset of 200 per trigger
    # set up correct bootstrap server and port
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers","localhost:9092") \
        .option("subscribe","sfcrime") \
        .option("maxRatePerPartition",20) \
        .option("maxOffsetsPerTrigger",20) \    
        .option("startingOffsets", "earliest") \
        .option("stopGracefullyOnShutdown", "true") \
        .load()
  
    # Show schema for the incoming resources for checks
    df.printSchema()

    # TODO extract the correct column from the kafka input resources
    # Take only value and convert it to String
    kafka_df = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
    
    service_table = kafka_df\
        .select(psf.from_json(psf.col('value'), schema).alias("DF"))\
        .select("DF.*")
    
    service_table.printSchema()
    
    # TODO select original_crime_type_name and disposition
    distinct_table = service_table.select(["original_crime_type_name","disposition"])
    distinct_table.printSchema()    
    
    # count the number of original crime type
    agg_df = distinct_table.groupBy(["original_crime_type_name","disposition"]).count()
    #agg_df = distinct_table.count()

    # TODO Q1. Submit a screen shot of a batch ingestion of the aggregation
    # TODO write output stream
    query = agg_df \
            .writeStream \
            .outputMode('Complete') \
            .format('console') \
            .option("truncate", "false") \
            .start()

    # TODO attach a ProgressReporter
    query.awaitTermination()

    # TODO get the right radio code json path
    radio_code_json_filepath = "/home/workspace/radio_code.json"
    radio_code_df = spark.read.json(radio_code_json_filepath,multiLine=True)

    # clean up your data so that the column names match on radio_code_df and agg_df
    # we will want to join on the disposition code

    # TODO rename disposition_code column to disposition
    radio_code_df = radio_code_df.withColumnRenamed("disposition_code", "disposition")
    radio_code_df.show()
    
    join_query = agg_df.join(radio_code_df,"disposition") \
                        .format("console") \
                        .outputMode("complete") \
                        .start()
    join_query.awaitTermination()


if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    # TODO Create Spark in Standalone mode
    spark = SparkSession \
        .builder \
        .master("local[*]") \
        .appName("KafkaSparkStructuredStreaming") \
        .getOrCreate()

    logger.info("Spark started")

    run_spark_job(spark)

    spark.stop()
