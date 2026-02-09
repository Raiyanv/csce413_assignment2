#!/usr/bin/env python3
"""Starter template for the honeypot assignment."""

import logging
import os
from time import sleep
import socket
import threading
import paramiko
from datetime import datetime

# ignore the wordy/irrelevant info
LOG_PATH = "/app/logs/honeypot.log"
logging.getLogger("paramiko.transport").setLevel(logging.CRITICAL)
logging.getLogger("paramiko.transport.sftp").setLevel(logging.CRITICAL)


def setup_logging():
    os.makedirs("/app/logs", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()],
    )

BIND_INT = "0.0.0.0"
TARGET_PORT = 22
KEY = paramiko.RSAKey.generate(2048)


class HoneypotServer(paramiko.ServerInterface):
    def __init__(self, ip):
        self.client_ip = ip
        self.event = threading.Event()

    def check_channel_request(self, kind: str, channel_id: int): 
        '''
        Determine if a channel request of a given type will be granted, and return OPEN_SUCCEEDED or an error code.
        This method is called in server mode when the client requests a channel, after authentication is complete.
        Returns either OPEN_SUCCEEDED (0) or error code 

        OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
        OPEN_FAILED_CONNECT_FAILED
        OPEN_FAILED_UNKNOWN_CHANNEL_TYPE
        OPEN_FAILED_RESOURCE_SHORTAGE
        '''
        return paramiko.OPEN_SUCCEEDED
    
    def check_auth_password(self, username, password):
        logging.info(f"[+] Login Attempt | IP: {self.client_ip} | User: {username} | Password: {password}")
        sleep(2)
        return paramiko.AUTH_FAILED


def handle_connection(client, address):
    client_ip = address[0]
    logging.info(f"Incoming connection from: {client_ip}:{address[1]}")

    ssh_trans = None
    try:
        ssh_trans = paramiko.Transport(client)
        ssh_trans.local_version = "SSH-2.0-dropbear_2022.82"
        ssh_trans.add_server_key(KEY)

        server = HoneypotServer(client_ip)
        try:
            ssh_trans.start_server(server=server)
        except paramiko.SSHException:
            return
        except EOFError:
            return
        channel = ssh_trans.accept(15)
        if channel is None:
            ssh_trans.close()
            return
        
    except Exception as e:
        logging.error(f"Connection Error {e}")
    finally:
        if ssh_trans:
            ssh_trans.close()
        client.close()
        
    
def run_honeypot():
    logger = logging.getLogger("Honeypot")
    logger.info("Honeypot starter template running.")
    # logger.info("TODO: Implement protocol simulation, logging, and alerting.")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
        sock.bind((BIND_INT, TARGET_PORT))
        sock.listen(100)
        logger.info(f"Honeypot active on {BIND_INT}:{TARGET_PORT}")

        while True:
            client, addr = sock.accept()
            client_thread = threading.Thread(target=handle_connection, args=(client, addr))
            client_thread.start()

    except Exception as e:
        logger.error(f"Failed to serve {e}")    



if __name__ == "__main__":
    setup_logging()
    run_honeypot()
