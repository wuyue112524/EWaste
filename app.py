from src.DataCollect import DataCollect
from src.DataTransform import DataTransform
from src.InsDiscardModel import InsDiscardModel
from src.GraDiscardModel import GraDiscardModel
from src.utils import read_table
import os
from dotenv import load_dotenv
import psycopg2
import yaml
from sqlalchemy import create_engine
import pandas as pd



if __name__ == "__main__":
    load_dotenv()
    # miner_revenue_code = os.getenv('miner_revenue_code')
    # network_hashrate_code = os.getenv('network_hashrate_code')
    # mining_equipment_url = os.getenv('mining_equipment_url')
    # quandl_api = os.getenv('quandl_api_key',None)
    electricity_cost = float(os.getenv('electricity_cost'))
    
    # ## load data here
    # data_loader = DataCollect()
    # miner_revenue = data_loader.load_quandl_api(miner_revenue_code,['date','miner_rev'],quandl_api)
    
    # network_hashrate = data_loader.load_quandl_api(network_hashrate_code,['date','network_hashrate'],quandl_api)
    # mining_equipment = data_loader.pull_sheet(mining_equipment_url)
    config_path = 'C:/Users/clair/CCAF/Week45 0830-0903/E-waste coding/EWaste/config.yml'
    with open(config_path) as credential:
        config = yaml.load(credential,Loader = yaml.FullLoader)

    mining_equipment = read_table(config,'ewaste','mining_equipment')
    miner_revenue =  read_table(config,'ewaste','miner_revenue')
    network_hashrate = read_table(config,'ewaste','network_hashrate')
    column_list = ['Power (W)','Hashing power (Th/s)','Efficiency_J_Gh','Weight in kg']
    for column in column_list:            
        mining_equipment[column] = mining_equipment[column].astype('float')
    
    ## model calculation starts here
    
    data_transformer = DataTransform(miner_revenue,network_hashrate,mining_equipment)
    mining_equipment = data_transformer.calculate_daily_cost(electricity_cost= electricity_cost)
    miner_revenue = data_transformer.calculate_daily_rev()
    miner_profitability = data_transformer.calculate_profitability()
    
    ## Instant Discard Model
    #insDiscard_model = InsDiscardModel(mining_equipment,miner_revenue,miner_profitability)
    #miner_hashrate_attribution = insDiscard_model.attribute_hashrate(instant_discard_days = 1)
    #ewaste = insDiscard_model.calculate_ewaste(instant_discard_days=1)
    #graph = insDiscard_model.graph_data_export()
    #graph.to_excel('graph_0.05.xlsx',index = False)
    
    ## Gradual Discard Model
    graDiscard_model = GraDiscardModel(mining_equipment,miner_revenue,miner_profitability)
    graDiscard_model.calculate_miner_quantity(discard_days = 365)
    ewaste = graDiscard_model.calculate_ewaste()
    
    
    
    
   

    
    
    