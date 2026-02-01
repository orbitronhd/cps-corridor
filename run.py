import time
import traci


# Configuration
SUMO_CONFIG = "osm.sumocfg"
CLEARING_DIST = 30  # Distance ahead to clear traffic


def get_green_phase(tls_id, incoming_link_index):
    """Finds the phase index that gives a Green light to a specific lane."""
    try:
        logic = traci.trafficlight.getAllProgramLogics(tls_id)[0]
        for i, phase in enumerate(logic.phases):
            state = phase.state
            if len(state) > incoming_link_index:
                if state[incoming_link_index].lower() == 'g':
                    return i
        return 0
    except Exception:
        return 0


def clear_traffic_ahead(ambulance_id):
    """Removes vehicles directly in front of the ambulance to prevent gridlock."""
    leader_info = traci.vehicle.getLeader(ambulance_id, dist=50)
    if leader_info:
        leader_id, dist = leader_info
        if dist < CLEARING_DIST:
            try:
                traci.vehicle.remove(leader_id)
            except traci.TraCIException:
                pass


def run():
    sumo_cmd = ["sumo-gui", "-c", SUMO_CONFIG, "--start", "--quit-on-end"]
    traci.start(sumo_cmd)

    traci.simulationStep(0)
    print("Ambulance Priority Traffic Light System:")
    input("Press Enter to start...")

    ambulance_active = False
    controlled_tls_ids = set()

    try:
        while True:
            traci.simulationStep()

            if "AMBULANCE" in traci.vehicle.getIDList():
                if not ambulance_active:
                    traci.gui.trackVehicle("View #0", "AMBULANCE")
                    traci.gui.setZoom("View #0", 600)
                    ambulance_active = True

                # Clear physical obstacles
                clear_traffic_ahead("AMBULANCE")

                # Identify targets
                all_upcoming = traci.vehicle.getNextTLS("AMBULANCE")
                bubble_targets = all_upcoming[:2]
                bubble_ids = set()

                for tls_info in bubble_targets:
                    tls_id = tls_info[0]
                    tls_index = tls_info[1]
                    bubble_ids.add(tls_id)

                    best_phase = get_green_phase(tls_id, tls_index)

                    # Force it Green and hold it by extending duration
                    traci.trafficlight.setPhase(tls_id, best_phase)
                    traci.trafficlight.setPhaseDuration(tls_id, 5)

                    controlled_tls_ids.add(tls_id)

                for old_id in list(controlled_tls_ids):
                    if old_id not in bubble_ids:
                        # Release back to default logic (Program 0)
                        traci.trafficlight.setProgram(old_id, "0")
                        print(f"[RESTORE] Releasing Intersection {old_id}.")
                        controlled_tls_ids.remove(old_id)

            time.sleep(0.02)
    except traci.exceptions.FatalTraCIError:
        print("Simulation closed by user.")
    finally:
        traci.close()


if __name__ == "__main__":
    run()