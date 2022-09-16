
import tkinter
from dash import Dash, html, dcc, Input, Output, callback, State, dash_table
from plotly.tools import mpl_to_plotly
import io
import base64

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
                                                    "font-size":'x-large',
                                                    "font-family":"Arial"}),
    html.Div(style={'padding-left':'10px'},children=[dcc.Input(id="input_box", type='text', style={'height':'100px',
                                                  "width":'50%',
                                                  'border-size':'1px',
                                                  'border-color':'#202124',
                                                  "border-radius":'10px',
                                                  'margin-top':'5px',
                                                  'font-size':'20px',
                                                  "padding-top":'10px',
                                                  'text-align':'left',
                                                  "font-family":"Arial"
                                                  }, placeholder="CopyIL Path")]),
    html.Div(children=[html.Button('Submit', id='submit_button',n_clicks=0, style={"height":"50px", "width":"120px", "background-color":"#FFA500", "color":'#FFFFFF', "border-radius":"10px", "font-size":'20px'})], style={"height":"100px", "padding-top":'30px', 'padding-left':'300px'}),
    html.Div(id="path_box", style={'height':'100px','width':"50%", 'font-size':'20px', 'border':'2px solid black',"border-radius":'10px', 'padding-left':'10px', "background":"0#FFFFFF", 'font-family':'Arial'}),
    html.Hr(style={'border-color':'#FFA500',
                   'border-width':'1px'}),
    html.Div(id='report', style={'height':"2000px",'width':"100%", 'background':'0#FFFFFF', "border":"2px solid black", 'border-radius':'10px'}, children=[
        html.Div(children="Report for your selected CopyIL", style={'height':'30px','width':'100%', 'font-size':'30px','text-align':'center', 'font-family':'Arial'}),
        html.Hr(),
        html.Div(id='error_part', children=[
            html.Div(id="error_code", style={"padding-left":'10px', "font-family":"Arial"}),
            html.Div(id='error_message', style={"padding-left":'10px', "font-family":"Arial"}),
            html.Div(id='error_reason', style={"padding-left":"10px", "font-family":"Arial"})
        ]),
        html.Hr(id='line1'),
        html.Div(id='IQM', children=[
            html.Img(id='IQM_graph'),
            html.Div(id='IQM_words', style={"padding-left":'10px', "font-family":"Arial"})
        ]),
        html.Hr(id="line2"),
        html.Div(id='leak', children=[
            html.Div(id="leak_detected", style={"font-family":"Arial", "padding-left":'10px'}),
            html.Div(id="outlier_points", style={"font-family":"Arial", "padding-left":'10px'})
        ]),
        html.Hr(id='line3'),
        html.Div(id='peroxide', style={"font-family":"Arial", "padding-left":"10px"}),
        html.Hr(id='line4'),
        html.Div(id="solenoid_bubble", children=[
            dash_table.DataTable(id="solenoid_and_bubble",style_cell={"font-family":"Arial"})
        ]),
        html.Hr(id="line5"),
        html.Div(id='PSC-C', style={"padding-left":"10px", "font-family":"Arial"}),
        html.Hr(id="line6"),
        html.Div(id="Delamination", style={"padding-left":"10px", "font-family":"Arial"}),
        html.Hr(id="line7"),
        html.Div(id="CMC_debris", style={"padding-left":"10px", "font-family":"Arial"}),
        html.Hr(id='line8')
    ])
])


@app.callback(
    Output('path_box', 'children'),
    Output('error_code','children'),
    Output('error_message','children'),
    Output('error_reason','children'),
    Output('line1','style'),
    Output('IQM_graph','src'),
    Output('IQM_graph','style'),
    Output('IQM_words','children'),
    Output('line2', 'style'),
    Output('leak_detected', 'children'),
    Output('outlier_points', 'children'),
    Output('line3', 'style'),
    Output('peroxide', 'children'),
    Output('line4', 'style'),
    Output('solenoid_and_bubble', 'data'),
    Output('line5', 'style'),
    Output("PSC-C", 'children'),
    Output("line6", "style"),
    Output("Delamination", "children"),
    Output("line7", "style"),
    Output("CMC_debris", "children"),
    Output("line8", "style"),
    Input('submit_button','n_clicks'),
    State('input_box', 'value')
)
def update_output(n_clicks, value):
    if n_clicks>0:
        Main_parse(value)
        sensor_path, event_log_path, cartridge = Main_parse(value)
        sensor_file, SerialNo = Sensor_parse(sensor_path)
        event_log_relavant = Event_log_parse(event_log_path, SerialNo)
        error_code = Error_code_extract(event_log_relavant)
        message = Error_message_extract(error_code)
        reason = Error_reason_extract(error_code)
        fig, columns, information = IQM_check(sensor_file, event_log_relavant, SerialNo)
        leak, sensor_leak_failures = Leak_check(sensor_file)
        peroxide = Peroxide_Exposure_check(sensor_file)
        solenoid_and_bubbles_dict = pd.DataFrame(Solenoid_and_bubbles_check(sensor_file)).to_dict('records')
        PSC_information = PSC_C_check(sensor_file)
        delamination = Delamination_check(sensor_file, cartridge)
        CMC_debris = CMC_Debris_check(sensor_file)

        leak_detected = "Leak dectection on sensors: "+leak
        outlier_points = "Total number of outlier points in leak check: "+str(sensor_leak_failures)
        peroxide_failure = "Peroxide exposure check on sensors: "+peroxide

        if columns == 0:
            return f"The folder you selected: \n {value}", f"Error code: {error_code}", f"Error message: {message}", \
                f"Error reason: {reason}",{"border-top":'1px', "border-color":'black'}, None, None, fig,\
                {"border-top":'1px', "border-color":'black'}, leak_detected, outlier_points,\
                {"border-top":'1px', "border-color":'black'}, peroxide_failure, {"border-top":'1px', "border-color":'black'}, solenoid_and_bubbles_dict,\
                {"border-top":'1px', "border-color":'black'}, PSC_information, {"border-top":'1px', "border-color":'black'}, \
                "Delamination detection: "+delamination, {"border-top":'1px', "border-color":'black'}, "CMC Debris detection: "+CMC_debris, \
                {"border-top":'1px', "border-color":'black'}
        else:
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            data = base64.b64encode(buf.getbuffer()).decode('utf-8')
            fig_height = str(200*columns)+'px'
            IQM = []
            for i in information:
                IQM1="Sensor "+i['Sensor']+" Failed at Calibration Type "+i['Calibration Type']
                line_break1 = html.Br()
                IQM2="Sensor Disabled time:"+i['Disabled time']
                line_break2 = html.Br()
                IQM3="Sensor Disabled age:"+i['Disabled age']+'hrs'
                line_break3 = html.Br()
                IQM4="Sensor data maximum value "+str(i['max'])
                line_break4 = html.Br()
                IQM5="Sensor data minimum value "+str(i['min'])
                line_break5 = html.Br()
                IQM6="-------------------------------"
                line_break6 = html.Br()
                IQM.append(IQM1)
                IQM.append(line_break1)
                IQM.append(IQM2)
                IQM.append(line_break2)
                IQM.append(IQM3)
                IQM.append(line_break3)
                IQM.append(IQM4)
                IQM.append(line_break4)
                IQM.append(IQM5)
                IQM.append(line_break5)
                IQM.append(IQM6)
                IQM.append(line_break6)
            IQM_P = html.P(IQM)
            return f"The folder you selected: \n {value}", f"Error code: {error_code}", f"Error message: {message}", \
                f"Error reason: {reason}",{"border-top":'1px', "border-color":'black'}, "data:image/png;base64,{}".format(data),\
                {"height":fig_height, "width":'100%'}, IQM_P, {"border-top":'1px', "border-color":'black'}, leak_detected, outlier_points,\
                {"border-top":'1px', "border-color":'black'}, peroxide_failure, {"border-top":'1px', "border-color":'black'}, solenoid_and_bubbles_dict, \
                {"border-top":'1px', "border-color":'black'}, "PSC-C detection: "+PSC_information, {"border-top":'1px', "border-color":'black'},\
                "Delamination detection: "+delamination, {"border-top":'1px', "border-color":'black'}, "CMC Debris detection: "+CMC_debris, \
                {"border-top":'1px', "border-color":'black'}
    else:
        return "","","","",{'border-top':'1px', 'border-color':'transparent'}, None, None, None,{'border-top':'1px', 'border-color':'transparent'},\
            "","", {"border-top":'1px', "border-color":'transparent'}, "", {"border-top":'1px', "border-color":'transparent'}, None, \
            {"border-top":'1px', "border-color":'transparent'}, "", {"border-top":'1px', "border-color":'transparent'}, "",\
            {"border-top":'1px', "border-color":'transparent'}, "", {"border-top":'1px', "border-color":'transparent'}


if __name__ == "__main__":
    app.run_server(debug=True)