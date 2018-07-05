# USAGE
# Start the server:
# 	python run_keras_server.py
# Submit a request via cURL:
# 	curl -X POST -F image=@dog.jpg 'http://localhost:5000/predict'
# Submita a request via Python:
#	python simple_request.py

# import the necessary packages
from keras.applications import ResNet50
from keras.preprocessing.image import img_to_array
from keras.applications import imagenet_utils
from keras.models import load_model
from PIL import Image
import numpy as np
import flask
import io

# initialize our Flask application and the Keras model
app = flask.Flask(__name__)
model = None

def get_model():
    # load the pre-trained Keras model (here we are using a model
    # pre-trained on ImageNet and provided by Keras, but you can
    # substitute in your own networks just as easily)
    global model
    model = load_model('squat_detector.h5') #ResNet50(weights="imagenet")

    
@app.route("/predict", methods=["POST"])
def predict():
    # initialize the data dictionary that will be returned from the
    # view
    data = {"success": False, "squat_prob":None}
    # ensure an image was properly uploaded to our endpoint
    if flask.request.method == "POST":
        if flask.request.files.get("input"):
            # read the image in PIL format
            x_b = flask.request.files["input"].read()
            x = np.frombuffer(x)
            squat_prob = model.predict(x)[0][1]
            # indicate that the request was a success
            data["squat_prob"] = squat_prob
            data["success"] = True

    # return the data dictionary as a JSON response
    return flask.jsonify(data)

# if this is the main thread of execution first load the model and
# then start the server
if __name__ == "__main__":
    print(("* Loading Keras model and Flask starting server...please wait until server has fully started"))
    get_model()
    app.run(host='0.0.0.0')