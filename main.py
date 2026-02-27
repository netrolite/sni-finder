import socket
import ipaddress
from collections import defaultdict

def map_domains_to_subnets(domains_file, subnets_file, output_file):
    # 1. Parse the subnets
    subnets = []
    try:
        with open(subnets_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    # strict=False allows host bits to be set in the network definition
                    subnets.append(ipaddress.ip_network(line, strict=True))
    except FileNotFoundError:
        print(f"Error: Could not find '{subnets_file}'.")
        return

    # 2. Parse the domains
    domains = []
    try:
        with open(domains_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    domains.append(line)
    except FileNotFoundError:
        print(f"Error: Could not find '{domains_file}'.")
        return

    # 3. Resolve domains and group them by subnet
    # Using a set to prevent duplicate domain entries under a single subnet 
    # if a domain resolves to multiple IPs within the same subnet.
    subnet_to_domains = defaultdict(set) 

    print("Resolving domains and matching against subnets...")
    for domain in domains:
        try:
            # gethostbyname_ex gets all IPv4 addresses for a domain
            _, _, ip_addresses = socket.gethostbyname_ex(domain)
            
            for ip_str in ip_addresses:
                try:
                    ip_obj = ipaddress.ip_address(ip_str)
                    
                    # Check the IP against all provided subnets
                    for subnet in subnets:
                        if ip_obj in subnet:
                            subnet_to_domains[str(subnet)].add(domain)
                            
                except ValueError:
                    print("  [!] invalid IP address") # log if it returns an oddly formatted IP
                    
        except socket.gaierror:
            print(f"  [!] DNS Lookup failed for: {domain}")
        except Exception as e:
            print(f"  [!] Error processing {domain}: {e}")

    # 4. Format and write the output
    try:
        with open(output_file, 'w') as f:
            for subnet_str, matched_domains in subnet_to_domains.items():
                f.write(f"{subnet_str}:\n")
                # Sort domains alphabetically for a cleaner output
                for d in sorted(matched_domains):
                    f.write(f"{d}\n")
                f.write("\n") # Add blank line between subnet groups
                
        print(f"\nSuccess! Results have been written to '{output_file}'.")
    except IOError as e:
        print(f"Error writing to '{output_file}': {e}")

if __name__ == "__main__":
    # Define your filenames here
    DOMAINS_TXT = "domains.txt"
    SUBNETS_TXT = "subnetsYandex.txt"
    OUTPUT_TXT = "output.txt"
    
    map_domains_to_subnets(DOMAINS_TXT, SUBNETS_TXT, OUTPUT_TXT)
