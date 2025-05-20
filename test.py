from google.cloud import iam_admin_v1, resourcemanager_v3
from google.iam.v1 import iam_policy_pb2, policy_pb2
from common.config import read_config
import aiofiles
import aiohttp
import asyncio
from gcloud.aio.storage import Storage
from tqdm.asyncio import tqdm
from google.oauth2 import service_account

async def async_download_file(no):
    config = read_config()
    projectId = config['project_id']
    accountFile = config['account_file']
    bucketName = config['bucket_name']
    rawFolder = config['raw_folder']
    processedFolder = config['processed_folder']
    session = aiohttp.ClientSession()
    credentials = service_account.Credentials.from_service_account_file(accountFile)
    storageClient = Storage(session=session, service_file=credentials)
    bucket = await storageClient.get_bucket_metadata(bucket=bucketName)
    print(bucket)
    print(f"Start download file {no}")
    status = await storageClient.download(bucket=bucketName, object_name="amz_raw_html/0061d01e-d2ac-11ef-b314-44850033dafa.html")
    print(f"Finished download file {no}")
    await session.close()

async def gather_tasks():
    tasks = [async_download_file(no) for no in range(10)]
    await tqdm.gather(*tasks)

asyncio.run(gather_tasks())