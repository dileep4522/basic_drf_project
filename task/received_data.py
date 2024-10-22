import websocket
import json
import datetime
import os
import threading

# File to store the received data
json_file_path = 'received_data.json'

# Time limit (in seconds) for receiving data
TIMEOUT_LIMIT = 30

# Variable to track the time when the last message was received
last_message_time = None


# Function to load existing data from the JSON file
def load_existing_data():
    if os.path.exists(json_file_path):
        # Check if the file is empty
        if os.stat(json_file_path).st_size == 0:
            return []  # Return an empty list if the file is empty

        # Try loading JSON data
        try:
            with open(json_file_path, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            # If there's an error decoding, return an empty list
            print(f"Error: {json_file_path} contains invalid JSON. Starting with an empty list.")
            return []
    return []  # Return an empty list if the file doesn't exist


# Function to save data to the JSON file
def save_data(data):
    with open(json_file_path, 'w') as file:
        json.dump(data, file, indent=4)


# List to store received messages
received_messages = load_existing_data()


def on_message(ws, message):
    global last_message_time
    # Get the current timestamp and update the time when the last message was received
    last_message_time = datetime.datetime.now()

    # Parse the received message to convert it from string to JSON object
    try:
        message_data = json.loads(message)
    except json.JSONDecodeError:
        print("Error: Failed to decode message data, storing it as a string.")
        message_data = message  # If decoding fails, keep the message as a string

    # Create a dictionary with the message and timestamp
    data_entry = {
        "timestamp": last_message_time.isoformat(),
        "message": message_data  # Store as JSON object, not a string
    }

    # Append the new entry to the list
    received_messages.append(data_entry)

    # Print the received message
    print(f"Received message: {message_data}")

    # Save the updated list to the JSON file
    save_data(received_messages)


def on_error(ws, error):
    print(f"WebSocket Error: {error}")
    print("Connection error occurred. Data flow might be stopped.")


def on_close(ws, close_status_code, close_msg):
    print(f"Connection closed with status code: {close_status_code}, Message: {close_msg}")
    print("Data storage stopped as the WebSocket connection has been closed.")


def on_open(ws):
    global last_message_time
    print("Connection opened. Data storage started.")
    last_message_time = datetime.datetime.now()

    # Start the timer to check if the machine stops sending data
    def check_for_timeout():
        while ws.keep_running:
            time_since_last_message = (datetime.datetime.now() - last_message_time).total_seconds()
            if time_since_last_message > TIMEOUT_LIMIT:
                print(f"No data received for {TIMEOUT_LIMIT} seconds. The machine may have stopped sending data.")
                ws.close()  # Close the connection if no data is received within the timeout limit
            threading.Event().wait(5)  # Check every 5 seconds

    timeout_checker = threading.Thread(target=check_for_timeout)
    timeout_checker.daemon = True
    timeout_checker.start()


if __name__ == "__main__":
    # URL of the WebSocket API
    ws_url = "ws://dev.atomssol.in:8000/machine_mqtt_data/?machine_id=AA_001"

    # Create a WebSocket application
    ws = websocket.WebSocketApp(ws_url,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    try:
        # Run the WebSocket
        ws.run_forever()
    except KeyboardInterrupt:
        print("WebSocket connection closed manually.")
