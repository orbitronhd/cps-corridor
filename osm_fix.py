import gzip
import random
import os

# CONFIGURATION
DEFAULT_NET_FILE = "osm.net.xml.gz" 

def get_valid_edges():
    target_file = DEFAULT_NET_FILE
    print(f"Scanning {target_file} for drivable roads...")
    valid_edges = []
    
    # Handle compressed/uncompressed
    opener = None
    if os.path.exists(target_file):
        opener = gzip.open
    elif os.path.exists(target_file.replace(".gz", "")):
        target_file = target_file.replace(".gz", "")
        opener = open
    else:
        print(f"ERROR: Map file '{DEFAULT_NET_FILE}' not found!")
        return []

    try:
        with opener(target_file, 'rt') as f:
            current_edge = None
            allowed = False
            
            for line in f:
                line = line.strip()
                # Check for Edge ID
                if line.startswith("<edge "):
                    if 'id="' in line:
                        idx = line.find('id="') + 4
                        end = line.find('"', idx)
                        current_edge = line[idx:end]
                        if current_edge.startswith(":"): current_edge = None # Skip internal
                        allowed = False 

                # Check Permissions
                if current_edge and (line.startswith("<lane ") or line.startswith("<edge ")):
                    # If it explicitly allows cars or has no restrictions
                    if 'disallow' not in line or 'passenger' not in line:
                        allowed = True

                # Save if valid
                if line.startswith("</edge>") and current_edge and allowed:
                    valid_edges.append(current_edge)
                    
        return valid_edges
    except Exception as e:
        print(f"Error reading map: {e}")
        return []

# --- MAIN ---
edges = get_valid_edges()
if not edges: exit()

# Pick Start/End
start_edge = random.choice(edges)
end_edge = random.choice(edges)
while start_edge == end_edge:
    end_edge = random.choice(edges)

print(f"Ambulance Route: {start_edge} -> {end_edge}")

# Write Ambulance File
content = f"""<routes>
    <vType id="ambulance" vClass="emergency" speedFactor="1.5" color="red" guiShape="emergency"/>
    <trip id="AMBULANCE" type="ambulance" depart="15" from="{start_edge}" to="{end_edge}" />
</routes>
"""

with open("ambulance.rou.xml", "w") as f:
    f.write(content)
print("SUCCESS: 'ambulance.rou.xml' created.")