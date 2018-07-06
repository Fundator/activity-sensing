import socket
import numpy as np
import pandas as pd
import time
import pika
import json

credentials = pika.PlainCredentials('thomas', 'Test2011')
parameters = pika.ConnectionParameters(credentials=credentials, host='40.127.197.251')
connection = pika.BlockingConnection(parameters)

channel = connection.channel()
channel.queue_declare(queue='hello')

UDP_IP = "192.168.1.14"
UDP_PORT = 5555
CHUNKSIZE=1500
sock = socket.socket(socket.AF_INET, # Internet
                    socket.SOCK_DGRAM) # UDP

sock.bind((UDP_IP, UDP_PORT))

def divide_chunks(l, n):    
    # looping til length l
    for i in range(0, len(l), n):
        yield l[i:i + n] #How many elements each list should have

def chunk_to_df(buffer):
    received = "".join(buffer).split(",")[1:]
    chunks = list(divide_chunks(received, 4))
    measurements = np.vstack(chunks)
    df = pd.DataFrame(measurements, columns=["sensor", "x", "y", "z"])
    return df

def prep_df(df, msgpack=True):
    for c in df.columns:
        if c=="sensor":
            df[c] = pd.to_numeric(df[c], errors="coerce", downcast="unsigned")
        else:
            df[c] = pd.to_numeric(df[c], errors="coerce", downcast="float")
    if df.shape[0]>CHUNKSIZE:
        df = df.iloc[:CHUNKSIZE]
    if msgpack:
        df = df.to_msgpack()
        return df 
    else:
        return df

print("Receiving stream...")
while True:
    try:
        data, addr = sock.recvfrom(512) 
        df = chunk_to_df(data.decode("UTF-8"))
        chunk = prep_df(df, True)
        channel.basic_publish(exchange='', routing_key='hello', body=chunk) 
    except Exception as e:
        print(e)
        print("Closing connection.")
        sock.close()
        connection.close()
        connection = pika.BlockingConnection(parameters)
        sock = socket.socket(socket.AF_INET, # Internet
                    socket.SOCK_DGRAM) # UDP
        sock.bind((UDP_IP, UDP_PORT))
        channel = connection.channel()
        channel.queue_declare(queue='hello')
        print("Stream reset")
        continue