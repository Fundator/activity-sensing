import pandas as pd
import redis
import numpy as np
from sklearn.preprocessing import StandardScaler
import pickle
import requests
import json
import time

KERAS_REST_API_URL = "http://40.113.111.0:5000/predict"
r = redis.Redis(host='localhost', port=6379, db=0)
sensordict = {3:"acc_", 4:"gyro_", 5:"mag_"}
sc = pickle.load(open("data/sc_3.pkl", "rb"))

def get_df():
    try:
        dfs = []
        for n in [3,4,5]:
            df = pd.read_msgpack(r.get("sensor"+str(n)+"_ml"))
            dfs.append(df.iloc[:,1:])
        mldf = pd.concat(dfs, axis=1, ignore_index=True)
        mldf.columns = [sensordict[n]+m for n in [3,4,5] for m in ["x", "y","z"]]
        mldf.drop("mag_z", axis=1, inplace=True)
        df = pd.DataFrame(sc.transform(mldf.values))
    except Exception as e:
        print(e)
        df = pd.DataFrame([])
    return df

while True:
    start = time.time()
    x = get_df()
    if x.shape[0]==0:
        continue
    payload = {"input": x.to_msgpack()}
    # submit the request
    resp = requests.post(KERAS_REST_API_URL, files=payload).json()
    print("got response in "+str(time.time()-start))
    print(resp)
    # ensure the request was sucessful
    if resp["success"]:
        #print(resp["squat_prob"])
        r.set("squat_prob", resp["squat_prob"])
    # otherwise, the request failed
    else:
        print("Request failed")
    time.sleep(2.5)