# Activity detector

Streaming sensor data from Android phone via local proxy to server in cloud, that visualize the data, and make classification requests from another server, exposing a prediction API for a Temporal Convolutional Network.  
  
<br><br>
![Imgur](https://i.imgur.com/0qe2d7I.jpg)

<br>
## The following programs must run for the application to work:
### On the mobile
Download the app "Sensorstream IMU+GPS" from Google Play. 
Change the settings to the IP-address of your proxy server. Start stream.

### On the proxy server(laptop)
- `rcv_udp_realtime.py`
Receieves the raw sensor data from the phone on UDP port 5555, convert to a more friendly format, and relays to a RabbitMQ channel.
Note: This must be on the same LAN as the phone. 

### On main server
- `receive.py` 
Listens on the RabbitMQ channel and write the streaming data to a Redis DB. 
It also writes a selected window of all the sensors that is used for prediction.
- `prep_and_predict.py`
This reads the most recent data from the Redis DB, prep it a little bit, and send to the Deep Learning API for prediction output. 

### On GPU server
- `run_keras_server.py`
Exposes the prediction API by sending the content of the request to a pretrained TCN and returning the prediction.

