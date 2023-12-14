import processBase
processes = []
with open("datafile.dat",'r') as file:
    for line in file.readlines():
        job = line.split()
        time = job[0]
        priority = job[2]
        cpu_io_bursts = job[3:]
        processes.append(processBase.ProcessBase(starttime = time, burts = cpu_io_bursts, priority = priority))
print(processes)