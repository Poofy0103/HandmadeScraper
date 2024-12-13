import asyncio
from datamodel.model import ListTasks
from typing import List
import uuid
import datetime

class AsyncioManager:
    def __init__(self, maxSize = 3):
        self.queue = asyncio.Queue(maxSize)
        self.completedTasks = 0
        self.runningTasks = 0
        self.pendingTasks = 0
        
    
    async def add_task(self, coro):
        self.pendingTasks += 1
        await self.queue.put(coro)
        self.pendingTasks -= 1
        self.runningTasks += 1
        print(f"[{str(datetime.datetime.now())}] Added a new task")
        
    async def execute_task(self):
        while True:
            coro = await self.queue.get()
            try:
                await coro
                self.runningTasks -= 1
                self.completedTasks += 1
            except Exception as e:
                print("Failed to execute this task")
            self.queue.task_done()
    
    async def monitor_task(self, interval: int = 3):
        while True:
            print(f"[{str(datetime.datetime.now())}] {self.runningTasks} task(s) running. Completed: {self.completedTasks}")
            await asyncio.sleep(interval)
    