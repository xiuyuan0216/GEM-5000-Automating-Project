from sre_parse import State
import tkinter
from dash import Dash, html, dcc, Input, Output, callback, State

from Main_parse import *
from Select_copyIL import *
from Sensor_parse import *
from Main_parse import *
from Event_log_parse import *
from CMC_Debris_check import *
from Delamination_check import *
from Error_code_extract import *
from Error_message_extract import *
from Error_reason_extract import *
from IQM_check import *
from Leak_check import *
from Peroxide_Exposure_check import *
from PSC_C_check import *
from Solenoid_and_bubbles_check import *

app = Dash(__name__)

app.layout = html.Div(style={"background-image":'url("/assets/Background.PNG")',
                             "background-size":'100% 1000px',
                             "background-repeat":"no-repeat"},children=[
    html.Div(style={"height":"20px",
                    "width":"100%",
                    "background-color":'#00008b',
                    "position":'fixed',
                    "top":'0',
                    'left':'0'}),
    html.Div(children="werfen", style={
                    "height":"80px",
                    "width":"100%",
                    "padding-top":'45px',
                    "padding-left":'80px',
                    'font-size':'70px',
                    'font-weight':'bold',
                    "color":'#00008b',
                    'font-family':'sans-serif'
    }),
    html.Hr(style={'border-color':'#FFA500',
                   'border-width':'1px'}),
    html.Div("Paste CopyIL folder path here:", style={'color':'#00008b',
                                                    'height':'30px',
                                                    'padding-top':'10px',
                                                    'padding-left':'10px',
                                                    "font-size":'x-large'}),
    html.Div(style={'padding-left':'10px'},children=[dcc.Input(id="input_box", type='text', style={'height':'100px',
                                                  "width":'50%',
                                                  'border-size':'1px',
                                                  'border-color':'#202124',
                                                  "border-radius":'10px',
                                                  'margin-top':'5px',
                                                  'font-size':'20px',
                                                  "padding-top":'10px',
                                                  'text-align':'left',
                                                  }, placeholder="CopyIL Path")]),
    html.Div(children=[html.Button('Submit', id='submit_button',n_clicks=0, style={"height":"50px", "width":"120px", "background-color":"#FFA500", "color":'#FFFFFF', "border-radius":"10px", "font-size":'20px'})], style={"height":"100px", "padding-top":'30px', 'padding-left':'300px'}),
    html.Div(id="path_box", style={'height':'100px','width':"50%", 'font-size':'20px', 'border':'2px solid black',"border-radius":'10px', 'padding-left':'10px', "background":"0#FFFFFF"}),
    html.Hr(style={'border-color':'#FFA500',
                   'border-width':'1px'}),
    html.Div(id='report', style={'height':"1000px",'width':"100%", 'background':'0#FFFFFF', "border":"2px solid black", 'border-radius':'10px'})
])


@app.callback(
    Output('path_box', 'children'),
    Input('submit_button','n_clicks'),
    State('input_box', 'value')
)
def update_output(n_clicks, value):
    if n_clicks>0:
        print(value)
        Main_parse(value)
        sensor_path, event_log_path, cartridge = Main_parse(value)
        sensor_file, SerialNo = Sensor_parse(sensor_path)
        event_log_relavant = Event_log_parse(event_log_path, SerialNo)
        error_code = Error_code_extract(event_log_relavant)
        message = Error_message_extract(error_code)
        reason = Error_reason_extract(error_code)
        print(error_code)

        return f"The folder you selected: \n {value}"
    else:
        return ""


if __name__ == "__main__":
    app.run_server(debug=True)