import pika
import pandas as pd
import redis

# Initialize Redis DB and RabbitMQ connection.
r = redis.Redis(host='localhost', port=6379, db=0)
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='hello')

activity_length = 45

def callback(ch, method, properties, body):
    # Read msgpack as DataFrame.
    df = pd.read_msgpack(body)    
    for n, g in df.groupby("sensor"):
        # Set sensor store with last received DataFrame
        sensor = 'sensor'+str(n)
        r.set(sensor,g.to_msgpack())
        # If sensor store for ml exists
        if r.get(sensor+'_ml') is not None:
            # Append new measurements to old
            old = pd.read_msgpack(r.get(sensor+'_ml'))
            new = old.append(g, ignore_index=True)
            # Chop of only last if longer than activity_length
            if len(new)>activity_length:
                new = new.iloc[-activity_length:]
            # Set new values for sensor store ml
            r.set(sensor+'_ml',new.to_msgpack())
        else:
            r.set(sensor+'_ml',g.to_msgpack())

channel.basic_consume(callback,
                      queue='hello',
                      no_ack=True)

try:
    print(' [*] Receiving messages. To exit press CTRL+C')
    channel.start_consuming()
except KeyboardInterrupt:
    # Graceful shutdown.
    connection.close()