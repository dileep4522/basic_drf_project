import paho.mqtt.client as mqtt
import time
import json
from datetime import datetime

# Initialize an empty list to store machine data
machine_data_list = []

def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print('Connected successfully to HiveMQ broker')
        client.subscribe('machine_data_dev')
    else:
        print(f"Connection failed with reason code {reason_code}. Attempting to reconnect...")
        client.reconnect()

def on_message(client, userdata, msg):
    global machine_data_list  # Use the global variable to store data
    try:
        connected_machine_data = json.loads(msg.payload.decode())  # Assuming the payload is a string
        topic = msg.topic
        data = {
            "timestamp": datetime.now().isoformat(),
            "machine_data": connected_machine_data
        }
        # Append the new data to the list
        machine_data_list.append(data)

        # Save data to JSON file after each message
        save_data_to_json()

        print('Received message:', connected_machine_data, 'on topic:', topic)

    except Exception as e:
        print(f"Failed to process message: {str(e)}")

def on_disconnect(client, userdata, rc, properties=None, *args):
    print(f"Disconnected with result code {rc}")
    # Optionally save data on disconnect
    save_data_to_json()

    while not client.is_connected():
        try:
            print("Attempting to reconnect...")
            client.reconnect()
            time.sleep(1)
        except Exception as e:
            print(f"Reconnection failed: {str(e)}")
            time.sleep(5)

def save_data_to_json():
    # Save the collected machine data to a JSON file
    if machine_data_list:
        with open("machine_data.json", "w") as json_file:  # Open in write mode
            json.dump(machine_data_list, json_file, indent=4)
        print("Data saved to machine_data.json")

# Create the client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# Optional: Set username and password if required by the broker
# Comment out or remove if using HiveMQ's public broker
# client.username_pw_set(username="your_username", password="your_password")  # Replace with your credentials if needed

client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# Connect to the broker
client.connect(
   host='broker.hivemq.com',
   port=1883,
   keepalive=60
)

# Start the loop to process incoming and outgoing messages
try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Disconnecting from broker...")
    client.disconnect()
    save_data_to_json()  # Save data on manual exit
