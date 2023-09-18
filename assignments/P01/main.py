import os
import curses,readline

class command:
    pass

current_location = os.path.abspath(__file__)
current_path = os.path.dirname(current_location)
history=[]

while 1:
    raw_command = input("Shell: ~"+current_path+"$ ")
    history.append(raw_command)
    if raw_command[:2]=="ls":
        print(*os.listdir(current_path))
    elif raw_command == "history":
        for i, cmd in enumerate(history):
            print(f"{i + 1}: {cmd}")
    elif raw_command[:2]=="cd":
        new_path = raw_command[2:].strip()
        # print(new_path)
        if new_path == "..":
            # Move up to the parent directory
            current_path = os.path.dirname(current_path)
        elif os.path.isdir(os.path.join(current_path, new_path)):
            # Check if it's a valid subdirectory
            current_path = os.path.join(current_path, new_path)
        elif os.path.isabs(new_path) and os.path.isdir(new_path):
            # Check if it's a complete directory path
            current_path = new_path
        else:
            print(f"'{new_path}' is not found!")
    elif raw_command=="exit" or raw_command=="x":
        exit()
    else:
        print("Command "+raw_command+"not recognized.")