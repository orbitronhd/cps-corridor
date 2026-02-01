import gzip
import random
import os

# Configuration
NET_FILE = "osm.net.xml.gz"
VEHS_PER_HOUR_PER_ROAD = 200


def get_valid_edges():
    """Parses the SUMO network file to find all valid edge IDs allowed for cars."""
    target_file = NET_FILE
    valid_edges = []

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
                        if current_edge.startswith(":"):
                            current_edge = None  # Skip internal edges
                        allowed = False

                if current_edge and (line.startswith("<lane ") or line.startswith("<edge ")):
                    # Check if passenger cars are allowed (no 'disallow' or explicit 'passenger')
                    if 'disallow' not in line or 'passenger' not in line:
                        allowed = True

                if line.startswith("</edge>") and current_edge and allowed:
                    valid_edges.append(current_edge)

        return list(set(valid_edges))  # Remove duplicates
    except Exception as e:
        print(f"Error reading map: {e}")
        return []


def generate_traffic():
    edges = get_valid_edges()
    if not edges:
        exit()

    print(f"Found {len(edges)} total roads.")
    print("Generating uniform traffic on EVERY road...")

    flows = []
    used_routes = 0

    # Loop through every single edge to guarantee full city coverage
    for start_edge in edges:
        end_edge = random.choice(edges)
        attempts = 0
        
        # Ensure start and end are different
        while end_edge == start_edge and attempts < 10:
            end_edge = random.choice(edges)
            attempts += 1

        # Create a traffic flow starting from this specific road
        flow_str = (
            f'    <flow id="uniform_{used_routes}" type="car" begin="0" end="300" '
            f'vehsPerHour="{VEHS_PER_HOUR_PER_ROAD}" from="{start_edge}" to="{end_edge}" />'
        )
        flows.append(flow_str)
        used_routes += 1

    with open("traffic.rou.xml", "w") as f:
        f.write('<routes>\n')
        f.write('    <vType id="car" vClass="passenger" color="yellow" guiShape="passenger"/>\n')
        f.write("\n".join(flows))
        f.write("\n</routes>")

    print(f"Generated {used_routes} traffic flows covering the entire map.")


if __name__ == "__main__":
    generate_traffic()