import gzip
import random
import os

# CONFIGURATION
NET_FILE = "osm.net.xml.gz" 
# Lower density per road, but MANY more roads = Even spread
# 300 vehs/hour on every single street is plenty for a jam
VEHS_PER_HOUR_PER_ROAD = 200  

def get_valid_edges():
    target_file = NET_FILE
    valid_edges = []
    
    # Handle compressed/uncompressed
    opener = None
    if os.path.exists(target_file):
        opener = gzip.open
    elif os.path.exists(target_file.replace(".gz", "")):
        target_file = target_file.replace(".gz", "")
        opener = open
    else:
        print("ERROR: Map file not found!")
        return []

    try:
        with opener(target_file, 'rt') as f:
            current_edge = None
            allowed = False
            
            for line in f:
                line = line.strip()
                if line.startswith("<edge "):
                    if 'id="' in line:
                        idx = line.find('id="') + 4
                        end = line.find('"', idx)
                        current_edge = line[idx:end]
                        if current_edge.startswith(":"): current_edge = None 
                        allowed = False 

                if current_edge and (line.startswith("<lane ") or line.startswith("<edge ")):
                    if 'disallow' not in line or 'passenger' not in line:
                        allowed = True

                if line.startswith("</edge>") and current_edge and allowed:
                    valid_edges.append(current_edge)
                    
        return list(set(valid_edges)) # Remove duplicates
    except Exception as e:
        print(f"Error reading map: {e}")
        return []

# --- MAIN LOGIC ---
edges = get_valid_edges()
if not edges: exit()

print(f"Found {len(edges)} total roads.")
print("Generating uniform traffic on EVERY road...")

flows = []
used_routes = 0

# LOOP THROUGH EVERY SINGLE EDGE
for start_edge in edges:
    
    # Pick a random end point that is NOT the start point
    end_edge = random.choice(edges)
    attempts = 0
    while end_edge == start_edge and attempts < 10:
        end_edge = random.choice(edges)
        attempts += 1
    
    # Create a flow for this specific road
    # This guarantees that EVERY street in your city is a starting point for cars
    flows.append(f'    <flow id="uniform_{used_routes}" type="car" begin="0" end="300" vehsPerHour="{VEHS_PER_HOUR_PER_ROAD}" from="{start_edge}" to="{end_edge}" />')
    used_routes += 1

# Write XML
with open("traffic.rou.xml", "w") as f:
    f.write("""<routes>
    <vType id="car" vClass="passenger" color="yellow" guiShape="passenger"/>
""")
    f.write("\n".join(flows))
    f.write("\n</routes>")

print(f"SUCCESS! Generated {used_routes} traffic flows covering the entire map.")