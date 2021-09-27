import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import os
from dotenv import load_dotenv
import pandas as pd
from src.DataCollect import DataCollect
from src.DataTransform import DataTransform
from src.InsDiscardModel import InsDiscardModel
import psycopg2
import yaml
from sqlalchemy import create_engine

def read_table(config,database,table_name):
    with psycopg2.connect(**config[database]) as connection:
        c =  connection.cursor()
        query = "select * from {};".format(table_name)
        
        c.execute(query)
        values = c.fetchall()
        
        col_names = []
        for elt in c.description:
            col_names.append(elt[0])
        df = pd.DataFrame(values, columns = col_names)
    return df


#load_dotenv()
#miner_revenue_code = os.getenv('miner_revenue_code')
#network_hashrate_code = os.getenv('network_hashrate_code')
#mining_equipment_url = os.getenv('mining_equipment_url')
#quandl_api = os.getenv('quandl_api_key',None)

#data_loader = DataCollect()
#miner_revenue_original = data_loader.load_quandl_api(miner_revenue_code,['date','miner_rev'],quandl_api)
#network_hashrate_original = data_loader.load_quandl_api(network_hashrate_code,['date','network_hashrate'],quandl_api)
#mining_equipment_original = data_loader.pull_sheet(mining_equipment_url)






external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__,external_stylesheets = external_stylesheets)

app.layout = html.Div(children = 
                     [
            html.H1(id = 'app_title',children = 'E-Waste Instant Discard Model'),
            html.H6('Electricity cost in $'),
            dcc.Slider(id = 'app_slider_electricity_cost',
                      min = 0.01,
                      max = 0.2,
                      value = 0.05,
                      step = 0.001,
                      tooltip = {'always_visible':True},
        
                       updatemode = 'mouseup'
                      ),
            html.H6('Instant discard days'),
            dcc.Slider(id = 'app_slider_discard_days',
                      min = 1,
                      max = 365,
                      value = 1,
                      step = 1,
                      tooltip = {'always_visible':True},
                       updatemode = 'mouseup',
                    
                      ),
            dcc.Graph(id = 'app_graph')
                     ])

@app.callback(
    Output('app_graph', 'figure'),
    Input('app_slider_electricity_cost', 'value'),
    Input('app_slider_discard_days', 'value')
)
def update_figure(selected_elect_tricity_cost,instant_discard_days):
    electricity_cost = selected_elect_tricity_cost
    
    data_transformer = DataTransform(miner_revenue_original,
                                         network_hashrate_original,
                                         mining_equipment_original)
    mining_equipment_transform = data_transformer.calculate_daily_cost(electricity_cost= electricity_cost)
    miner_revenue_transform = data_transformer.calculate_daily_rev()
    miner_profitability_transform = data_transformer.calculate_profitability()
    
    ## Instant Discard Model
    insDiscard_model = InsDiscardModel(mining_equipment_transform,
                                           miner_revenue_transform,
                                           miner_profitability_transform)
    miner_hashrate_attribution = insDiscard_model.attribute_hashrate(instant_discard_days)
    ewaste = insDiscard_model.calculate_ewaste(instant_discard_days)
    graph = insDiscard_model.graph_data_export()
    graph['year'] = pd.to_datetime(graph['year'])
    graph['year'] = graph['year'].dt.year
    fig = px.bar(graph,x = 'year', y = 'Ewaste in t')
    fig.update_xaxes(tickvals= list(range(2016,2022)))



    return fig

if __name__ == "__main__":
    config_path = 'C:/Users/clair/CCAF/Week45 0830-0903/E-waste coding/EWaste/config.yml'

    with open(config_path) as credential:
        config = yaml.load(credential,Loader = yaml.FullLoader)

    mining_equipment_original = read_table(config,'ewaste','mining_equipment')
    miner_revenue_original =  read_table(config,'ewaste','miner_revenue')
    network_hashrate_original = read_table(config,'ewaste','network_hashrate')
 
    column_list = ['Power (W)','Hashing power (Th/s)','Efficiency_J_Gh','Weight in kg']
    for column in column_list:            
        mining_equipment_original[column] = mining_equipment_original[column].astype('float')
        
    app.run_server()