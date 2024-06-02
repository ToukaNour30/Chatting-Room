import threading
import socket
import os
import mysql.connector

# MySQL database configuration
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'TXKouT_34',
    'database': 'networks'
}

# Establish MySQL database connection
db_connection = mysql.connector.connect(**db_config)
db_cursor = db_connection.cursor()

# Create tables to store different types of data
create_text_table_query = """
CREATE TABLE IF NOT EXISTS text_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message TEXT
)
"""
db_cursor.execute(create_text_table_query)

create_files_table_query = """
CREATE TABLE IF NOT EXISTS files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255),
    filesize BIGINT,
    file_type VARCHAR(50)
)
"""
db_cursor.execute(create_files_table_query)

create_images_table_query = """
CREATE TABLE IF NOT EXISTS images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255),
    filesize BIGINT
)
"""
db_cursor.execute(create_images_table_query)

create_audio_table_query = """
CREATE TABLE IF NOT EXISTS audio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255),
    filesize BIGINT
)
"""
db_cursor.execute(create_audio_table_query)

create_video_table_query = """
CREATE TABLE IF NOT EXISTS video (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255),
    filesize BIGINT
)
"""
db_cursor.execute(create_video_table_query)


create_client_activity_table_query = """
CREATE TABLE IF NOT EXISTS client_activity (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_name VARCHAR(255),
    entry_time DATETIME,
    exit_time DATETIME,
    duration INT  -- Duration in seconds
)
"""
db_cursor.execute(create_client_activity_table_query)


host = '127.0.0.1'
port = 57700

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []

def handle_client(client):
    entry_time = datetime.datetime.now()
    client_name = client.recv(1024).decode('utf-8')  # Assuming the client sends its name first

    try:
        while True:
            message_type = client.recv(1024).decode('utf-8')
            if not message_type:
                break
            if message_type == "TEXT":
                message = client.recv(1024).decode('utf-8')
                # Store text message in the database
                insert_query = "INSERT INTO text_messages (message) VALUES (%s)"
                db_cursor.execute(insert_query, (message,))
                db_connection.commit()
            elif message_type in ["FILE", "IMAGE", "AUDIO", "VIDEO"]:
                filename = client.recv(1024).decode('utf-8')
                filesize = int(client.recv(1024).decode('utf-8'))
                data = b""
                while len(data) < filesize:
                    packet = client.recv(1024)
                    if not packet:
                        break
                    data += packet
                with open(filename, 'wb') as f:
                    f.write(data)
                if message_type == "FILE":
                    insert_query = "INSERT INTO files (filename, filesize, file_type) VALUES (%s, %s, %s)"
                    db_cursor.execute(insert_query, (filename, filesize, message_type))
                elif message_type == "IMAGE":
                    insert_query = "INSERT INTO images (filename, filesize) VALUES (%s, %s)"
                    db_cursor.execute(insert_query, (filename, filesize))
                elif message_type == "AUDIO":
                    insert_query = "INSERT INTO audio (filename, filesize) VALUES (%s, %s)"
                    db_cursor.execute(insert_query, (filename, filesize))
                elif message_type == "VIDEO":
                    insert_query = "INSERT INTO video (filename, filesize) VALUES (%s, %s)"
                    db_cursor.execute(insert_query, (filename, filesize))
                db_connection.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        exit_time = datetime.datetime.now()
        duration = (exit_time - entry_time).seconds
        log_client_activity(client_name, entry_time, exit_time, duration)
        index = clients.index(client)
        clients.remove(client)
        client.close()

def log_client_activity(activity):
    try:
        entry_time = datetime.datetime.now()
        exit_time = entry_time  # Assuming exit time is the same as entry time for now
        duration = (exit_time - entry_time).total_seconds()  # Calculate duration in seconds
        insert_query = "INSERT INTO client_activity (client_name, entry_time, exit_time, duration) VALUES (%s, %s, %s, %s)"
        db_cursor.execute(insert_query, (alias, entry_time, exit_time, duration))
        db_connection.commit()
    except Exception as e:
        print(f"Error logging client activity: {e}")
def receive():
    while True:
        print('Server is running and listening...')
        client, address = server.accept()
        print(f'Connection established with {str(address)}')

        clients.append(client)

        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

if __name__ == "__main__":
    receive()
if __name__ == "__main__":
    receive()