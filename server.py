import paho.mqtt.client as mqtt
import json
from math import radians, cos, sin, asin, sqrt

# Config
LIGHT_LOCATION = (10.0050, 76.3050) # The fixed location of the traffic light
TRIGGER_DISTANCE = 300 # Meters

# Haversine Formula (Calculates distance between two GPS points)
def calculate_distance(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return c * 6371 * 1000 # Returns meters

def on_message(client, userdata, message):
    data = json.loads(message.payload.decode("utf-8"))
    distance = calculate_distance(data["lat"], data["long"], LIGHT_LOCATION[0], LIGHT_LOCATION[1])
    
    print(f"Ambulance is {int(distance)} meters away...")

    if distance < TRIGGER_DISTANCE:
        print(">>> CRITICAL RANGE! TRIGGERING GREEN LIGHT <<<")
        client.publish("hackathon/traffic_signal/1", "GREEN_WAVE")
    else:
        client.publish("hackathon/traffic_signal/1", "NORMAL")

client = mqtt.Client()
client.on_message = on_message
client.connect("test.mosquitto.org", 1883, 60)
client.subscribe("hackathon/ambulance/location")

print("--- Server Monitoring System Online ---")
client.loop_forever()