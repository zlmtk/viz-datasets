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
import argparse
import glob 
import os
import matplotlib.pyplot as plt
import matplotlib
import plotly.graph_objects as go
import json

pp = pprint.PrettyPrinter(width=41, compact=True)

color_names = [

        'red',          # Primary color, very distinct
        'blue',         # Primary color, very distinct
        'green',        # Primary color, very distinct
        'yellow',       # Secondary color, very distinct
        'cyan',         # Secondary color, very distinct
        'magenta',      # Secondary color, very distinct
        'orange',       # Intermediate color, distinct
        'purple',       # Intermediate color, distinct
        'lime',         # Bright color, distinct
        'aqua',         # Bright color, distinct
        'fuchsia',      # Bright color, distinct
        'teal',         # Dark color, distinct
        'navy',         # Dark color, distinct
        'maroon',       # Dark color, distinct
        'olive',        # Dark color, distinct
        'silver',       # Neutral color, distinct
        'gray',         # Neutral color, distinct
        'gold',         # Metallic color, distinct
        'coral',        # Warm color, distinct
        'salmon'        # Warm color, distinct
    ]


def get_color(dataset,
              color_names,
              colors_used,
              colors_args):

    dataset=str(dataset)
    if dataset in colors_args.keys() : 
        c=colors_args[dataset]
        print ('dataset %s is defined by user for the color %s' % (dataset,c))
        colors_used.add(c)
        return c 
    else : 
        for cn in color_names : 
            if cn not in colors_used : 
                print ('dataset %s is defined the color %s' % (dataset,cn))
                colors_used.add(cn)
                return cn 
    raise Exception ("No colors found")
        

def load_images (path) : 
    with Image.open(path) as img:
        print(path)
        img = img.resize((200, 200))
        output = BytesIO()
        img.save(output, format='JPEG')
        im_data = output.getvalue()
        encoded_image = base64.b64encode(im_data).decode('ascii')
        return encoded_image


def build_data (embedding_file,colors) : 

    print(embedding_file)
    df_loaded=pd.read_table(embedding_file,sep=",")
    print(df_loaded.head())

    data=[]
    print(df_loaded.columns)
    colors_used = set()

    for i, datasetname in enumerate(df_loaded['dataset'].unique()) : 
        
        sel_color = get_color(datasetname,
                             color_names,
                             colors_used,
                             colors
                             )

        df=df_loaded[df_loaded['dataset']==datasetname] 
        customData=[(i,sel_color) for i in df['image']] 
     
        data.append(go.Scatter(customdata=customData,  
                           x=df['x'],
                           y=df['y'],
                           mode='markers',
                           marker=dict(color=sel_color)))
    return data

def build_scatter_figure_layout(data) : 

    figure = {
                'data': data,
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
    return figure 

##################################################################################
#== MAIN == |
##################################################################################

if __name__ == "__main__":

    # Create the parser
    parser = argparse.ArgumentParser(description='dataviz')
    # Add arguments
    parser.add_argument('-f',
                     '--embedding-file', 
                     type=str, 
                     help='file path with the embedding in a csv format',
                     required=True)
    parser.add_argument('--colors', 
                          type=str,
                          required=False,
                          default=None,
                          help="Json list of colors example : '{\"datasetname\":\"colorname\"}'  \n %s" % color_names)
    # Parse the arguments
    args = parser.parse_args()
    print(args.colors)
    colors= json.loads(str(args.colors))
    
    ##############################################################################
    # LAYOUT
    ##############################################################################

    app=dash.Dash(__name__)
    app = dash.Dash(__name__, external_stylesheets=[], external_scripts=[])

    #Global layout 
    app.layout = html.Div([
            dbc.NavbarSimple(
        children=[
            dbc.Button("Reset", color="secondary", className="me-1",id="reset-2"),

        ],
        brand="Embedding scatter",
        brand_href="#",
        color="dark",
        dark=True,
    ),
        dcc.Graph(
            id='scatter-plot',
            figure=build_scatter_figure_layout(build_data(args.embedding_file,colors)),
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
            return build_scatter_figure_layout(build_data(args.embedding_file))

    @app.callback(
        Output('image-output', 'children'),
        [Input('scatter-plot', 'selectedData')], 
    )
    def display_selected_image(selectedData ):
        if selectedData:
            returned_images=[]
        #pp.pprint(selectedData)
            for i in selectedData['points'] : 
                try : 
                    print(i)
                    point_index =i['curveNumber']
                    cdata=i['customdata']
                    encoded_image=load_images(cdata[0])

                    #display each images
                    im_load=html.Img(src="data:image/png;base64,{}".format(encoded_image),
                                    style={"border": "2px solid "+cdata[1]})
                    returned_images.append(im_load)
                except Exception as e : 
                    print(e)
                    pass
            return returned_images
        else:
            return ''

    # Exécution de l'application Dash
    app.run_server(host='0.0.0.0',port='7777')