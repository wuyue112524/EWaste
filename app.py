from src.DataCollect import DataCollect
from src.EWaste import EWaste
import os
import time
from dotenv import load_dotenv


if __name__ == "__main__":
    load_dotenv()
    miner_revenue_url = os.getenv('miner_revenue_url')
    network_hashrate_url = os.getenv('network_hashrate_url')
    mining_equipment_url = os.getenv('mining_equipment_url')
    electricity_cost = float(os.getenv('electricity_cost'))
    
    ## load data here
    data_loader = DataCollect()
    miner_revenue = data_loader.load_quandl_api(miner_revenue_url,['date','miner_rev'])
    time.sleep(2)
    network_hashrate = data_loader.load_quandl_api(network_hashrate_url,['date','network_hashrate'])
    mining_equipment = data_loader.pull_sheet(mining_equipment_url)
    
    ## model calculation starts here
    
    ewaste = EWaste(miner_revenue,network_hashrate,mining_equipment)
    mining_equipment = ewaste.calculate_daily_cost(electricity_cost= electricity_cost)
    miner_revenue = ewaste.calculate_daily_rev()
    miner_profitability = ewaste.calculate_profitability()
    
    mining_equipment.to_excel('mining_equipment.xlsx',index = False)
    miner_revenue.to_excel('miner_revenue.xlsx',index = False)
    miner_profitability.to_excel('miner_profitability.xlsx',index = False)
    
   

    
    
    