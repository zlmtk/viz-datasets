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


def build_data (embedding_file) : 

    print(embedding_file)
    df_loaded=pd.read_table(embedding_file,sep=",")
    print(df_loaded.head())

    data=[]
    color_tab=['Aqua','Teal','Coral','Fuchsia']
    print(df_loaded.columns)
    for datasetname in df_loaded['dataset'].unique() : 

        df=df_loaded[df_loaded['dataset']==datasetname] 
        sel_color=color_tab.pop()
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
    # Parse the arguments
    args = parser.parse_args()
    
    ##############################################################################
    # LAYOUT
    ##############################################################################

    app=dash.Dash(__name__)

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
            figure=build_scatter_figure_layout(build_data(args.embedding_file)),
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