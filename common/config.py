import configparser
from dataclasses import dataclass
import os

ROOT_DIR = os.path.abspath(os.curdir)
CONFIG_PATH = os.path.join(ROOT_DIR, 'config.ini')

@dataclass
class Config:
    debug_mode: bool
    log_level: str
    external_ip: str
    ssh_key: str
    ssh_port: int
    username: str
    bootstrap_server: str
    kafka_port: int
    topic: str
    raw_bucket: str
    root_dir: str = ROOT_DIR

def create_config():
    config = configparser.ConfigParser()

    # Add sections and key-value pairs
    config['General'] = {'debug': True, 'log_level': 'info'}
    config['VM_Host'] = {'external_ip': 'xxx.xxx.xxx.xxx',
                          'ssh_key': 'gcloudssh', 
                          'ssh_port': 22,
                          'username': 'xxxx'}
    config['Kafka_Server'] = {'bootstrap_server': 'xxx.xxx.xxx.xxx',
                                'port': 9092,
                                'topic': 'scraper'}

    # Write the configuration to a file
    with open(CONFIG_PATH, 'w') as configfile:
        config.write(configfile)

def read_config(config_path: str = CONFIG_PATH) -> Config:
    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Read the configuration file
    config.read(config_path)

    # Access values from the configuration file
    debug_mode = config.getboolean('General', 'debug')
    log_level = config.get('General', 'log_level')

    external_ip = config.get('VM_Host', 'external_ip')
    ssh_key = config.get('VM_Host', 'ssh_key')
    ssh_port = config.getint('VM_Host', 'ssh_port')
    username = config.get('VM_Host', 'username')
    bootstrap_server = config.get('Kafka_Server', 'bootstrap_server')
    kafka_port = config.getint('Kafka_Server', 'port')
    topic = config.get('Kafka_Server', 'topic')
    raw_bucket = config.get('GGCloud', 'raw_bucket')
    # Return a dictionary with the retrieved values
    config_values = Config(
                            debug_mode=debug_mode,
                            log_level=log_level,
                            external_ip=external_ip,
                            ssh_key=ssh_key,
                            ssh_port=ssh_port,
                            username=username,
                            bootstrap_server=bootstrap_server,
                            kafka_port=kafka_port,
                            topic=topic,
                            raw_bucket=raw_bucket
                          )

    return config_values