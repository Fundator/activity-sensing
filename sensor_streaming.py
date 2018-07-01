import io
import requests
import pandas as pd
import numpy as np
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.models.widgets import TextInput, Button, Dropdown
from bokeh.plotting import figure, curdoc
from bokeh.layouts import row, widgetbox
import redis

r = redis.Redis(host='localhost', port=6379, db=0)


TICKER = ""
data = ColumnDataSource(dict(time=[], value=[], sensor=[], x=[], y=[],z=[]))

i = 0

hover = HoverTool(tooltips=[
    ("Time", "@time"),
    ("Measurement", "@value")
    ])

value_plot = figure(plot_width=800,
                    plot_height=400,
                    x_axis_type='datetime',
                    tools=[hover],
                    title="Sensor streaming")

value_plot.line(source=data, x='time', y='value')
value_plot.xaxis.axis_label = "Time"
value_plot.yaxis.axis_label = "Value"
value_plot.title.text = "Sensor: "

sensormenu = [("accelerometer", "accelerometer"), ("gyroscope", "gyroscope"),("magnetic field", "magnetic field")]
sensordict = {"accelerometer":3.0, "gyroscope":4.0, "magnetic field":5.0}
sensordropdown = Dropdown(label="Sensor", menu=sensormenu, default_value="accelerometer")

menu = [("x", "x"), ("y", "y"),("z", "z")]
dropdown = Dropdown(label="Measurement", menu=menu, default_value="x")

def update_dropdown(attr, old, new):
    #dropdown.value
    #value_plot.title.text = "Sensor: " + sensordropdown.value + " Measurement: " + dropdown.value
    #df = pd.read_msgpack(r.lindex("sensor"+str(sensordict[sensordropdown.value]), -1))
    #df["value"] = df[dropdown.value]
    #df["time"] = np.arange(i,(i+len(df))*7, 7)
    #df = df.loc[df.sensor==sensordict[sensordropdown.value]]
    #data.data = df.to_dict(orient="list")
    data.data = dict(time=[], value=[], sensor=[], x=[], y=[],z=[])
    global i
    i = 0
    return

def update_sensor(attr, old, new):
    #dropdown.value
    value_plot.title.text = "Sensor: " + sensordropdown.value + " Measurement: " + dropdown.value
    #df = pd.read_msgpack(r.lindex("sensor"+str(sensordict[sensordropdown.value]), -1))
    #df["value"] = df[dropdown.value]
    #df["time"] = np.arange(i,(i+len(df))*7, 7)
    #df = df.loc[df.sensor==sensordict[sensordropdown.value]]
    #data.data = df.to_dict(orient="list") #dict(time=[],value=[])
    data.data = dict(time=[], value=[], sensor=[], x=[], y=[],z=[])
    global i 
    i = 0
    return

def update_value():
    new_values = get_last_values(measure=dropdown.value)
    #data.stream(dict(time=new_values["time"],
    #                 value=new_values["value"]), 1000)
    data.stream(new_values.to_dict(orient="list"), 10000)
    return

def get_last_values(measure):
    # endpoint = "tops/last"
    global i
    #i += 1
    #df = pd.DataFrame([[1556511+i,np.random.randint(4),
    #                      np.random.randint(100),np.random.randint(100),
    #                      np.random.randint(100)]], 
    #                    columns=["time", "sensor","value","y","z"])
    df = pd.read_msgpack(r.lindex("sensor"+str(sensordict[sensordropdown.value]), -1)) if sensordropdown.value else  pd.read_msgpack(r.lindex("sensor3.0", -1))
    #print(df.head())
    df["value"] = df[dropdown.value] if dropdown.value else df.x
    df["time"] = np.arange(7*i,(i+len(df))*7, 7)
    df.fillna(0, inplace=True)
    i += len(df)-1
    return df

#ticker_textbox = TextInput(placeholder="Sensor")
#update = Button(label="Update")
#update.on_click(update_ticker)

sensordropdown.on_change('value', update_sensor)
dropdown.on_change('value', update_dropdown)

inputs = widgetbox([sensordropdown, dropdown], width=150)

curdoc().add_root(row(inputs, value_plot, width=1600))
curdoc().title = "Sensor streaming from mobile phone"
curdoc().add_periodic_callback(update_value, 1000)