class ProcessBase:
    def ___init__(self,  arrivalTime = 0 ,startTime = 0 , bursts = [], priority = 'P0'):
        self.id = current_id
        current_id += 1
        self.arrivalTime = arrivalTime
        self.startTime = startTime
        self.bursts = bursts
        self.priority = priority
        self.endTime = None
        self.cpuTime = None
    current_id = 0