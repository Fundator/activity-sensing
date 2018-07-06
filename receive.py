import pika
import pandas as pd
import redis
from collections import defaultdict
r = redis.Redis(host='localhost', port=6379, db=0)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()


channel.queue_declare(queue='hello')

received = defaultdict(bool)
first = True
min_len = 1e9
dfs = []

def callback(ch, method, properties, body):
    #print(" [x] Received msg")
    df = pd.read_msgpack(body)
    num_rows = []
    for n, g in df.groupby("sensor"):
        sensor = 'sensor'+str(n)
        r.set(sensor,g.to_msgpack())
        if r.get(sensor+'_ml') is not None:
            old = pd.read_msgpack(r.get(sensor+'_ml'))
            new = old.append(g, ignore_index=True)
            #print(new.shape)
            if len(new)>45:
                new = new.iloc[-45:]
            r.set(sensor+'_ml',new.to_msgpack())
        else:
            r.set(sensor+'_ml',g.to_msgpack())

channel.basic_consume(callback,
                      queue='hello',
                      no_ack=True)

try:
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
except KeyboardInterrupt:
    connection.close()