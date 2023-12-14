import json
import base64
from channels.generic.websocket import WebsocketConsumer
import time
from threading import Thread, Event
from . import cpu
import io
import matplotlib.pyplot as plt

class ProcessConsumer(WebsocketConsumer):
    clock = 0
    event = Event()
    def connect(self):
        self.accept()
        self.speed=10
        self.clock= ProcessConsumer.clock
        self.thread = Thread(target=self.infinite_loop)
        self.thread.start()
       
    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        self.speed = float(text_data_json.get("speed",self.speed))
        roundRobinTime = text_data_json.get("roundRobinTime",None)
        if roundRobinTime:
            cpu.change_roundrobbin_time_slice(float(roundRobinTime))
        cpuType = text_data_json.get("cpuType",None)
        if cpuType:
            cpu.change_cpu_type(cpuType)
        numCPUs = text_data_json.get("numCPUs",None)
        if numCPUs:
            cpu.change_cpus(int(numCPUs))
        numIODevices = text_data_json.get("numIODevices",None)
        if numIODevices:
            cpu.change_io_devices(int(numIODevices))
        if text_data_json.get("getImageRequest",False):
            print(text_data_json.get("getImageRequest",False))
            self.send_plot_data()

        
    def infinite_loop(self):
        while True:
            ProcessConsumer.clock += 1
            data = cpu.get_data(ProcessConsumer.clock)
            self.send(text_data=json.dumps(data))
            time.sleep(2/self.speed)
            # print(ProcessConsumer.clock,self.speed)
        
    def send_plot_data(self):
        # Generate a simple plot
        image_data = cpu.get_plot()
        # plt.plot([1, 2, 3, 4], [1, 4, 9, 16])
        # plt.title('Sample Plot')
        # plt.xlabel('X-axis')
        # plt.ylabel('Y-axis')

        # # Save the plot to a BytesIO object
        # image_stream = io.BytesIO()
        # plt.savefig(image_stream, format='png')
        # plt.close()

        # # Convert BytesIO object to base64-encoded string
        # image_stream.seek(0)
        # image_data = base64.b64encode(image_stream.read()).decode('utf-8')

        # Send the image data through WebSocket
        self.send(text_data=json.dumps({"imageData": image_data}))
