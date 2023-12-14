import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from . import cpu

class ProcessConsumer(AsyncWebsocketConsumer):
    clock = 0

    async def connect(self):
        await self.accept()
        self.speed = 10
        self.clock = ProcessConsumer.clock
        self.loop_task = asyncio.ensure_future(self.infinite_loop())

    async def disconnect(self, close_code):
        self.loop_task.cancel()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        self.speed = float(text_data_json.get("speed", self.speed))
        round_robin_time = text_data_json.get("roundRobinTime", None)
        if round_robin_time:
            cpu.change_roundrobbin_time_slice(float(round_robin_time))
        cpu_type = text_data_json.get("cpuType", None)
        if cpu_type:
            cpu.change_cpu_type(cpu_type)
        num_cpus = text_data_json.get("numCPUs", None)
        if num_cpus:
            cpu.change_cpus(int(num_cpus))
        num_io_devices = text_data_json.get("numIODevices", None)
        if num_io_devices:
            cpu.change_io_devices(int(num_io_devices))
        if text_data_json.get("getImageRequest", False):
            await self.send_plot_data()

    async def infinite_loop(self):
        try:
            while True:
                ProcessConsumer.clock += 1
                data = cpu.get_data(ProcessConsumer.clock)
                await self.send(text_data=json.dumps(data))
                await asyncio.sleep(2 / self.speed)
        except asyncio.CancelledError:
            pass

    async def send_plot_data(self):
        image_data = cpu.get_plot()
        await self.send(text_data=json.dumps({"imageData": image_data}))
