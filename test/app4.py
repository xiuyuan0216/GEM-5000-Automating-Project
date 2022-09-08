import tkinter
from dash import Dash, html, dcc, Input, Output

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
    html.Div(id="path_box", style={'height':'1000px','width':"100%"})
])


if __name__ == "__main__":
    app.run_server(debug=True)