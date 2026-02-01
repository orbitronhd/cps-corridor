import paho.mqtt.client as mqtt
import time
import json

BROKER = "test.mosquitto.org"
TOPIC = "hackathon/ambulance/location"

client = mqtt.Client()
client.connect(BROKER, 1883, 60)

# Simulate a route: [Latitude, Longitude]
# Let's say the Traffic Light is at [10.0050, 76.3050]
route = [
    {"lat": 10.0010, "long": 76.3010}, # 600m away
    {"lat": 10.0020, "long": 76.3020}, # 450m away
    {"lat": 10.0035, "long": 76.3035}, # 250m away (Should Trigger!)
    {"lat": 10.0050, "long": 76.3050}  # 0m away (Arrived)
]

print("--- Ambulance Started Emergency Run ---")
for pos in route:
    payload = json.dumps(pos)
    print(f"Sending Location: {payload}")
    client.publish(TOPIC, payload)
    time.sleep(3) # Wait 3 seconds between updates

print("--- Ambulance Arrived at Destination ---")