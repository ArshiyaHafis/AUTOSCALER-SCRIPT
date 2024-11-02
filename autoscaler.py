import libvirt
import time
import paramiko
import os


# Configuration
OVERLOAD_THRESHOLD = 50  
UNDERLOAD_THRESHOLD = 10  
NEW_VM_NAME = "new-server"
NEW_VM_IP = "192.168.122.12"  
SSH_USERNAME = "tuni"  
SSH_KEY_PATH = os.path.expanduser("~/.ssh/id_rsa")

conn = libvirt.open('qemu:///system')

def get_cpu_utilization(domain):
    try:
        prev_stats = domain.getCPUStats(True)
        prev_time = time.time()
        time.sleep(1)
        current_stats = domain.getCPUStats(True)
        current_time = time.time()

        cpu_time_diff = current_stats[0]['cpu_time'] - prev_stats[0]['cpu_time']
        elapsed_time = current_time - prev_time
        num_cpu = domain.maxVcpus()

        utilization = (cpu_time_diff / (elapsed_time * num_cpu * 1e9)) * 100
        return utilization
    except libvirt.libvirtError as e:
        print(f"Error getting CPU utilization for domain {domain.name()}: {e}")
        return None

def start_server_script(ip, username, key_path):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, key_filename=key_path)

        # Run server.py
        ssh.exec_command("python3 /path/to/server.py &")
        print(f"server.py started on {ip}")
        ssh.close()
    except Exception as e:
        print(f"Error starting server.py on {ip}: {e}")

def monitor_vms(domains):
    try:
        new_vm = conn.lookupByName(NEW_VM_NAME)
    except libvirt.libvirtError:
        print(f"Error: The specified new vm '{NEW_VM_NAME}' does not exist.")
        return

    while True:
        overload_detected = False
        for domain in list(domains):
            utilization = get_cpu_utilization(domain)
            if utilization is not None:
                print(f"Domain {domain.name()} CPU Utilization: {utilization}%")
                if utilization > OVERLOAD_THRESHOLD:
                    overload_detected = True
            else:
                print(f"Domain {domain.name()} no longer exists. Removing from list.")
                domains.remove(domain)

        if overload_detected and not new_vm.isActive():
            print("Overload detected, starting the new VM...")
            new_vm.create()  
            domains.append(new_vm)
            time.sleep(7)
            start_server_script(NEW_VM_IP, SSH_USERNAME, SSH_KEY_PATH)
            with open("server_ips.txt", "a") as f:
                f.write(f"{NEW_VM_IP}\n")
            print(f"IP {NEW_VM_IP} added to server_ips file.")
            continue

        
        if new_vm.isActive():
            new_vm_utilization = get_cpu_utilization(new_vm)
            if new_vm_utilization is not None:
                if new_vm_utilization < UNDERLOAD_THRESHOLD:
                    print(f"Underload detected, shutting down the new VM {NEW_VM_NAME}...")
                    new_vm.destroy()
                    domains.remove(new_vm)
                    with open("server_ips.txt", "r+") as f:
                        lines = f.readlines()
                        f.seek(0)
                        for line in lines:
                            if line.strip() != NEW_VM_IP:
                                f.write(line)
                        f.truncate()
                    print(f"IP {NEW_VM_IP} removed from server_ips file.")
            time.sleep(5)

if __name__ == "__main__":
    try:
        domains = [conn.lookupByName('ubuntu-server-1'), conn.lookupByName('ubuntu24.04')]
        monitor_vms(domains)
    except libvirt.libvirtError as e:
        print(f"Error initializing VMs: {e}")

