#!/usr/bin/env python3
"""Starter template for the port knocking server."""

import argparse
import logging
import socket
import time
import subprocess
import select
import threading
import sys


DEFAULT_KNOCK_SEQUENCE = [7000,8000,9000]
DEFAULT_PROTECTED_PORT = 2222
DEFAULT_SEQUENCE_WINDOW = 10.0

client_status = {}


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )



def exec_cmd(command):
    try:
        subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        pass # ignore errors

def setup_firewall(protected_port):
    logging.info(f"Firewall Setup: Blocked Port = {protected_port}")
    exec_cmd("iptables -F")
    exec_cmd("iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT")

        # local host access for testing
    exec_cmd("iptables -A INPUT -i lo -j ACCEPT")
    
    exec_cmd(f"iptables -A INPUT -p tcp --dport {protected_port} -j DROP")
    
    

def open_protected_port(ip, protected_port):
    """Open the protected port using firewall rules."""
    # TODO: Use iptables/nftables to allow access to protected_port.
    logging.info("Opening firewall for port %s", protected_port)
    exec_cmd(f"iptables -I INPUT 1 -s {ip} -p tcp --dport {protected_port} -j ACCEPT")


    
    thread = threading.Timer(20, close_protected_port, args=[ip, protected_port])
    thread.start()
    logging.info(f"Port Closing in... 20 seconds")

def close_protected_port(ip, protected_port):
    """Close the protected port using firewall rules."""
    # TODO: Remove firewall rules for protected_port.
    logging.info("Closing firewall for port %s", protected_port)
    try:
        exec_cmd(f"iptables -D INPUT -s {ip} -p tcp --dport {protected_port} -j ACCEPT")
    except:
        logging.warning(f"Could not remove rule for {ip}")



def listen_for_knocks(sequence, window_seconds, protected_port):
    """Listen for knock sequence and open the protected port."""
    logger = logging.getLogger("KnockServer")
    logger.info("Listening for knocks: %s", sequence)
    logger.info("Protected port: %s", protected_port)

    # TODO: Create UDP or TCP listeners for each knock port.
    # TODO: Track each source IP and its progress through the sequence.
    # TODO: Enforce timing window per sequence.
    # TODO: On correct sequence, call open_protected_port().
    # TODO: On incorrect sequence, reset progress.
# Create UDP sockets for each port in the sequence
    sockets = []
    # Map socket objects back to port numbers: { socket_obj: 7000 }
    sock_map = {} 

    try:
        for port in sequence:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0', port))
            s.setblocking(False) # Non-blocking for select()
            sockets.append(s)
            sock_map[s] = port
            logger.debug(f"Bound to UDP port {port}")
    except PermissionError:
        logger.error("Failed to bind ports. Are you running as root?")
        sys.exit(1)

    while True:
        readable, _, _ = select.select(sockets, [], [], 1.0)

        # Cleanup: Check for timed-out clients periodically
        now = time.time()
        
        # Process incoming knocks
        for s in readable:
            logging.info("Received knock")
            try:
                data, addr = s.recvfrom(1024)
                ip = addr[0]
                port = sock_map[s]
                
                handle_knock(ip, port, sequence, window_seconds, protected_port)
            except Exception as e:
                logger.error(f"Error receiving packet: {e}")



def handle_knock(ip, port, sequence, window_seconds, protected_port):
    """Process a single knock"""
    now = time.time()
    
    # Initialize state for new IPs
    if ip not in client_status:
        client_status[ip] = {'index': 0, 'start_time': 0}

    state = client_status[ip]

    # Check for timeout (Reset if too much time passed since first knock)
    if state['index'] > 0 and (now - state['start_time'] > window_seconds):
        logging.info(f"[{ip}] Sequence timed out. Resetting.")
        state['index'] = 0
        state['start_time'] = 0

    # Determine which port we expect next
    expected_port = sequence[state['index']]

    if port == expected_port:
        # Correct Knock!
        if state['index'] == 0:
            state['start_time'] = now # Start the timer on first knock

        state['index'] += 1
        logging.info(f"[{ip}] Correct knock on {port} ({state['index']}/{len(sequence)})")

        # Check if sequence is complete
        if state['index'] == len(sequence):
            logging.info(f"[{ip}] SEQUENCE COMPLETE!")
            open_protected_port(ip, protected_port)
            # Reset state so they can knock again later if needed
            state['index'] = 0 
            state['start_time'] = 0
    else:
        # Incorrect Knock - Reset progress
        # Only log if they had progress, otherwise it's just noise
        if state['index'] > 0:
            logging.info(f"[{ip}] Wrong knock on {port}. Expected {expected_port}. Resetting.")
        state['index'] = 0
        state['start_time'] = 0
        
        
def parse_args():
    parser = argparse.ArgumentParser(description="Port knocking server starter")
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
        "--window",
        type=float,
        default=DEFAULT_SEQUENCE_WINDOW,
        help="Seconds allowed to complete the sequence",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    print(f"Starting Server")
    setup_logging()


    

    try:
        sequence = [int(port) for port in args.sequence.split(",")]
    except ValueError:
        raise SystemExit("Invalid sequence. Use comma-separated integers.")

    setup_firewall(args.protected_port)
    try:
        listen_for_knocks(sequence, args.window, args.protected_port)
    except KeyboardInterrupt:
        logging.info(f"Shutting Down")
        exec_cmd("iptables -A INPUT -p tcp --dport 2222 -j DROP")

        sys.exit(0)


if __name__ == "__main__":
    main()
