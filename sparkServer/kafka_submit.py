from kafka import KafkaProducer
import json
import logging
from sshtunnel import SSHTunnelForwarder
from common.config import read_config

# JSON serializer for Kafka messages
def json_serializer(data):
    return json.dumps(data).encode('utf-8')

def kafka_submit(data):
    # GCP VM and Kafka settings
    config = read_config()
    GCP_VM_IP = config["external_ip"]  # Public IP of your GCP VM
    GCP_VM_USERNAME = config["username"]  # GCP VM username
    PRIVATE_KEY_PATH = config["ssh_key"]  # Path to your SSH private key
    KAFKA_LOCAL_PORT = config["kafka_port"]  # Local port for SSH tunnel to Kafka broker
    KAFKA_TOPIC = config["topic"]
    KAFKA_BOOTSTRAP_SERVER = config["bootstrap_server"]

    # Set up an SSH tunnel to the GCP VM
    try:
        # Start the SSH tunnel
        ssh_tunnel = SSHTunnelForwarder(
            (GCP_VM_IP, config["ssh_port"]),  # GCP VM IP and SSH port
            ssh_username=GCP_VM_USERNAME,
            ssh_pkey=PRIVATE_KEY_PATH,
            remote_bind_address=(KAFKA_BOOTSTRAP_SERVER, KAFKA_LOCAL_PORT),  # Kafka broker inside the VM
        )
        ssh_tunnel.start()

        print(f"SSH tunnel established! Local Kafka port: {KAFKA_LOCAL_PORT}")

        # Set up the Kafka producer
        producer = KafkaProducer(
            bootstrap_servers=f'{KAFKA_BOOTSTRAP_SERVER}:{KAFKA_LOCAL_PORT}',  # Use the tunneled localhost
            value_serializer=json_serializer,
        )
        if config["debug"] == True:
            logging.basicConfig(level=logging.DEBUG)

        # Sending a simple string message
        producer.send(KAFKA_TOPIC, data)

        # Ensure all messages are sent before exiting
        producer.flush()
        print(f"Message sent to Kafka topic '{KAFKA_TOPIC}'.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Clean up the SSH tunnel
        if 'ssh_tunnel' in locals() and ssh_tunnel.is_active:
            ssh_tunnel.stop()
            print("SSH tunnel closed.")
