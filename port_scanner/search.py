import argparse
import ipaddress
import socket
from concurrent.futures import ThreadPoolExecutor
import sys
from typing import Tuple, Optional

# Docker-compose services and common ports
COMMON_PORTS = [21, 22, 80, 443, 3306, 5000, 6379, 8080, 8888, 2222]

def grab_banner(ip, port) -> Tuple[str, str, Optional[str]]:
    """Connect to a port then search for banners & flags.
    
    Args:
        ip: The target IP to query.
        port: The service that is being targeted
    Returns:
        A tuple of the port, status of the port, and banner fetch result.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.5)
        res = s.connect_ex((ip, port))
        
        if res == 0:
            # Success
            try:
                # Try querying HTTP/API services
                if port in [80, 5000, 8080, 8888]:
                    s.send(b"GET / HTTP/1.1\r\nHost: ctf\r\n\r\n")
                
                # Redis Service
                if port == 6379:
                    s.send(b"INFO\r\n")

                banner = s.recv(4096).decode(errors='ignore').strip()
                s.close()
                return port, "Open", banner
            except:
                s.close()
                return port, "Open", "No Banner"
        else:
            s.close()
            return port, "Closed", None
    except:
        return port, "Error", None

def host_scan(ip):
    """Scans a single host for open ports.
    
    Args:
        ip: The ip address to scan.
        
    Returns:
        found flags: list of found flags
    
    """
    found_flags = []
    print(f"[*] Checking {ip}...")
    
    for port in COMMON_PORTS:
        # Split up the tuple
        p, status, banner = grab_banner(str(ip), port)
        if status == "Open":
            print(f"    [+++] {ip}:{port} - Open")
            if banner and banner != "No Banner":
                # Flag pattern
                # if "FLAG" in banner or "flag" in banner:
                print(f"\t[+++] {ip}:{port}")
                print(f"\t[+++] BANNER: {banner}")
                found_flags.append(banner)
                print(f"Banner: {banner}\n")
    return found_flags

def main():
    parser = argparse.ArgumentParser(description="CTF Recon Tool")
    parser.add_argument("subnet", help="Target Subnet (e.g., 172.20.0.0/24)")
    args = parser.parse_args()

    # Parse CIDR
    try:
        network = ipaddress.ip_network(args.subnet, strict=False)
    except ValueError:
        print("[-] Invalid subnet format.")
        sys.exit(1)

    print(f"[*] Starting Recon on {network}...")
    print(f"[*] Looking for Hidden Services & Flags...\n")

    # Use Threading to scan hosts in parallel
    all_flags = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        # Skip network address and broadcast (.0 and .255)
        hosts = [ip for ip in network.hosts()]
        futures = {executor.submit(host_scan, ip): ip for ip in hosts}
        
        for future in futures:
            flags = future.result()
            all_flags.extend(flags)

    print("\n" + "="*40)
    print(f"SCAN COMPLETE. Found {len(all_flags)} flag candidates.")
    print("="*40)

if __name__ == "__main__":
    main()
