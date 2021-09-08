from src.DataCollect import DataCollect
from src.DataTransform import DataTransform
import os
import time
from dotenv import load_dotenv


if __name__ == "__main__":
    load_dotenv()
    miner_revenue_code = os.getenv('miner_revenue_code')
    network_hashrate_code = os.getenv('network_hashrate_code')
    mining_equipment_url = os.getenv('mining_equipment_url')
    quandl_api = os.getenv('quandl_api_key',None)
    electricity_cost = float(os.getenv('electricity_cost'))
    
    ## load data here
    data_loader = DataCollect()
    miner_revenue = data_loader.load_quandl_api(miner_revenue_code,['date','miner_rev'],quandl_api)
    
    network_hashrate = data_loader.load_quandl_api(network_hashrate_code,['date','network_hashrate'],quandl_api)
    mining_equipment = data_loader.pull_sheet(mining_equipment_url)
    
    ## model calculation starts here
    
    data_transformer = DataTransform(miner_revenue,network_hashrate,mining_equipment)
    mining_equipment = data_transformer.calculate_daily_cost(electricity_cost= electricity_cost)
    miner_revenue = data_transformer.calculate_daily_rev()
    miner_profitability = data_transformer.calculate_profitability()
    
    mining_equipment.to_excel('mining_equipment.xlsx',index = False)
    miner_revenue.to_excel('miner_revenue.xlsx',index = False)
    miner_profitability.to_excel('miner_profitability.xlsx',index = False)
    
   

    
    
    