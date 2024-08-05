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
import plotly.graph_objects as go
import json

pp = pprint.PrettyPrinter(width=41, compact=True)

updated_object=None
colors_used={}
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
    if dataset in colors_used.keys() : 
        return colors_used[dataset]

    if dataset in colors_args.keys() : 
        c=colors_args[dataset]
        print ('dataset %s is defined by user for the color %s' % (dataset,c))
        colors_used[dataset]=c
        return c 
    else : 
        for cn in color_names : 
            if cn not in colors_used.values() : 
                print ('dataset %s is defined the color %s' % (dataset,cn))
                colors_used[dataset]=cn
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

def create_dropdown_menu(items):

    menu_items = [
        dbc.DropdownMenuItem(
            [
                html.Div(style={'background-color': item['color'], 'width': '10px', 'height': '10px', 'display': 'inline-block', 'margin-right': '10px'}),
                html.Span(item['label'])
            ],
            href="#"
        )
        for item in items
    ]
    return dbc.DropdownMenu(children=menu_items, nav=True, in_navbar=True, label="datasets")

def get_dropdown_menu_items():
    items=[]
    for k,v in colors_used.items() : 
        items.append({"label":k,"color":v})
    return items


def build_modal () : 

    print("crate modal structure")
    modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Images urls")),
        dbc.ModalBody(
            dcc.Textarea(
                id="textarea",
                value="",
                style={"width": "100%", "height": "100%"},
                readOnly=True
            )
        ),
    ],
    id="modal",
    is_open=False,
    style={"width": "600px", "height": "400px"},
    )
    return modal 

def build_python_list (selectedData) :
    
     str_r="selected_images=["
     for i in selectedData['points'] : 
        str_r+="'"+i['customdata'][0]+"',\n"
     str_r=str_r[:-2]
     str_r+="]\n"
     return str_r


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
    colors= json.loads(str(args.colors)) if args.colors is not None else {}
    
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
            html.Div(id='dropdown-menu'),
            dbc.Button("Selected images", color="secondary", className="me-1", id="sel-img", n_clicks=0),
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
        build_modal(),
        html.Br(),
        html.Div(id='image-output'),
       
    ])

    ##############################################################################
    #CALLBACK 
    ##############################################################################

    # Callbacks model window 
    @app.callback(
        Output("modal", "is_open"),
        [Input("sel-img", "n_clicks")],
        [State("modal", "is_open")],
    )
    def toggle_modal(n1, is_open):
        if n1 :
            return not is_open
        return is_open

    @app.callback(
    Output('textarea', 'value'),
    [Input('scatter-plot', 'selectedData')],
    )   
    def update_textarea(selectedData):
        
        if selectedData is not None :   
            return  build_python_list(selectedData)
        return ""


    @app.callback(
    Output('dropdown-menu', 'children'),
    [Input('scatter-plot', 'figure')]  
    )
    def update_dropdown_menu(figure):
        global updated_object 
        if updated_object is None : 
            return create_dropdown_menu(get_dropdown_menu_items()) 
        return None 

    @app.callback(
        Output('scatter-plot', 'figure'),
        [Input('reset-2', 'n_clicks')],
        [State('scatter-plot', 'selectedData')]
    )
    def reset_selection(selectedData,relayoutData):
            
            print("==============reset===================")
            return build_scatter_figure_layout(build_data(args.embedding_file,colors))

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