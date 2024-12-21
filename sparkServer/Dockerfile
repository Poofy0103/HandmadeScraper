FROM quay.io/centos/centos:stream9

# Install necessary dependencies
RUN dnf update -y --allowerasing && \
    dnf install -y --allowerasing \
      nano \
      sudo \
      curl \
      vim \
      unzip \
      rsync \
      java-devel \
      gcc \
      gcc-c++ \
      make \
      python3 \
      python3-pip \
      procps \
      openssh-clients && \
    dnf clean all

# Set environment variables
ENV SPARK_HOME=${SPARK_HOME:-"/opt/spark"}
ENV HADOOP_HOME=${HADOOP_HOME:-"/opt/hadoop"}

# Create necessary directories
RUN mkdir -p ${HADOOP_HOME} && mkdir -p ${SPARK_HOME}
WORKDIR ${SPARK_HOME}

# Download and install Spark
RUN curl https://dlcdn.apache.org/spark/spark-3.5.3/spark-3.5.3-bin-hadoop3.tgz -o spark-3.5.3-bin-hadoop3.tgz \
 && tar xvzf spark-3.5.3-bin-hadoop3.tgz --directory /opt/spark --strip-components 1 \
 && rm -rf spark-3.5.3-bin-hadoop3.tgz

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Set additional environment variables
ENV PATH="/opt/spark/sbin:/opt/spark/bin:${PATH}"
ENV SPARK_HOME="/opt/spark"
ENV SPARK_MASTER="spark://spark-master:7077"
ENV SPARK_MASTER_HOST=spark-master
ENV SPARK_MASTER_PORT=7077
ENV PYSPARK_PYTHON=python3
ENV PYTHONPATH=$SPARK_HOME/python/:$PYTHONPATH

# Copy Spark configuration and entrypoint script
COPY spark-defaults.conf "$SPARK_HOME/conf"
COPY entrypoint.sh .

# Make Spark scripts executable
RUN chmod u+x /opt/spark/sbin/* && \
    chmod u+x /opt/spark/bin/*
RUN ["chmod", "+x", "entrypoint.sh"]

ENTRYPOINT ["./entrypoint.sh"]

