import os 
import webbrowser
import threading
import subprocess

def htop(output_dict):
    thread = threading.Thread(target=open_server,args=())
    thread.start()
    return output_dict

def open_server():
    subprocess.Popen(['open',"http://localhost:8000/scheduler"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Open the web browser to localhost:8000
    
    