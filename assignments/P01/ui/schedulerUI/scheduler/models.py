from django.db import models

class Process_model(models.Model):
    start_time = models.IntegerField(default=0)
    cpu_bursts = models.JSONField(default=list)
    io_bursts = models.JSONField(default=list)
    current_burst = models.IntegerField(null=True, blank=True)
    current_burst_type = models.CharField(max_length=255, null=True, blank=True)
    priority = models.CharField(max_length=255, null=True, blank=True)
    message = models.CharField(max_length=200000, blank=True)
    time_spent_in_wait_queue = models.IntegerField(default=0)
    time_spent_in_ready_queue = models.IntegerField(default=0)
    time_spent_in_running_queue = models.IntegerField(default=0)
    time_spent_in_IO_queue = models.IntegerField(default=0)
    last_cycle_time = models.IntegerField(default=0)
    response = models.CharField(max_length=255, blank=True)
    process_in_ready_in_last_cycle = models.IntegerField(default=0)
    total_time = models.IntegerField(default=0)

    @classmethod
    def create_from_process(cls, process):
        return cls(
            start_time=process.arrival_time,
            cpu_bursts=process.cpu_bursts,
            io_bursts=process.io_bursts,
            current_burst=process.current_burst,
            current_burst_type=process.current_burst_type,
            priority=process.priority,
            message=process.message,
            time_spent_in_wait_queue=process.time_spent_in_wait_queue,
            time_spent_in_ready_queue=process.time_spent_in_ready_queue,
            time_spent_in_running_queue=process.time_spent_in_running_queue,
            time_spent_in_IO_queue=process.time_spent_in_IO_queue,
            last_cycle_time=process.last_cycle_time,
            response= process.response if process.response else "",
            process_in_ready_in_last_cycle = process.process_in_ready_in_last_cycle ,
            total_time = process.total_time
            
        )
