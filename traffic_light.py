import paho.mqtt.client as mqtt

# This script represents the Traffic Light at the junction
BROKER = "test.mosquitto.org"
TOPIC = "hackathon/traffic_signal/1"

def on_message(client, userdata, message):
    payload = message.payload.decode("utf-8")
    if payload == "GREEN_WAVE":
        print("\n[!!!] EMERGENCY ALERT RECEIVED [!!!]")
        print("      LIGHT STATUS: >>> GREEN <<<")
    else:
        print("Status: Normal Cycle (Red/Green)")

client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.subscribe(TOPIC)

print("t--- Traffic Light Simulation Online ---")
client.loop_forever()