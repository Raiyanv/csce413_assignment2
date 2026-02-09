#!/bin/bash

# Build
echo "[*] Building Honeypot Container..."
docker build -t honeypot .

echo "[*] Starting Honeypot on localhost:2222"
container_id=$(docker run -d -p 2222:2222 --name my_honeypot honeypot)

# Wait for startup
sleep 2

# Simulate 
echo "----------------------------------------------------"
echo "[+] Attack Simulation..."
echo "----------------------------------------------------"

sshpass -p "password123" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p 2222 root@localhost "ls" 2>/dev/null
sshpass -p "admin" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p 2222 admin@localhost "ls" 2>/dev/null
sshpass -p "secret" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p 2222 root@localhost "ls" 2>/dev/null

echo "[*] Attack complete. Fetching Honeypot Logs..."
echo "----------------------------------------------------"

# 4. View Logs
docker logs $container_id | grep "Login"

# Cleanup
echo "----------------------------------------------------"
docker stop my_honeypot
docker rm my_honeypot