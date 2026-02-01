import gzip
import random
import os

# Configuration
DEFAULT_NET_FILE = "osm.net.xml.gz"


def get_valid_edges():
    """
    Scans the network file for drivable roads (edges) that allow passenger vehicles.
    Returns a list of valid edge IDs.
    """
    target_file = DEFAULT_NET_FILE
    print(f"Scanning {target_file} for drivable roads...")
    valid_edges = []

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
                if line.startswith("<edge "):
                    if 'id="' in line:
                        idx = line.find('id="') + 4
                        end = line.find('"', idx)
                        current_edge = line[idx:end]
                        if current_edge.startswith(":"):
                            current_edge = None
                        allowed = False

                if current_edge and (line.startswith("<lane ") or line.startswith("<edge ")):
                    if 'disallow' not in line or 'passenger' not in line:
                        allowed = True

                if line.startswith("</edge>") and current_edge and allowed:
                    valid_edges.append(current_edge)

        return valid_edges
    except Exception as e:
        print(f"Error reading map: {e}")
        return []


def generate_ambulance_route():
    """
    Picks random start and end points for the ambulance and writes the route file.
    Must be re-run if the map network (osm.net.xml) changes.
    """
    edges = get_valid_edges()
    if not edges:
        return

    # Pick distinct Start/End edges
    start_edge = random.choice(edges)
    end_edge = random.choice(edges)
    while start_edge == end_edge:
        end_edge = random.choice(edges)

    print(f"Ambulance Route: {start_edge} -> {end_edge}")
    print("NOTE: Run this script again if you edit the map (netedit), as Edge IDs may change.")

    # Write Ambulance Route File
    content = (
        '<routes>\n'
        '    <vType id="ambulance" vClass="emergency" speedFactor="1.5" color="red" guiShape="emergency"/>\n'
        f'    <trip id="AMBULANCE" type="ambulance" depart="15" from="{start_edge}" to="{end_edge}" />\n'
        '</routes>\n'
    )

    with open("ambulance.rou.xml", "w") as f:
        f.write(content)
    print("'ambulance.rou.xml' created.")


if __name__ == "__main__":
    generate_ambulance_route()