#!/usr/bin/env python3
import paho.mqtt.client as mqtt
from flask import Flask, request, jsonify
import threading
import json

app = Flask(__name__)

# MQTT Broker details (adjust as needed)
broker = "mosquitto-broker"
port = 1883

# Create a global MQTT client for the serverless layer
mqtt_client = mqtt.Client()

# Callback for when messages are received from the publisher
def on_message(client, userdata, msg):
    print(f"[MQTT] Received on topic {msg.topic}: {msg.payload.decode('utf-8')}")

# Function to run the MQTT loop in a separate thread
def mqtt_loop():
    mqtt_client.on_message = on_message
    mqtt_client.connect(broker, port)
    mqtt_client.subscribe("/home/publish/#")
    mqtt_client.loop_forever()

# HTTP endpoint to change the fan speed
@app.route('/home/<device>', methods=['POST'])
def fan(device):
    data = request.get_json()
    if not data or 'value' not in data:
        return jsonify({"error": "Expected JSON payload with 'speed'"}), 400
    value = data['value']
    try:
        # Publish new speed value to the fan device
        mqtt_client.publish("/home/subscribe/"+device, str(value))
        return jsonify({"message": "Update published", "new_value": value}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Start the MQTT loop in a separate thread
    mqtt_thread = threading.Thread(target=mqtt_loop, daemon=True)
    mqtt_thread.start()

    # Start the Flask HTTP server on port 8080
    app.run(host='0.0.0.0', port=8080)
