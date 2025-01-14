import asyncio
from typing import List
import uuid
import time
import datetime
from google.cloud import storage
from google.oauth2 import service_account
import json
from google.cloud import iam_admin_v1, resourcemanager_v3
from google.iam.v1 import iam_policy_pb2, policy_pb2
from config import read_config

class AsyncioManager:
    def __init__(self, maxSize = 0, queuesNum = 2):
        self.maxSize = maxSize
        self.completedTasks = 0
        self.runningTasks = 0
        self.queuesNum = queuesNum
        self.queues: List[asyncio.Queue] = []
        
    async def add_task(self, coro):
        self.runningTasks += 1
        try:
            tasksInQueues = [tasks.qsize() for tasks in self.queues]
            print(tasksInQueues)
            idx_max = tasksInQueues.index(min(tasksInQueues))
            await self.queues[idx_max].put(coro)
            print(f"[{str(datetime.datetime.now())}] Added a new task")
        except:
            print("Please add queues to the list")
    
    def create_queue(self):
        for i in range(self.queuesNum):
            self.queues.append(asyncio.Queue(self.maxSize))
        
    async def execute_task(self, queue: asyncio.Queue, index):
        print(f"Execute the queue {index}")
        while True:
            coro = await queue.get()
            try:
                await coro
            except Exception as e:
                print("Failed to execute this task")
            self.runningTasks -= 1
            self.completedTasks += 1
            queue.task_done()
    
    async def start_all_queues(self):
        tasks = [self.execute_task(queue, index) for index, queue in enumerate(self.queues)]
        await asyncio.gather(*tasks)
    
    def monitor_task(self, interval: int = 3):
        while True:
            print(f"[{str(datetime.datetime.now())}] {self.runningTasks} task(s) running. Completed: {self.completedTasks}")
            time.sleep(interval)

class CloudManager:
    def __init__(self):
        # Instantiates a client
        self.config = read_config()
        self.projectId = self.config['project_id']
        self.accountFile = self.config['account_file']
        self.bucketName = self.config['bucket_name']
        self.rawFolder = self.config['raw_folder']
        self.processedFolder = self.config['processed_folder']
        self.credentials = service_account.Credentials.from_service_account_file(self.accountFile)
        self.storageClient = storage.Client(credentials=self.credentials, project=self.projectId)
        self.bucket = self.storageClient.bucket(self.bucketName)
        self.listOfServices = {
                                    'storage': self.bucket
                                }

    def get_service_account_iam_policy(self, resource):
        policy = resource.get_iam_policy(requested_policy_version=3)
        return policy.bindings
    
    def verify_iam_policy(self, resource, recommended_role):
        """
        Verify if the current account is granted with the recommended role on the resource
        """
        policy_bindings = self.get_service_account_iam_policy(resource)
        for binding in policy_bindings:
            if recommended_role in binding['role'] and self.accountFile.rstrip(".json") in str(binding['members']):
                return True
        return False
            
    def verify_all_iam_policies(self):
        for resource, recommended_role in self.config['iam'].items():
            if self.verify_iam_policy(resource=self.listOfServices[resource], recommended_role=recommended_role):
                print(f"GREAT!!! You have adequate permissions on {resource}")
            else:
                print(f"WARNING!! You might have not granted the recommended role of the current account on {resource}")
    
    def list_blob(self):
        blobs = self.bucket.list_blobs()
        for blob in blobs:
            print(blob)
        return blobs

    def upload_blob_from_memory(self, content):
        """Uploads a file to the bucket."""
        destinationBlobName = f"{self.rawFolder}/{str(uuid.uuid4)}.html"
        blob = self.bucket.blob(destinationBlobName)
        blob.upload_from_string(content)

        print(
            f"{destinationBlobName} uploaded to {self.rawFolder}."
        )
