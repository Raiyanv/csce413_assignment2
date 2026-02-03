import argparse
import ipaddress
import re
import socket
from concurrent.futures import ThreadPoolExecutor
import sys
from typing import Tuple, Optional
import json

# Docker-compose services and common ports
COMMON_PORTS = [21, 22, 80, 443, 3306, 5000, 6379, 8080, 8888, 2222]

def clean_banner(banner):
    """Parses raw banners into human-readable info."""
    info = {}
    # print(banner)

    
    # HTTP Response
    if "HTTP/" in banner:
        lines = banner.split('\r\n')
        info['type'] = 'HTTP'
        info['server'] = 'Unknown'
        
        for line in lines:
            if line.startswith("Server:"):
                info['server'] = line.split(":", 1)[1].strip()
            if line.startswith("Content-Type:"):
                info['content'] = line.split(":", 1)[1].strip()
        
        if "{" in banner:
            try:
                # start of JSON
                json_start = banner.find("{")
                json_data = json.loads(banner[json_start:])
                info['payload'] = json.dumps(json_data, indent=2) # 
            except:
                pass
                
    # Redis Response
    elif "redis_version" in banner or banner.startswith("$"):
        info['type'] = 'Redis Datastore'
        if "redis_version" in banner:
            start = banner.find("redis_version")
            end = banner.find("\n", start)
            info['server'] = banner[start:end].strip()
        else:
            info['server'] = "Redis Instance (Active)"

    # MySQL 
    if "mysql_native_password" in banner or "MariaDB" in banner:
        info['type'] = 'MySQL Database'
        version_match = re.search(r'(\d+\.\d+\.\d+)', banner)
        if version_match:
            info['server'] = f"MySQL {version_match.group(1)}"
        else:
            info['server'] = "MySQL (Version Unknown)"
            
    # SSH or Other
    elif "SSH" in banner:
        info['type'] = 'SSH'
        info['server'] = banner.strip()
        
    else:
        info['type'] = 'Unknown Service'
        info['server'] = banner[:50].strip() + "..." # Truncate long garbage
    # print(info) 
    return info


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

                banner = clean_banner(s.recv(4096).decode(errors='ignore').strip())
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
    """
    found_results = []
    for port in COMMON_PORTS:
        # Split up the tuple
        p, status, banner = grab_banner(str(ip), port)

        
        if status == "Open":
            print(f"[+++] {ip}:{port} - Open")
            service = banner['type']
            if banner['server'] != "...":
                service+=banner['server']
            info = {
                "ip" : ip,
                "port" : p,
                "status" : status,
                "banner" : banner,
                "service": banner['type'] 
            }
            found_results.append(info)
    return found_results


def main():
    parser = argparse.ArgumentParser(description="CTF Recon Tool")
    parser.add_argument("subnet", help="Target Subnet (e.g., 172.20.0.0/24) or CSV Target List")
    args = parser.parse_args()

    hosts = []
    # Parse CIDR
    try:
        network = ipaddress.ip_network(args.subnet, strict=False)
        print(f"[*] Mode: CIDR Scan on {network}")
        hosts = [str(ip) for ip in network.hosts()]
    except ValueError:
        # print("[-] Invalid subnet format.")
        print("[*] Mode: Custom Target List")
        hosts = [ip.strip() for ip in args.subnet.split(',') if ip.strip()]
    except Exception as e:
        print(f"[+] Critical Error. {e}")
        sys.exit(1)
    if not hosts:
        print("[+] No targets found. Exiting")
        sys.exit(1)

        
    print(f"[*] Scanning {len(hosts)} targets")

    # Use Threading to scan hosts in parallel
    all_flags = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(host_scan, ip): ip for ip in hosts}
        
        for future in futures:
            flags = future.result()
            all_flags.extend(flags)

    print("\n" + "="*40)
    print(f"SCAN COMPLETE. Found {len(all_flags)} open ports.")
    print("="*40,end="\n\n")
    print("-" * 50)
    print(f"{'IP Address':<15} {'Port':<8} {'Service':<15} {'Status':<10}")
    print("-" * 50)

    for item in all_flags:
        print(f"{str(item['ip']):<15} {item['port']:<8} {item['service']:<15} {item['status']:<10}")
if __name__ == "__main__":
    main()
