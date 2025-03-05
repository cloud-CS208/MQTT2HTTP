#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import threading
import time
import json

# Global variable for fan speed (initial speed)
speed = 50  

# MQTT Broker details (adjust if needed)
broker = "mosquitto-broker"
port = 1883

# Callback when a subscribed message is received
def on_message(client, userdata, msg):
    global speed
    try:
        # Assume payload is a simple number (as a string)
        new_speed = int(msg.payload.decode('utf-8'))
        print(f"[Subscriber] Received new speed: {new_speed}")
        speed = new_speed
    except Exception as e:
        print(f"[Subscriber] Error processing message: {e}")

# Publisher thread: publish the fan speed and health every 5 seconds
def publisher_thread():
    pub_client = mqtt.Client()
    pub_client.connect(broker, port)
    while True:
        payload = json.dumps({"speed": speed, "health": "OK"})
        pub_client.publish("/home/publish/fan", payload)
        print(f"[Publisher] Published: {payload}")
        time.sleep(5)

# Subscriber thread: listen for new speed values
def subscriber_thread():
    sub_client = mqtt.Client()
    sub_client.on_message = on_message
    sub_client.connect(broker, port)
    sub_client.subscribe("/home/subscribe/fan")
    sub_client.loop_forever()

if __name__ == '__main__':
    # Create and start publisher and subscriber threads
    t_pub = threading.Thread(target=publisher_thread, daemon=True)
    t_sub = threading.Thread(target=subscriber_thread, daemon=True)
    t_pub.start()
    t_sub.start()

    # Keep the main thread running
    while True:
        time.sleep(1)
