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

data = ColumnDataSource(dict(time=[], value=[], sensor=[], x=[], y=[],z=[]))

i = 0
update_freq = 100 # ms

hover = HoverTool(tooltips=[
    ("Time", "@time"),
    ("Measurement", "@value")
    ])

value_plot = figure(plot_width=800,
                    plot_height=400, #x_axis_type='datetime',
                    tools=[hover],
                    title="Sensor streaming")

value_plot.line(source=data, x='time', y='value')
value_plot.xaxis.axis_label = "Time [ms]"
value_plot.yaxis.axis_label = "Value"
value_plot.title.text = "Sensor: "

sensormenu = [("accelerometer", "accelerometer"), ("gyroscope", "gyroscope"),("magnetic field", "magnetic field")]
sensordict = {"accelerometer":3, "gyroscope":4, "magnetic field":5}
sensordropdown = Dropdown(label="Sensor", menu=sensormenu, default_value="accelerometer")

menu = [("x", "x"), ("y", "y"),("z", "z")]
dropdown = Dropdown(label="Measurement", menu=menu, default_value="x")

def update_dropdown(attr, old, new):
    data.data = dict(time=[], value=[], sensor=[], x=[], y=[],z=[])
    global i
    i = 0
    return

def update_sensor(attr, old, new):
    value_plot.title.text = "Sensor: " + sensordropdown.value + " Measurement: " + dropdown.value
    data.data = dict(time=[], value=[], sensor=[], x=[], y=[],z=[])
    global i 
    i = 0
    return

def update_value():
    new_values = get_last_values(measure=dropdown.value)
    data.stream(new_values.to_dict(orient="list"), 100)
    return

def get_last_values(measure):
    global i
    df = pd.read_msgpack(r.get("sensor"+str(sensordict[sensordropdown.value]))) if sensordropdown.value else  pd.read_msgpack(r.get("sensor3"))
    df["value"] = df[dropdown.value] if dropdown.value else df.x
    df["time"] = np.arange(update_freq*i,(i+len(df))*update_freq, update_freq)
    df.fillna(0, inplace=True)
    i += len(df)
    return df

sensordropdown.on_change('value', update_dropdown)
dropdown.on_change('value', update_dropdown)

inputs = widgetbox([sensordropdown, dropdown], width=150)

curdoc().add_root(row(inputs, value_plot, width=1600))
curdoc().title = "Sensor streaming from mobile phone"
curdoc().add_periodic_callback(update_value, update_freq)