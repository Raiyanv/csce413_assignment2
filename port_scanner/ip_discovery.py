import subprocess

TARGET_CONTAINERS = [
    "2_network_database",
    "2_network_honeypot",
    "2_network_port_knocking",
    "2_network_redis",
    "2_network_secret_api",
    "2_network_secret_ssh",
    "2_network_webapp"
]

def get_container_ip(container_name):
    """
    Executes docker inspect to extract the internal IP address.
    """
    cmd = [
        "docker", "inspect", 
        "-f", "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}", 
        container_name
    ]
    
    try:
        # Run the command and capture stdout
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        ip = result.stdout.strip()
        
        if ip:
            return ip
        else:
            return None
            
    except subprocess.CalledProcessError:
        print(f"[-] Error: Could not inspect {container_name}")
        return None

def main():
    print(f"{'CONTAINER':<30} | {'INTERNAL IP':<15}")
    print("-" * 50)
    
    targets = {}

    for container in TARGET_CONTAINERS:
        ip = get_container_ip(container)
        if ip:
            print(f"{container:<30} | {ip:<15}")
            targets[container] = ip
        else:
            print(f"{container:<30} | [NOT FOUND/STOPPED]")

if __name__ == "__main__":
    main()