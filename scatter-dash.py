import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from PIL import Image 
from io import BytesIO 
import pandas as pd 
import plotly.graph_objects as go
import base64
import pprint 
pp = pprint.PrettyPrinter(width=41, compact=True)


def load_images (path) : 
    with Image.open(path) as img:
        print(path)
        img = img.resize((200, 200))
        output = BytesIO()
        img.save(output, format='JPEG')
        im_data = output.getvalue()
        encoded_image = base64.b64encode(im_data).decode('ascii')
        return encoded_image

def build_data () : 

    #Data management 
    df=pd.read_table('/data1/datasets/cvlab/fire-smoke/error-analysis/embed_laion-VIT-validset.csv',sep=',')
    
    images_path=[]
    data=[]
    data.append(go.Scatter(customdata= df['image'],
                           x=df['x'],
                           y=df['y'],
                           mode='markers',
                           marker=dict(size=10)))
    return data


##############################################################################
# MAIN Layout 
##############################################################################

app=dash.Dash(__name__)


#Global layout 
app.layout = html.Div([
        dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Accueil", href="/")),
        dbc.NavItem(dbc.NavLink("Page 1", href="/page1")),
        dbc.NavItem(dbc.NavLink("Page 2", href="/page2")),
        dbc.Button("Reset", color="secondary", className="me-1",id="reset-2"),

    ],
    brand="Mon Application",
    brand_href="#",
    color="dark",
    dark=True,
),
    dcc.Graph(
        id='scatter-plot',
        figure={
                'data': build_data(),
                'layout': go.Layout(
                    title='Scatter dataset embedding',
                    hovermode='closest',
                    clickmode='event+select',
                    showlegend=False,
                    height=600,
                    plot_bgcolor= '#111111',
                    paper_bgcolor= '#111111',
                    font= {'color': '#7FDBFF'}
              )
        },
        style={'width': '100%'}
    ),
    html.Br(),
    html.Div(id='image-output'),
])



##############################################################################
#CALLBACK 
##############################################################################


@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('reset-2', 'n_clicks')],
    [State('scatter-plot', 'selectedData')]
)
def reset_selection(selectedData,relayoutData):
        print("==============reset===================")
        return {
                'data': build_data(),
                'layout': go.Layout(
                    title='Scatter dataset embedding',
                    hovermode='closest',
                    clickmode='event+select',
                    showlegend=False,
                    height=600,
                    plot_bgcolor= '#111111',
                    paper_bgcolor= '#111111',
                    font= {'color': '#7FDBFF'}
              )
        }

@app.callback(
    Output('image-output', 'children'),
    [Input('scatter-plot', 'selectedData')]
)
def display_selected_image(selectedData):
    print(selectedData)
    if selectedData:
        returned_images=[]
       #pp.pprint(selectedData)
        for i in selectedData['points'] : 
      
          point_index =i['curveNumber']
          encoded_image=load_images(i['customdata'])

          #display each images
          im_load=html.Img(src='data:image/png;base64,{}'.format(encoded_image))
          returned_images.append(im_load)
          
          #returned_images.append(html.Img(src='data:image/png;base64,{}'.format(encoded_images[point_index])))
        return returned_images
    else:
        return ''


# Exécution de l'application Dash
app.run_server(host='0.0.0.0',port='9191')