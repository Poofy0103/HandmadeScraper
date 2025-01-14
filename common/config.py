import configparser

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
    config['Cloud_Services'] = {'account_file': 'xxxxxxxxxxxxxxxxxxx',
                                'project_id': 'xxxxxxxxxxxxxxxxxxx',
                                'bucket_name': "handmade-scraper",
                                'raw_folder': 'amz_raw_html',
                                'processed_folder': 'amz_processed_html'}
    config['IAM_Rules'] = {'storage': 'storage.objectUser'}

    # Write the configuration to a file
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def read_config():
    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Read the configuration file
    config.read('config.ini')

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
    iam_storage = config.get('IAM_Rules', 'storage')
    project_id = config.get('Cloud_Services', 'project_id')
    bucket_name = config.get('Cloud_Services', 'bucket_name')
    raw_folder = config.get('Cloud_Services', 'raw_folder')
    processed_folder = config.get('Cloud_Services', 'processed_folder')
    account_file = config.get('Cloud_Services', 'account_file')

    # Return a dictionary with the retrieved values
    config_values = {
        'debug_mode': debug_mode,
        'log_level': log_level,
        'external_ip': external_ip,
        'ssh_key': ssh_key,
        'ssh_port': ssh_port,
        'username': username,
        'bootstrap_server': bootstrap_server,
        'kafka_port': kafka_port,
        'topic': topic,
        'project_id': project_id,
        'bucket_name': bucket_name,
        'raw_folder': raw_folder,
        'processed_folder': processed_folder,
        'account_file': account_file,
        'iam': {"storage": iam_storage}
    }

    return config_values