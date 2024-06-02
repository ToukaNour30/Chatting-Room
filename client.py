import threading
import socket
import os
import pyaudio
import wave
import mysql.connector
import datetime

# Establishing MySQL database connection
db_connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="TXKouT_34",
    database="networks"
)

db_cursor = db_connection.cursor()

alias = input('Choose an alias >>> ')
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Function to connect to the server
def connect_to_server():
    try:
        client.connect(('127.0.0.1', 57700))
        client.send(alias.encode('utf-8'))
        log_client_activity("Connected to the server")
    except Exception as e:
        print(f"Error connecting to the server: {e}")
        os._exit(1)

# Function to receive messages from the server
def client_receive():

    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == 'NICKNAME?':
                client.send(alias.encode('utf-8'))
            else:
                print(message)
        except Exception as e:
            print(f"Error receiving message: {e}")
            client.close()
            log_client_activity("Disconnected from the server")
            os._exit(1)

# Function to send messages to the server
def send_message(message_type, data):
    try:
        client.send(message_type.encode('utf-8'))
        client.send(data)
    except Exception as e:
        print(f"Error sending message: {e}")
        client.close()
        log_client_activity("Disconnected from the server")
        os._exit(1)

# Function to send text messages to the server
def send_text():
    try:
        message = f'{alias}: {input("")}'
        if message.strip():  # Check if the message is not empty
            send_message("TEXT", message.encode('utf-8'))
    except Exception as e:
        print(f"Error sending message: {e}")

# Function to send files, images, or videos to the server
def send_data(data_type):
    try:
        file_path = input(f"Enter the path of the {data_type.lower()}: ").strip()
        if os.path.isfile(file_path):
            filesize = os.path.getsize(file_path)
            with open(file_path, "rb") as f:
                data = f.read()
                client.send(data_type.encode('utf-8'))
                client.send(os.path.basename(file_path).encode('utf-8'))
                client.send(str(filesize).encode('utf-8'))
                client.send(data)
        else:
            print(f"{data_type} does not exist. Please try again.")
    except Exception as e:
        print(f"Error sending {data_type}: {e}")

# Function to stop recording
def stop_recording_func():
    input("Press Enter to stop recording...")
    print("Recording stopped.")

# Function to record audio
def record_audio(filename, duration=60):
    chunk = 1024#holding 1024 frame per buffer
    sample_format = pyaudio.paInt16#paInt16 for high quality sound
    channels = 2
    fs = 44100#number of frames captured per second
    p = pyaudio.PyAudio()

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = []

    stop_thread = threading.Thread(target=stop_recording_func)
    stop_thread.start()

    for _ in range(0, int(fs / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))

    return filename

# Function to send audio
def send_audio(audiopath):
    try:
        if os.path.isfile(audiopath):
            record_audio(audiopath)
            send_data("AUDIO")
        else:
            print("Audio file does not exist. Please try again.")
    except Exception as e:
        print(f"Error sending audio: {e}")

# Function to log client activity
def log_client_activity(activity):
    try:
        entry_time = datetime.datetime.now()
        exit_time = entry_time
        duration = 0
        insert_query = "INSERT INTO client_activity (client_name, entry_time, exit_time, duration) VALUES (%s, %s, %s, %s)"
        db_cursor.execute(insert_query, (alias, entry_time, exit_time, duration))
        db_connection.commit()
    except Exception as e:
        print(f"Error logging client activity: {e}")

# Creating thread for receiving messages
connect_to_server()

# Start the message receiving thread
receive_thread = threading.Thread(target=client_receive)
receive_thread.start()

#  loop to send different types of messages
while True:
    try:
        print("Choose an option:\n1. Send Text\n2. Send File\n3. Send Image\n4. Record and Send Audio\n5. Send Video")
        choice = input(">>> ")
        if choice == "1":
            send_text()
        elif choice == "2":
            send_data("FILE")
        elif choice == "3":
            send_data("IMAGE")
        elif choice == "4":
            send_audio("recorded_audio.wav")
        elif choice == "5":
            send_data("VIDEO")
        else:
            print("Invalid choice. Please choose again.")
    except KeyboardInterrupt:
        print("\nGoodbye!")
        client.close()
        log_client_activity("Disconnected from the server")
        os._exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")

