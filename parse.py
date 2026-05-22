import json
import gzip
import os
import sys

def parse_database(input_path, output_path):
    print(f"Reading from {input_path}...")
    cn_networks = []
    
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
                    network = data.get("network")
                    if network:
                        cn_networks.append(network)
                count += 1
                if count % 500000 == 0:
                    print(f"Processed {count} lines...")
            except Exception:
                pass

    print(f"Found {len(cn_networks)} CN networks.")
    
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
