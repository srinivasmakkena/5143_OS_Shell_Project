from django.shortcuts import render,HttpResponse
from . import consumers
from . import cpu
import json
from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse
# Create your views here.

def index(request):
    
    return render(request, "scheduler/index.html")

def get_data(request):
    # process_consumer = consumers.ProcessConsumer()
    # process_consumer.send(text_data = {"clock": 1})
    return render(request, "scheduler/scheduler.html")

def add_process(request):
    # print("received")
    process_id = request.GET.get("process_id")
    process_name = request.GET.get("process_name")
    process_bursts = [int(i)%20+1 for i in request.GET.getlist("process_bursts")]
    process_priority = request.GET.get("process_priority")
    process_message = request.GET.get("process_message")
    process_expression = request.GET.get("process_expression")
    process_answer = request.GET.get("process_answer")
    process_arrival_time = request.GET.get("process_arrival_time")
    process = cpu.Process(arrival_time = consumers.ProcessConsumer.clock + int(process_arrival_time), response = process_answer, message = process_message, cpu_bursts = process_bursts[0::2],io_bursts = process_bursts[1::2],priority=process_priority)
    cpu.add_process(process)
    # print(process.__dict__.items())
    # return json.dumps(process_data)
    return HttpResponse(content=request.__dict__)

@csrf_exempt
def add_process_bulk(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            
            for process_data in data:
                process_id = process_data.get("process_id")
                process_name = process_data.get("process_name")
                process_bursts = [int(i)%20+1 for i in process_data.get("process_bursts")]
                process_priority = process_data.get("process_priority")
                process_message = process_data.get("process_message")
                process_expression = process_data.get("process_expression")
                process_answer = process_data.get("process_answer")
                process_arrival_time = process_data.get("process_arrival_time")
                
                process = cpu.Process(
                    arrival_time=consumers.ProcessConsumer.clock + int(process_arrival_time),
                    response=process_answer,
                    message=process_message,
                    cpu_bursts=process_bursts[0::2],
                    io_bursts=process_bursts[1::2],
                    priority=process_priority
                )
                
                cpu.add_process(process)
            
            # You can customize the response as needed
            return JsonResponse({"status": "success"})
            
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    
    return JsonResponse({"status": "error", "message": "Invalid request method"})
