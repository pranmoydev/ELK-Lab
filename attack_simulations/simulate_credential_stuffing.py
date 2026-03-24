#!/usr/bin/env python3
"""
Credential Stuffing Attack Simulation for ELK Stack
Generates realistic authentication logs simulating credential stuffing attacks
"""

import random
import time
import json
from datetime import datetime
import socket

class CredentialStuffingSimulator:
    def __init__(self, log_file='/var/log/attack-simulation/auth_simulation.log'):
        self.log_file = log_file
        self.hostname = socket.gethostname()
        
        # Target usernames
        self.usernames = [
            "admin", "user", "root", "test", "developer",
            "john.doe", "jane.smith", "bob.wilson", "alice.jones", "charlie.brown",
            "david.lee", "emma.davis", "frank.miller", "grace.taylor", "henry.clark"
        ]
        
        # Attacker IPs (simulated)
        self.attacker_ips = [
            "203.0.113.100",
            "198.51.100.50",
            "192.0.2.200"
        ]
        
        # Legitimate IPs (simulated)
        self.legitimate_ips = [
            "10.0.1.50",
            "10.0.1.51",
            "192.168.1.100"
        ]
    
    def generate_syslog_message(self, source_ip, username, success=False, timestamp=None):
        """Generate syslog-format authentication message"""
        if timestamp is None:
            timestamp = datetime.now()
        
        month = timestamp.strftime("%b")
        day = timestamp.strftime("%d").lstrip('0').rjust(2)
        time_str = timestamp.strftime("%H:%M:%S")
        
        if success:
            message = f"{month} {day} {time_str} {self.hostname} sshd[{random.randint(1000, 9999)}]: Accepted password for {username} from {source_ip} port {random.randint(40000, 60000)} ssh2"
        else:
            message = f"{month} {day} {time_str} {self.hostname} sshd[{random.randint(1000, 9999)}]: Failed password for {username} from {source_ip} port {random.randint(40000, 60000)} ssh2"
        
        return message
    
    def run_attack_simulation(self, num_attempts=50, duration_seconds=300):
        """Simulate credential stuffing attack"""
        print(f"[*] Starting Credential Stuffing Simulation")
        print(f"    Attempts: {num_attempts}")
        print(f"    Duration: {duration_seconds} seconds")
        print(f"    Log file: {self.log_file}")
        
        attacker_ip = random.choice(self.attacker_ips)
        print(f"    Attacker IP: {attacker_ip}")
        
        interval = duration_seconds / num_attempts
        
        with open(self.log_file, 'a') as f:
            for i in range(num_attempts):
                username = random.choice(self.usernames)
                
                # 95% failure rate
                success = random.random() < 0.05
                
                message = self.generate_syslog_message(attacker_ip, username, success)
                f.write(message + '\n')
                f.flush()
                
                if (i + 1) % 10 == 0:
                    print(f"    Generated {i + 1}/{num_attempts} attempts")
                
                time.sleep(interval)
        
        print(f"[+] Credential stuffing simulation complete!")
        print(f"    Check logs: {self.log_file}")
    
    def run_legitimate_traffic(self, num_events=20):
        """Generate legitimate authentication traffic"""
        print(f"[*] Generating legitimate authentication traffic")
        
        with open(self.log_file, 'a') as f:
            for i in range(num_events):
                source_ip = random.choice(self.legitimate_ips)
                username = random.choice(self.usernames[:5])
                
                # Mostly successful with occasional failures
                success = random.random() < 0.9
                
                message = self.generate_syslog_message(source_ip, username, success)
                f.write(message + '\n')
                f.flush()
                
                time.sleep(random.uniform(1, 5))
        
        print(f"[+] Legitimate traffic generation complete!")

def main():
    simulator = CredentialStuffingSimulator()
    
    print("=" * 60)
    print("CREDENTIAL STUFFING ATTACK SIMULATION")
    print("=" * 60)
    
    # Run attack simulation
    simulator.run_attack_simulation(num_attempts=50, duration_seconds=300)
    
    # Generate some legitimate traffic
    simulator.run_legitimate_traffic(num_events=10)
    
    print("\n" + "=" * 60)
    print("SIMULATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()