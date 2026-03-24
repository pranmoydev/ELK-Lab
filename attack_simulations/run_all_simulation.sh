#!/bin/bash

echo "=================================================================="
echo "ELK STACK ATTACK SIMULATION - MASTER CONTROL SCRIPT"
echo "=================================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create log directory if it doesn't exist
sudo mkdir -p /var/log/attack-simulation
sudo chmod 755 /var/log/attack-simulation

echo -e "${GREEN}[+] Log directory ready: /var/log/attack-simulation${NC}"
echo ""

# Function to run simulation
run_simulation() {
    local script_name=$1
    local description=$2
    
    echo -e "${YELLOW}[*] Running: $description${NC}"
    echo "    Script: $script_name"
    
    if [ -f "$script_name" ]; then
        python3 "$script_name"
        echo -e "${GREEN}[+] $description completed${NC}"
    else
        echo -e "${RED}[!] Error: $script_name not found${NC}"
    fi
    echo ""
}

# Menu
echo "Select simulation to run:"
echo "1) Credential Stuffing"
echo "2) DNS Tunneling"
echo "3) PowerShell Exploitation"
echo "4) Run All Simulations"
echo "5) Run All in Background (continuous)"
echo "6) Exit"
echo ""

read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        run_simulation "simulate_credential_stuffing.py" "Credential Stuffing Simulation"
        ;;
    2)
        run_simulation "simulate_dns_tunneling.py" "DNS Tunneling Simulation"
        ;;
    3)
        run_simulation "simulate_powershell_exploitation.py" "PowerShell Exploitation Simulation"
        ;;
    4)
        echo -e "${GREEN}[+] Running all simulations sequentially...${NC}"
        echo ""
        run_simulation "simulate_credential_stuffing.py" "Credential Stuffing Simulation"
        sleep 5
        run_simulation "simulate_dns_tunneling.py" "DNS Tunneling Simulation"
        sleep 5
        run_simulation "simulate_powershell_exploitation.py" "PowerShell Exploitation Simulation"
        ;;
    5)
        echo -e "${GREEN}[+] Starting continuous attack simulation in background...${NC}"
        echo ""
        nohup bash -c '
            while true; do
                python3 simulate_credential_stuffing.py >> /var/log/attack-simulation/master.log 2>&1
                sleep 600
                python3 simulate_dns_tunneling.py >> /var/log/attack-simulation/master.log 2>&1
                sleep 600
                python3 simulate_powershell_exploitation.py >> /var/log/attack-simulation/master.log 2>&1
                sleep 600
            done
        ' &
        
        PID=$!
        echo "Background process started with PID: $PID"
        echo "To stop: kill $PID"
        echo "Logs: tail -f /var/log/attack-simulation/master.log"
        ;;
    6)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo "=================================================================="
echo -e "${GREEN}SIMULATION COMPLETE${NC}"
echo "=================================================================="
echo ""
echo "Check Filebeat status: sudo systemctl status filebeat"
echo "View Filebeat logs: sudo tail -f /var/log/filebeat/filebeat"
echo "View simulation logs: sudo tail -f /var/log/attack-simulation/*.log"
echo ""
echo "On ELK server, check Kibana for incoming data:"
echo "- http://<SERVER_IP>:5601"
echo ""