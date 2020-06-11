QHow did changing values on the SparkSession property parameters affect the throughput and latency of the data?
A
I tried to experiment canging  Rate per partition and Offsets per trigger based on the lecture video.
I observed changing the value altered the report of processed rows per second metric.
different value tried from none upto 20 and its ranged between 0.7 to 4.
Attached the screenshots for different tries.

What were the 2-3 most efficient SparkSession property key/value pairs? Through testing multiple variations on values, how can you tell these were the most optimal?
The following is used in my submission which improved to 4 records processed per second from 0.7
        #.option("maxRatePerPartition",20)
        #.option("maxOffsetsPerTrigger",20)
        
        
