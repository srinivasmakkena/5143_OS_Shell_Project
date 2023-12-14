from . import models
import io
import matplotlib.pyplot as plt
import base64

from django.db.models import Avg


class Process:
    id = 0
    def __init__(self, arrival_time = 0, response= "",message = "",cpu_bursts = [], io_bursts = [], priority = None):
        self.id = Process.id+1
        Process.id += 1 
        self.arrival_time = arrival_time
        self.cpu_bursts = cpu_bursts
        self.io_bursts = io_bursts
        self.current_burst = None
        self.current_burst_type = None
        self.priority = priority
        self.message = message
        self.time_spent_in_wait_queue = 0 
        self.time_spent_in_ready_queue = 0
        self.time_spent_in_running_queue = 0
        self.time_spent_in_IO_queue = 0
        self.last_cycle_time = 0
        self.response = response
        self.process_in_ready_in_last_cycle = 0
        self.total_time = 0
        
class CPU:
    def __init__(self):
        self.clock = 0
        self.new_queue = []
        self.ready_queue = []
        self.running_queue = []
        self.waiting_queue = []
        self.io_queue = []
        self.exit_queue = []
        self.num_cpus = 1
        self.num_io = 1
        self.cpu_type = "FCFS"
        self.RR_timeSlice = 1
        self.cpu_utilization = []
        self.IO_utilization = []

current_cpu = CPU()

def add_process(process):
    global current_cpu
    current_cpu.new_queue.append(process)

def change_cpu_type(cpuType):
    global current_cpu
    current_cpu.cpu_type = cpuType

def change_roundrobbin_time_slice(time):
    global current_cpu
    current_cpu.RR_timeSlice = time

def change_io_devices(IO_devices):
    global current_cpu
    current_cpu.num_io = IO_devices

def change_cpus(cpus):
    global current_cpu
    current_cpu.num_cpus = cpus

def get_cpu():
    global current_cpu
    return current_cpu

def get_data(clock):
    global current_cpu
    current_cpu,messages = process_cpu(current_cpu,clock)
    data = {"clock": clock}
    data["new_queue_count"] = len(current_cpu.new_queue)
    data["ready_queue_count"] = len(current_cpu.ready_queue)
    data["running_queue_count"] = len(current_cpu.running_queue)
    data["waiting_queue_count"] = len(current_cpu.waiting_queue)
    data["io_queue_count"] = len(current_cpu.io_queue)
    data["exit_queue_count"] = len(current_cpu.exit_queue)
    data["new_queue_elements"] = [str(i.id)+ " [" + str(i.arrival_time) + "] " +str(i.message)  for i in current_cpu.new_queue]
    data["ready_queue_elements"] = [str(i.id)+ " " + str(i.cpu_bursts[0]) for i in current_cpu.ready_queue]
    data["waiting_queue_elements"] = [str(i.id)+ " " +str(i.io_bursts[0]) for i in current_cpu.waiting_queue]
    data["running_queue_elements"] = [str(i.id)+ " " + str(i.current_burst)+"/"+str(i.cpu_bursts[0]) for i in current_cpu.running_queue]
    data["io_queue_elements"] = [str(i.id)+ " " + str(i.current_burst) + "/" + str(i.io_bursts[0]) for i in current_cpu.io_queue]
    data["exit_queue_elements"] = [str(i.id)+ " completed"for i in current_cpu.exit_queue]
    if current_cpu.cpu_type == "Priority":
        data["new_queue_elements"] = [str(i.id)+ " [" + str(i.arrival_time) + "] " +str(i.message)  for i in sorted(current_cpu.new_queue,key = lambda process :process.priority)]
        data["ready_queue_elements"] = [str(i.id)+ " " + str(i.cpu_bursts[0]) + " - " + i.priority for i in sorted(current_cpu.ready_queue,key = lambda process :process.priority)]
        data["waiting_queue_elements"] = [str(i.id)+ " " +str(i.io_bursts[0]) + " - " + i.priority for i in sorted(current_cpu.waiting_queue,key = lambda process :process.priority)]
        data["running_queue_elements"] = [str(i.id)+ " " + str(i.current_burst)+"/"+str(i.cpu_bursts[0]) + " - " + i.priority for i in sorted(current_cpu.running_queue,key = lambda process :process.priority)]
        data["io_queue_elements"] = [str(i.id)+ " " + str(i.current_burst) + "/" + str(i.io_bursts[0]) + " - " + i.priority for i in sorted(current_cpu.io_queue,key = lambda process :process.priority)]
        data["exit_queue_elements"] = [str(i.id)+ " completed"for i in current_cpu.exit_queue]
    
    data["messages"] = messages
    return data

def process_cpu(cpu,clock):
    if cpu.cpu_type == "FCFS":
        cpu,messages = process_FCFS(cpu,clock)
    elif cpu.cpu_type == "RoundRobin":
        cpu,messages = process_RoundRobbin(cpu,clock)
    elif cpu.cpu_type == "Priority":
        cpu,messages = process_priority_based(cpu,clock)
    else:
        print("Unknown cpu type : ",cpu.cpu_type)
    if cpu.new_queue or cpu.ready_queue or cpu.running_queue or cpu.waiting_queue or cpu.io_queue:        
        cpu.cpu_utilization.append((len(cpu.running_queue)/cpu.num_cpus)*100)
        cpu.IO_utilization.append((len(cpu.io_queue)/cpu.num_io)*100)
    return cpu,messages

def process_FCFS(cpu,clock):
    messages = []
    # messages.append("clock: "+ str(clock))
    current_updated = []
    for process in cpu.new_queue:
        if process not in current_updated:
            if process.arrival_time == clock or process.arrival_time < clock:
                cpu.ready_queue.append(process)
                cpu.new_queue.remove(process)
                messages.append(f"Process {process.id} moved to ready queue.")
                current_updated.append(process)        
    for process in cpu.ready_queue:
        if process not in current_updated:
            if cpu.num_cpus > len(cpu.running_queue):
                cpu.running_queue.append(process)
                cpu.ready_queue.remove(process)
                process.current_burst_type = "cpu"
                process.current_burst = process.cpu_bursts[0]
                current_updated.append(process)
                messages.append(f"Process {process.id} moved to running queue with cpu burst {process.current_burst}.")
            process.time_spent_in_ready_queue +=1

    for process in cpu.running_queue:
        if process not in current_updated:
            process.current_burst -= 1
            if process.current_burst == 0:
                if len(process.cpu_bursts) != 1:
                    cpu.waiting_queue.append(process)
                    process.current_burst_type = "io"
                    process.current_burst = process.io_bursts[0]
                    process.cpu_bursts = process.cpu_bursts[min(1,len(process.cpu_bursts)):]
                    messages.append(f"Process {process.id} moved to waiting queue with IO burst {process.current_burst}.")
                else:
                    cpu.exit_queue.append(process)
                    process.cpu_bursts = []
                    messages.append(f"Process {process.id} moved to exit queue.")
                cpu.running_queue.remove(process)
                current_updated.append(process)
            process.time_spent_in_running_queue +=1
        
    for process in cpu.waiting_queue:
        if process not in current_updated:
            if cpu.num_io > len(cpu.io_queue):
                cpu.io_queue.append(process)
                cpu.waiting_queue.remove(process)
                current_updated.append(process)            
                messages.append(f"Process {process.id} moved to io queue with io burst {process.current_burst}.")
            process.time_spent_in_wait_queue += 1

    for process in cpu.io_queue:
        if process not in current_updated:
            process.current_burst -= 1
            if process.current_burst == 0:
                cpu.ready_queue.append(process)
                process.current_burst_type = "cpu"
                process.current_burst = process.cpu_bursts[0]
                process.io_bursts = process.io_bursts[min(1,len(process.io_bursts)):]
                cpu.io_queue.remove(process)
                current_updated.append(process)
                messages.append(f"Process {process.id} moved to ready queue with cpu burst {process.current_burst}.")
            process.time_spent_in_IO_queue +=1
            
    for process in cpu.exit_queue:
        if process not in current_updated:
            cpu.exit_queue.remove(process)
            messages.append(f"-----------------------------------------------------")
            messages.append(f"Execution of Process {process.id} completed in {clock - int(process.arrival_time)} clock ticks.")
            messages.append(f"Process : {process.message} completed.")            
            messages.append(f"Response: {process.response}")
            messages.append(f"Process {process.id} waited {process.time_spent_in_ready_queue} clock ticks in ready queue,\n{process.time_spent_in_running_queue} clock ticks in running queue,\n{process.time_spent_in_IO_queue} clock ticks in IO queue, \n{process.time_spent_in_wait_queue} clock ticks in wait queue.")
            messages.append("-----------------------------------------------------")
            current_updated.append(process)
            process.total_time = clock - int(process.arrival_time)
            model_process = models.Process_model.create_from_process(process)
            model_process.save()
    return cpu,messages

def process_RoundRobbin(cpu,clock):
    messages = []
    # messages.append("clock: "+ str(clock))
    current_updated = []
    for process in cpu.new_queue:
        if process not in current_updated:
            if process.arrival_time == clock or process.arrival_time < clock:
                cpu.ready_queue.append(process)
                cpu.new_queue.remove(process)
                messages.append(f"Process {process.id} moved to ready queue.")
                current_updated.append(process)        
    for process in cpu.ready_queue:
        if process not in current_updated:
            if cpu.num_cpus > len(cpu.running_queue):
                cpu.running_queue.append(process)
                cpu.ready_queue.remove(process)
                process.current_burst_type = "cpu"
                process.current_burst = process.cpu_bursts[0]
                current_updated.append(process)
                messages.append(f"Process {process.id} moved to running queue with cpu burst {process.current_burst}.")
                
            process.time_spent_in_ready_queue +=1

    for process in cpu.running_queue:
        if process not in current_updated:
            process.current_burst -= 1
            if process.current_burst == 0:
                if len(process.cpu_bursts) != 1:
                    cpu.waiting_queue.append(process)
                    process.current_burst_type = "io"
                    process.current_burst = process.io_bursts[0]
                    process.cpu_bursts = process.cpu_bursts[min(1,len(process.cpu_bursts)):]
                    messages.append(f"Process {process.id} moved to waiting queue with IO burst {process.current_burst}.")
                else:
                    cpu.exit_queue.append(process)
                    process.cpu_bursts = []
                    messages.append(f"Process {process.id} moved to exit queue.")
                cpu.running_queue.remove(process)
                current_updated.append(process)
            elif (process.cpu_bursts[0] - process.current_burst) % cpu.RR_timeSlice == 0:
                process.cpu_bursts[0] = process.current_burst
                cpu.ready_queue.append(process)
                cpu.running_queue.remove(process)
                messages.append(f"Process {process.id} moved back to ready queue with remaining cpu burst {process.current_burst}.")
            process.time_spent_in_running_queue +=1
        
    for process in cpu.waiting_queue:
        if process not in current_updated:
            if cpu.num_io > len(cpu.io_queue):
                cpu.io_queue.append(process)
                cpu.waiting_queue.remove(process)
                current_updated.append(process)            
                messages.append(f"Process {process.id} moved to io queue with io burst {process.current_burst}.")
            process.time_spent_in_wait_queue += 1

    for process in cpu.io_queue:
        if process not in current_updated:
            process.current_burst -= 1
            if process.current_burst == 0:
                cpu.ready_queue.append(process)
                process.current_burst_type = "cpu"
                process.current_burst = process.cpu_bursts[0]
                process.io_bursts = process.io_bursts[min(1,len(process.io_bursts)):]
                cpu.io_queue.remove(process)
                current_updated.append(process)
                messages.append(f"Process {process.id} moved to ready queue with cpu burst {process.current_burst}.")
            process.time_spent_in_IO_queue +=1
            
    for process in cpu.exit_queue:
        if process not in current_updated:
            cpu.exit_queue.remove(process)
            messages.append(f"-----------------------------------------------------")
            messages.append(f"Execution of Process {process.id} completed in {clock - int(process.arrival_time)} clock ticks.")
            messages.append(f"Process : {process.message} completed.")            
            messages.append(f"Response: {process.response}")
            messages.append(f"Process {process.id} waited {process.time_spent_in_ready_queue} clock ticks in ready queue,\n{process.time_spent_in_running_queue} clock ticks in running queue,\n{process.time_spent_in_IO_queue} clock ticks in IO queue, \n{process.time_spent_in_wait_queue} clock ticks in wait queue.")
            messages.append("-----------------------------------------------------")
            current_updated.append(process)
            process.total_time = clock - int(process.arrival_time)
            model_process = models.Process_model.create_from_process(process)
            model_process.save()
    return cpu,messages

def process_priority_based(cpu,clock):
    messages = []
    # messages.append("clock: "+ str(clock))
    current_updated = []
    for process in cpu.new_queue:
        if process not in current_updated:
            if process.arrival_time == clock or process.arrival_time < clock:
                process.process_in_ready_in_last_cycle = 0
                cpu.ready_queue.append(process)
                cpu.new_queue.remove(process)
                messages.append(f"Process {process.id} moved to ready queue.")
                current_updated.append(process)   
    cpu.ready_queue = sorted(cpu.ready_queue,key = lambda process :process.priority)
    time_in_ready_queue_this_cycle = [i.process_in_ready_in_last_cycle for i in cpu.ready_queue]
    if time_in_ready_queue_this_cycle != []:
        avg_time_in_ready_queue_this_cycle = sum(time_in_ready_queue_this_cycle)/len(time_in_ready_queue_this_cycle)
    else:
        avg_time_in_ready_queue_this_cycle = 0
    for process in cpu.ready_queue:
        if process not in current_updated:
            if cpu.num_cpus > len(cpu.running_queue):
                cpu.running_queue.append(process)
                cpu.ready_queue.remove(process)
                process.current_burst_type = "cpu"
                process.current_burst = process.cpu_bursts[0]
                current_updated.append(process)
                messages.append(f"Process {process.id} moved to running queue with cpu burst {process.current_burst}.")
            process.process_in_ready_in_last_cycle += 1
            if process.process_in_ready_in_last_cycle > 1.5 * avg_time_in_ready_queue_this_cycle:
                process.priority = 'p'+ str(max(0, int(process.priority[1:])-1))
            process.time_spent_in_ready_queue +=1

    for process in cpu.running_queue:
        if process not in current_updated:
            process.current_burst -= 1
            cpu.ready_queue = sorted(cpu.ready_queue,key = lambda process :process.priority)
            if process.current_burst == 0:
                if len(process.cpu_bursts) != 1:
                    cpu.waiting_queue.append(process)
                    process.current_burst_type = "io"
                    process.current_burst = process.io_bursts[0]
                    process.cpu_bursts = process.cpu_bursts[min(1,len(process.cpu_bursts)):]
                    messages.append(f"Process {process.id} moved to waiting queue with IO burst {process.current_burst}.")
                else:
                    cpu.exit_queue.append(process)
                    process.cpu_bursts = []
                    messages.append(f"Process {process.id} moved to exit queue.")
                cpu.running_queue.remove(process)
                current_updated.append(process)
            elif len(cpu.ready_queue) != 0 and process.priority > cpu.ready_queue[0].priority:
                cpu.running_queue.remove(process)
                cpu.ready_queue.append(process)
                cpu.ready_queue = sorted(cpu.ready_queue,key = lambda process :process.priority)
                cpu.ready_queue[0].current_burst = cpu.ready_queue[0].cpu_bursts[0]
                cpu.running_queue.append(cpu.ready_queue[0])
                messages.append(f"Process {process.id} added to running queue due to high priority with remaining cpu burst {cpu.ready_queue[0].current_burst}.")
                cpu.ready_queue.remove(cpu.ready_queue[0])
                messages.append(f"Process {process.id} moved back to ready queue with remaining cpu burst {process.current_burst}.")
                
            process.time_spent_in_running_queue +=1
        
    for process in cpu.waiting_queue:
        if process not in current_updated:
            if cpu.num_io > len(cpu.io_queue):
                cpu.io_queue.append(process)
                cpu.waiting_queue.remove(process)
                current_updated.append(process)            
                messages.append(f"Process {process.id} moved to io queue with io burst {process.current_burst}.")
            process.time_spent_in_wait_queue += 1

    for process in cpu.io_queue:
        if process not in current_updated:
            process.current_burst -= 1
            if process.current_burst == 0:
                process.process_in_ready_in_last_cycle = 0
                cpu.ready_queue.append(process)
                process.current_burst_type = "cpu"
                process.current_burst = process.cpu_bursts[0]
                process.io_bursts = process.io_bursts[min(1,len(process.io_bursts)):]
                cpu.io_queue.remove(process)
                current_updated.append(process)
                messages.append(f"Process {process.id} moved to ready queue with cpu burst {process.current_burst}.")
            process.time_spent_in_IO_queue +=1
            
    for process in cpu.exit_queue:
        if process not in current_updated:
            cpu.exit_queue.remove(process)
            messages.append(f"-----------------------------------------------------")
            messages.append(f"Execution of Process {process.id} completed in {clock - int(process.arrival_time)} clock ticks.")
            messages.append(f"Process : {process.message} completed.")            
            messages.append(f"Response: {process.response}")
            messages.append(f"Process {process.id} waited {process.time_spent_in_ready_queue} clock ticks in ready queue,\n{process.time_spent_in_running_queue} clock ticks in running queue,\n{process.time_spent_in_IO_queue} clock ticks in IO queue, \n{process.time_spent_in_wait_queue} clock ticks in wait queue.")
            messages.append("-----------------------------------------------------")
            current_updated.append(process)
            process.total_time = clock - int(process.arrival_time)
            model_process = models.Process_model.create_from_process(process)
            model_process.save()
    return cpu,messages

def create_process_model_instance(original_process):
    return models.ProcessModel.objects.create(
        arrival_time=original_process.arrival_time,
        cpu_bursts=original_process.cpu_bursts,
        io_bursts=original_process.io_bursts,
        current_burst=original_process.current_burst,
        current_burst_type=original_process.current_burst_type,
        priority=original_process.priority,
        message=original_process.message,
        time_spent_in_wait_queue=original_process.time_spent_in_wait_queue,
        time_spent_in_ready_queue=original_process.time_spent_in_ready_queue,
        time_spent_in_running_queue=original_process.time_spent_in_running_queue,
        time_spent_in_IO_queue=original_process.time_spent_in_IO_queue,
        last_cycle_time=original_process.last_cycle_time,
        response=original_process.response,
    )
def get_plot():
    # models.Process_model.objects()
    global current_cpu
    image_data_list =[]
    try:
        cpu_utilization_avg = int(sum(current_cpu.cpu_utilization)/len(current_cpu.cpu_utilization))
    except:
        cpu_utilization_avg = 0
    try:
        io_utilization_avg = int(sum(current_cpu.IO_utilization)/len(current_cpu.IO_utilization))
    except:
        io_utilization_avg = 0
    average_tat = int(models.Process_model.objects.aggregate(Avg('total_time'))['total_time__avg'] or 0)
    average_wait_queue = int(models.Process_model.objects.aggregate(Avg('time_spent_in_wait_queue'))['time_spent_in_wait_queue__avg'] or 0)
    average_ready_queue = int(models.Process_model.objects.aggregate(Avg('time_spent_in_ready_queue'))['time_spent_in_ready_queue__avg'] or 0)
    average_running_queue = int(models.Process_model.objects.aggregate(Avg('time_spent_in_running_queue'))['time_spent_in_running_queue__avg'] or 0)
    average_io_queue = int(models.Process_model.objects.aggregate(Avg('time_spent_in_IO_queue'))['time_spent_in_IO_queue__avg'] or 0)
    msg = models.Process_model.objects.first()
    if msg:
        msg = msg.message
    else:
        msg = ""
    print("cpu: ",cpu_utilization_avg)
    print("IO: ",io_utilization_avg)    
    data = [["CPU", "IO","TAtime", "avg wait","avg ready", "avg running", "avg io"], 
            [cpu_utilization_avg,io_utilization_avg, average_tat, average_wait_queue, average_ready_queue, average_running_queue, average_io_queue]]
    bar_colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown']
    plt.bar(data[0],data[1],color = bar_colors)
    
    for a,b in zip(data[0],data[1]): 
        plt.text(a, b, str(b),ha='center', va='bottom')
    plt.title(current_cpu.cpu_type + " " +str(current_cpu.num_io) + " IO's, " + str(current_cpu.num_cpus) + " CPU's for " + msg)
    plt.xlabel('')
    plt.xticks(rotation=25, ha='right')
    plt.ylabel('Ticks and % of utilization')
    image_stream = io.BytesIO()
    plt.savefig(image_stream, format='png')
    plt.close()
    image_stream.seek(0)
    image_data = base64.b64encode(image_stream.read()).decode('utf-8')
    current_cpu.IO_utilization = []
    current_cpu.cpu_utilization = []
    image_data_list.append(image_data)
    models.Process_model.objects.all().delete()
    # Calculate average values
    
    # Print or use the average values as needed
    print("Average time spent in wait queue:", average_wait_queue)
    print("Average time spent in ready queue:", average_ready_queue)
    print("Average time spent in running queue:", average_running_queue)
    print("Average time spent in IO queue:", average_io_queue)
    return image_data

    

