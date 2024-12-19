import asyncio
from typing import List
import uuid
import time
import datetime

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
    