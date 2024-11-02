import paramiko

def run_script_on_vm(host, username, script_path, vm_script_path, ssh_key_path=None, password=None):
    """
    SSH into a VM and run a script on it.

    :param host: Hostname or IP address of the VM.
    :param username: SSH username.
    :param script_path: Path of the script on the local machine to copy over.
    :param vm_script_path: Path on the VM where the script will be stored and run.
    :param ssh_key_path: Path to the SSH key (optional, if not using password).
    :param password: Password for SSH login (optional if using an SSH key).
    """
    # Initialize SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to VM
        if ssh_key_path:
            ssh.connect(hostname=host, username=username, key_filename=ssh_key_path)
        else:
            ssh.connect(hostname=host, username=username, password=password)

        # Upload script to VM
        sftp = ssh.open_sftp()
        sftp.put(script_path, vm_script_path)
        sftp.close()

        # Run the script on the VM
        stdin, stdout, stderr = ssh.exec_command(f"python3 {vm_script_path}")
        
        # Print output and errors
        print("Output:")
        for line in stdout.read().decode().splitlines():
            print(line)

        print("Errors:")
        for line in stderr.read().decode().splitlines():
            print(line)

    finally:
        # Close the SSH connection
        ssh.close()

# Example usage:
host = "your_vm_ip_or_hostname"  # Replace with the VM's IP or hostname
username = "tuni"
script_path = "/path/to/your/local/script.py"  # Path to the script on your local machine
vm_script_path = "/path/on/vm/script.py"  # Path to place the script on the VM
ssh_key_path = "/path/to/ssh/key"  # Path to the SSH key, or None if using a password

run_script_on_vm(host, username, script_path, vm_script_path, ssh_key_path)

