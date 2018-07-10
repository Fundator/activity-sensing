import io
import requests
import pandas as pd
import numpy as np
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.models.widgets import TextInput, Button, Dropdown, Select, PreText, Div
from bokeh.plotting import figure, curdoc
from bokeh.layouts import row, widgetbox
import redis

r = redis.Redis(host='localhost', port=6379, db=0)


i = 0
squat_prob = 0.
squat_count = 0
update_freq = 50 # ms

hover = HoverTool(tooltips=[
    ("Time", "@time"),
    ("Measurement", "@value")
    ])

sensors = ["accelerometer","gyroscope","magnetic field"]
measures = ["x", "y", "z"]
datadict = {s+"_"+m : {"data": ColumnDataSource(dict(time=[], value=[], sensor=[], x=[], y=[],z=[]))} for s in sensors for m in measures if (s!="magnetic field" or m!="z")}

for key in datadict.keys():
    sensor, measure = key.split("_")[0], key.split("_")[-1]
    value_plot = figure(plot_width=400,
                        plot_height=200, #x_axis_type='datetime',
                        tools=[hover],
                        title=sensor+" - "+measure)
    value_plot.line(source=datadict[key]["data"], x='time', y='value')
    value_plot.xaxis.axis_label = "Time [ms]"
    value_plot.yaxis.axis_label = "Value"
    datadict[key]["plot"] = value_plot

#sensormenu = [("accelerometer", "accelerometer"), ("gyroscope", "gyroscope"),("magnetic field", "magnetic field")]
sensordict = {"accelerometer":3, "gyroscope":4, "magnetic field":5}
squat_text = Div(text='Squat probability:', width=500, height=200)

button = Button(label="Reset stream", button_type="default")

#sensordropdown = Dropdown(label="Sensor", menu=sensormenu, default_value="accelerometer")

#menu = [("x", "x"), ("y", "y"),("z", "z")]
#dropdown = Dropdown(label="Measurement", menu=menu, default_value="x")

#sensordropdown = Select(title="Sensor", options=["accelerometer","gyroscope","magnetic field"], value="accelerometer")
#dropdown = Select(title="Sensor", options=["x","y","z"], value="x")


#value_plot.title.text = "Squat probability: " + "{0:.2f}".format(float(squat_prob)*100) + "    Squat count: " + str(squat_count) 
#value_plot.title.text_font_size = "18pt"

def update_dropdown(attr, old, new):
    data.data = dict(time=[], value=[], sensor=[], x=[], y=[],z=[])
    global i
    i = 0
    return

def reset():
    global i, squat_count, squat_prob
    i = 0
    squat_count = 0 
    squat_prob = 0.
    return

def update_value():
    global i, squat_prob, squat_count

    for key in datadict.keys():
        new_values = get_last_values(sensor=key.split("_")[0], measure=key.split("_")[-1])
        datadict[key]["data"].stream(new_values.to_dict(orient="list"), 100)
    
    # Update squat prob
    new_squat_prob = r.get("squat_prob")
    if not new_squat_prob == squat_prob:
        squat_prob = new_squat_prob
        if float(squat_prob)>0.5:
            squat_count += 1
    try:
         
        squat_text.text = "<p style='text-align:center'><font size='7'> Squat count: <br> {1} </font><br><font size='4'>Squat probability: <br> {0:.2f}%</font></p>".format(float(squat_prob)*100, squat_count)
    except Exception as e:
        print(e)
    return

def get_last_values(sensor, measure):
    global i
    df = pd.read_msgpack(r.get("sensor"+str(sensordict[sensor])))
    df["value"] = df[measure] 
    df["time"] = np.arange(update_freq*i,(i+len(df))*update_freq, update_freq)
    df.fillna(0, inplace=True)
    i += len(df)
    return df

#sensordropdown.on_change('value', update_dropdown)
button.on_click(reset)

#controls = [dropdown, sensordropdown]
#for control in controls:
#    control.on_change('value', lambda attr, old, new: update())


#inputs = widgetbox([sensordropdown, dropdown], width=150)
plots = [datadict[key]["plot"] for key in datadict.keys()]
curdoc().add_root(row(widgetbox([squat_text,button], sizing_mode='stretch_both'), width=800))
curdoc().add_root(row(plots[:3], width=1600))
curdoc().add_root(row(plots[3:6], width=1600))
curdoc().add_root(row(plots[6:], width=1600))
curdoc().title = "Sensor streaming from mobile phone"
curdoc().add_periodic_callback(update_value, update_freq)