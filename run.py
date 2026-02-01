import traci
import time

# CONFIGURATION
SUMO_CONFIG = "osm.sumocfg" 
CLEARING_DIST = 30  # Zap distance

def get_green_phase(tls_id, incoming_link_index):
    """Finds the phase index that gives a Green light to our specific lane."""
    try:
        logic = traci.trafficlight.getAllProgramLogics(tls_id)[0]
        for i, phase in enumerate(logic.phases):
            state = phase.state
            if len(state) > incoming_link_index:
                if state[incoming_link_index].lower() == 'g':
                    return i 
        return 0 
    except:
        return 0

def clear_traffic_ahead(ambulance_id):
    """Zap cars directly in front to prevent gridlock."""
    leader_info = traci.vehicle.getLeader(ambulance_id, dist=50)
    if leader_info:
        leader_id, dist = leader_info
        if dist < CLEARING_DIST:
            try:
                traci.vehicle.remove(leader_id)
            except:
                pass 

def run():
    sumo_cmd = ["sumo-gui", "-c", SUMO_CONFIG, "--start", "--quit-on-end"]
    traci.start(sumo_cmd)
    
    traci.simulationStep(0)
    print(" >>> SMART CITY SIMULATION STARTED <<<")
    input("Press Enter to start...")

    ambulance_active = False
    
    # TRACKING SYSTEM: 
    # Keep track of lights we are currently controlling so we can release them later
    controlled_tls_ids = set()

    while True:
        traci.simulationStep()
        
        if "AMBULANCE" in traci.vehicle.getIDList():
            if not ambulance_active:
                traci.gui.trackVehicle("View #0", "AMBULANCE")
                traci.gui.setZoom("View #0", 600)
                ambulance_active = True
            
            # 1. Clear physical obstacles
            clear_traffic_ahead("AMBULANCE")

            # 2. IDENTIFY TARGETS (The "Bubble")
            # Get list of upcoming lights sorted by distance
            all_upcoming = traci.vehicle.getNextTLS("AMBULANCE")
            
            # The "Bubble" is only the next 2 lights
            bubble_targets = all_upcoming[:2]
            bubble_ids = set()

            # --- APPLY GREEN WAVE (ACQUIRE) ---
            for tls_info in bubble_targets:
                tls_id = tls_info[0]
                tls_index = tls_info[1]
                bubble_ids.add(tls_id)

                # Calculate best Green phase
                best_phase = get_green_phase(tls_id, tls_index)
                
                # Force it Green and hold it
                traci.trafficlight.setPhase(tls_id, best_phase)
                traci.trafficlight.setPhaseDuration(tls_id, 5) # Keep extending by small increments
                
                # Mark as controlled
                controlled_tls_ids.add(tls_id)

            # --- RESTORE NORMALCY (RELEASE) ---
            # Check every light we used to control
            # We need to create a copy of the set to iterate safely while modifying it
            for old_id in list(controlled_tls_ids):
                
                # If this light is NO LONGER in the target bubble...
                if old_id not in bubble_ids:
                    
                    # ...Release it back to the city!
                    # "programID 0" is usually the default logic
                    traci.trafficlight.setProgram(old_id, "0")
                    
                    print(f"[RESTORE] Releasing Intersection {old_id} back to normal flow.")
                    controlled_tls_ids.remove(old_id)

        time.sleep(0.02)

if __name__ == "__main__":
    run()