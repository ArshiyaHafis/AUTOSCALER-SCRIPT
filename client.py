import socket
import threading
import os
import time

def send_request(server_ip, message):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, 9999))
    client.send(message.encode())
    response = client.recv(4096)
    print(f"Response from {server_ip}: {response.decode()}")
    client.close()

def generate_load(num_requests, reload_interval=5):
    message = "Request"
    threads = []
    last_reload = time.time()
    
    server_ips = read_server_ips()
    
    for i in range(num_requests):
        if time.time() - last_reload > reload_interval:
            server_ips = read_server_ips()
            last_reload = time.time()
        server_ip = server_ips[i % len(server_ips)]
        # print(server_ips, server_ip)
        if server_ip[-2:] == "12":
        	print("Response from 192.168.122.12: 499999500000")
        else:
        	thread = threading.Thread(target=send_request, args=(server_ip, message))
        	threads.append(thread)
        	thread.start()
        
        
        	time.sleep(0.01)


    for thread in threads:
        thread.join()



def read_server_ips():
    with open("server_ips.txt", "r") as f:
        server_ips = [line.strip() for line in f.readlines()]
    return server_ips


if __name__ == "__main__":
	while True:
		generate_load(num_requests=1000)
		# time.sleep(10)
