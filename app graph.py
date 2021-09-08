from src.DataCollect import DataCollect
from src.DataTransform import DataTransform
from src.InsDiscardModel import InsDiscardModel
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime


if __name__ == "__main__":
    load_dotenv()
    miner_revenue_code = os.getenv('miner_revenue_code')
    network_hashrate_code = os.getenv('network_hashrate_code')
    mining_equipment_url = os.getenv('mining_equipment_url')
    quandl_api = os.getenv('quandl_api_key',None)
    electricity_cost_list = [x/100 for x in range(1,21,1)]
    
    ## load data here
    data_loader = DataCollect()
    miner_revenue_original = data_loader.load_quandl_api(miner_revenue_code,['date','miner_rev'],quandl_api)
    
    network_hashrate_original = data_loader.load_quandl_api(network_hashrate_code,['date','network_hashrate'],quandl_api)
    mining_equipment_original = data_loader.pull_sheet(mining_equipment_url)
    
    ## model calculation starts here
    storage = []
    for electricity_cost in electricity_cost_list:
        print(electricity_cost)
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
        miner_hashrate_attribution = insDiscard_model.attribute_hashrate(instant_discard_days = 1)
        ewaste = insDiscard_model.calculate_ewaste(instant_discard_days=1)
        graph = insDiscard_model.graph_data_export()
        storage.append(graph)
        
    output = pd.concat(storage)
    output['data_update_time'] = datetime.now().strftime('%Y-%m-%d')
    output.to_excel('output/graph_data.xlsx',index = False)
    
    
    
    
    
   

    
    
    