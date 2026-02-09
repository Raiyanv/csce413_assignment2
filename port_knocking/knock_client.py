#!/usr/bin/env python3
"""Starter template for the port knocking client."""

import argparse
import socket
import time
import sys



DEFAULT_KNOCK_SEQUENCE = ["7000,8000,9000"]
DEFAULT_PROTECTED_PORT = 2222
DEFAULT_DELAY = 0.3


def send_knock(target, port, delay, proto='UDP'):
    """
    Send a single knock to the target port over UDP.
    
    """
    try:
        ip = socket.gethostbyname(target)
        
        if proto.upper() == 'UDP':
            # Create UDP socket
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.settimeout(1.0)
                # Send empty packet
                s.sendto(b'', (ip, port))
                print(f"[+] Knock sent to {target}:{port} (UDP)")
                
        elif proto.upper() == 'TCP':
            # Create TCP socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1.0)
                result = s.connect_ex((ip, port))
                print(f"[+] Knock sent to {target}:{port} (TCP): {result}")
                
    except socket.gaierror:
        print(f"[!] Error: Could not resolve hostname {target}")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Error knocking port {port}: {e}")

    time.sleep(delay)


def perform_knock_sequence(target, sequence, delay, proto):
    """Send the full knock sequence."""
    for port in sequence:
        send_knock(target, port, delay, proto)


def check_protected_port(target, protected_port):
    """Try connecting to the protected port after knocking."""
    # TODO: Replace with real service connection if needed.
    try:
        with socket.create_connection((target, protected_port), timeout=3.0):
            print(f"[+] Connected to protected port {protected_port}")
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        print(f"[-] Could not connect to port {protected_port}")
        print("[-] The knock sequence failed.")
        return False

def parse_args():
    parser = argparse.ArgumentParser(description="Port knocking client starter")
    parser.add_argument("--target", required=True, help="Target host or IP")
    parser.add_argument(
        "--sequence",
        default=",".join(str(port) for port in DEFAULT_KNOCK_SEQUENCE),
        help="Comma-separated knock ports",
    )
    parser.add_argument(
        "--protected-port",
        type=int,
        default=DEFAULT_PROTECTED_PORT,
        help="Protected service port",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY,
        help="Delay between knocks in seconds",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Attempt connection to protected port after knocking",
    )
    parser.add_argument(
        "--protocol",
        choices=['UDP', 'TCP'],
        default='UDP',
        help="Protocol to use for knocking (default: UDP)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        sequence = [int(port) for port in args.sequence.split(",")]
    except ValueError:
        raise SystemExit("Invalid sequence. Use comma-separated integers.")

    perform_knock_sequence(args.target, sequence, args.delay, args.protocol)

    if args.check:
        time.sleep(3)
        check_protected_port(args.target, args.protected_port)


if __name__ == "__main__":
    main()
