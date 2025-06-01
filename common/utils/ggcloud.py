import json

from google.cloud import storage
import os
from google.cloud import iam_admin_v1
from google.iam.v1 import iam_policy_pb2, policy_pb2
from google.oauth2 import service_account
import sys
from common.config import read_config

class StorageClient(storage.Client):
    def __init__(self,project = None, credentials_info: dict = None):
        self.project = project if project is not None else credentials_info.get("project_id")
        self.cred = service_account.Credentials.from_service_account_info(credentials_info)
        super().__init__(self.project, self.cred)

    def upload_from_string(self, destination_path: str, data: bytes | str, content_type: str = "plain/text", timeout: int = 60):
        """
            params:
            @destination_path: absolute path from bucket. E.g: rawcrawlerdatalake/test.txt
            @data: uploaded content
        """
        delim = "\\" if 'win' in sys.platform else '/'
        destination_bucket = destination_path.split(delim)[0]
        destination_file_path = destination_path.split(delim)[1:]
        bucket_client: storage.bucket.Bucket = self.bucket(destination_bucket)
        destination_file_path = delim.join(map(str, destination_file_path))
        blob_client = bucket_client.blob(destination_file_path)
        print(f"Start to upload html file {destination_path}")
        blob_client.upload_from_string(data=data, content_type=content_type, timeout=timeout)
        print(f"Upload {destination_path} completed")

class CloudManager:
    config_values = read_config()
    with open(os.path.join(config_values['root_dir'], 'credentials.json'), 'r+') as f:
        credentials_info = json.load(f)

    def __init__(self):
        self.storage_client = self.create_storage_cloud_session()

    def create_storage_cloud_session(self) -> StorageClient:
        # This snippet demonstrates how to list buckets.
        # *NOTE*: Replace the client created below with the client required for your application.
        # Note that the credentials are not specified when constructing the client.
        # Hence, the client library will look for credentials using ADC.
        try:
            storage_client = StorageClient(
                credentials_info=self.credentials_info
            )
            buckets = storage_client.list_buckets()
            print("Accessible Buckets:")
            for bucket in buckets:
                print(bucket.name)
        except Exception as e:
            raise Exception(f"Storage Cloud Client cannot be created due to: {e}")
        else:
            return storage_client

if __name__ == "__main__":
    cloud_client = CloudManager()
    cloud_client.storage_client.upload_from_string("rawcrawlerdatalake/test/test","test", "text/plain")