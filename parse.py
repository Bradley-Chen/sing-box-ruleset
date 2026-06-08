import json
import gzip
import os
import sys
import ipaddress

def parse_database(input_path, output_path):
    print(f"Reading from {input_path}...")
    ipv4_nets = []
    ipv6_nets = []
    
    open_func = gzip.open if input_path.endswith('.gz') else open
    mode = 'rt' if input_path.endswith('.gz') else 'r'
    
    count = 0
    with open_func(input_path, mode, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                if data.get("country_code") == "CN":
                    network_str = data.get("network")
                    if network_str:
                        ip_net = ipaddress.ip_network(network_str, strict=False)
                        if ip_net.version == 4:
                            ipv4_nets.append(ip_net)
                        else:
                            ipv6_nets.append(ip_net)
                count += 1
                if count % 500000 == 0:
                    print(f"Processed {count} lines...")
            except Exception:
                pass

    print(f"Found raw networks: IPv4={len(ipv4_nets)}, IPv6={len(ipv6_nets)}")
    
    print("Collapsing (aggregating) adjacent CIDRs...")
    collapsed_ipv4 = list(ipaddress.collapse_addresses(ipv4_nets))
    collapsed_ipv6 = list(ipaddress.collapse_addresses(ipv6_nets))
    
    print(f"Collapsed networks: IPv4={len(collapsed_ipv4)}, IPv6={len(collapsed_ipv6)}")
    
    # Sort for consistent output and cleaner git diffs (IPv4 first, then IPv6)
    cn_networks = [str(net) for net in collapsed_ipv4] + [str(net) for net in collapsed_ipv6]
    
    ruleset = {
        "version": 1,
        "rules": [
            {
                "ip_cidr": cn_networks
            }
        ]
    }

    print(f"Writing to {output_path}...")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(ruleset, f, indent=2)
    print("Generation complete!")

if __name__ == "__main__":
    infile = sys.argv[1] if len(sys.argv) > 1 else "ipinfo_lite.json"
    outfile = sys.argv[2] if len(sys.argv) > 2 else "geoip-cn.json"
    parse_database(infile, outfile)
