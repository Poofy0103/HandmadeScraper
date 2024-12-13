from typing import Literal, NotRequired, TypedDict, List, Coroutine, Any
from asyncio import coroutines
import datetime


class ListTasks(TypedDict):
    """Define this dictionary with the following key-value pairs:
    - id: str
    - log_timestamp: datetime
    - values: any --arguments for the task function
    - task: Coroutine -- An instantiated coroutine for the above values
    - status: int -- 100: pending, 202: processing, 200: done, 404: error"""
    id: str
    log_timestamp: datetime.datetime
    values: Any
    task: Coroutine 
    status: int
    

