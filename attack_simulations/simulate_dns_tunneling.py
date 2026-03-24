#!/usr/bin/env python3
"""
DNS Tunneling Attack Simulation for ELK Stack
Generates realistic DNS query logs simulating DNS tunneling
"""

import random
import time
import string
import socket
from datetime import datetime

class DNSTunnelingSimulator:
    def __init__(self, log_file='/var/log/attack-simulation/dns_simulation.log'):
        self.log_file = log_file
        self.hostname = socket.gethostname()
        self.client_ip = socket.gethostbyname(socket.gethostname())
        
        # Malicious C2 domain
        self.c2_domain = "malicious-c2.example.com"
        
        # Legitimate domains for baseline
        self.legitimate_domains = [
            "google.com", "facebook.com", "twitter.com",
            "github.com", "stackoverflow.com", "reddit.com"
        ]
    
    def generate_random_hex(self, length):
        """Generate random hex string"""
        return ''.join(random.choices('0123456789abcdef', k=length))
    
    def generate_random_base64(self, length):
        """Generate random base64-like string"""
        chars = string.ascii_letters + string.digits + '+/'
        return ''.join(random.choices(chars, k=length))
    
    def generate_tunneling_query(self):
        """Generate DNS tunneling query"""
        encoding_type = random.choice(['hex', 'base64'])
        
        if encoding_type == 'hex':
            encoded = self.generate_random_hex(random.randint(40, 70))
        else:
            encoded = self.generate_random_base64(random.randint(40, 60))
        
        # Create multi-level subdomain
        subdomain_parts = [
            encoded[:20],
            encoded[20:40],
            encoded[40:60] if len(encoded) > 40 else ''
        ]
        subdomain_parts = [part for part in subdomain_parts if part]
        
        query_name = '.'.join(subdomain_parts + [self.c2_domain])
        
        return query_name, encoding_type
    
    def generate_dns_log_entry(self, query_name, query_type='A', timestamp=None):
        """Generate BIND-style DNS log entry"""
        if timestamp is None:
            timestamp = datetime.now()
        
        time_str = timestamp.strftime("%d-%b-%Y %H:%M:%S.%f")[:-3]
        client_port = random.randint(40000, 60000)
        
        log_entry = f"{time_str} queries: info: client @0x7f{self.generate_random_hex(12)} {self.client_ip}#{client_port} ({query_name}): query: {query_name} IN {query_type} + ({self.client_ip})"
        
        return log_entry
    
    def run_attack_simulation(self, num_queries=100, duration_seconds=600):
        """Simulate DNS tunneling attack"""
        print(f"[*] Starting DNS Tunneling Simulation")
        print(f"    Queries: {num_queries}")
        print(f"    Duration: {duration_seconds} seconds")
        print(f"    Log file: {self.log_file}")
        print(f"    C2 Domain: {self.c2_domain}")
        
        interval = duration_seconds / num_queries
        
        with open(self.log_file, 'a') as f:
            for i in range(num_queries):
                query_name, encoding_type = self.generate_tunneling_query()
                
                # Mostly A records, some TXT
                query_type = 'TXT' if random.random() < 0.1 else 'A'
                
                log_entry = self.generate_dns_log_entry(query_name, query_type)
                f.write(log_entry + '\n')
                f.flush()
                
                if (i + 1) % 20 == 0:
                    print(f"    Generated {i + 1}/{num_queries} queries")
                
                time.sleep(interval)
        
        print(f"[+] DNS tunneling simulation complete!")
    
    def run_legitimate_traffic(self, num_queries=30):
        """Generate legitimate DNS traffic"""
        print(f"[*] Generating legitimate DNS traffic")
        
        with open(self.log_file, 'a') as f:
            for i in range(num_queries):
                domain = random.choice(self.legitimate_domains)
                
                # Sometimes add www subdomain
                if random.random() > 0.5:
                    query_name = f"www.{domain}"
                else:
                    query_name = domain
                
                query_type = random.choice(['A', 'AAAA', 'MX'])
                
                log_entry = self.generate_dns_log_entry(query_name, query_type)
                f.write(log_entry + '\n')
                f.flush()
                
                time.sleep(random.uniform(1, 3))
        
        print(f"[+] Legitimate DNS traffic generation complete!")

def main():
    simulator = DNSTunnelingSimulator()
    
    print("=" * 60)
    print("DNS TUNNELING ATTACK SIMULATION")
    print("=" * 60)
    
    # Run attack simulation
    simulator.run_attack_simulation(num_queries=100, duration_seconds=600)
    
    # Generate legitimate traffic
    simulator.run_legitimate_traffic(num_queries=30)
    
    print("\n" + "=" * 60)
    print("SIMULATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()