import psycopg2
import yaml
from sqlalchemy import create_engine
from src.DataCollect import DataCollect
import os
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

    ## connect to db
    config_path = 'config.yml'

    with open(config_path) as credential:
        config = yaml.load(credential,Loader = yaml.FullLoader)

    a = 'postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}'.format(**config['ewaste'])
    engine = create_engine(a)
    miner_revenue.to_sql('miner_revenue', con = engine, index = False,if_exists = 'replace')
    network_hashrate.to_sql('network_hashrate', con = engine, index = False,if_exists = 'replace')
    
    query_1 = '''DROP TABLE IF EXISTS mining_equipment
            '''

    query_2 = '''CREATE TABLE IF NOT EXISTS mining_equipment(
                    "Miner_name" VARCHAR(255),
                    "Type" VARCHAR(255),
                    "Date of release" VARCHAR(255),
                    "UNIX_date_of_release" VARCHAR(255),
                    "Hashing power (Th/s)" numeric,
                    "Power (W)" numeric,
                    "Efficiency_J_Gh" numeric,
                    "Weight in kg" numeric,
                    "Efficiency:\nsuggested alternative(s)" VARCHAR(255),
                    "Qty" VARCHAR(255),
                    "UNIX_date_of_release_tran" VARCHAR(255)
                    )'''

    query_3 = """INSERT INTO mining_equipment (
                            "Miner_name",
                            "Type",
                            "Date of release",
                            "UNIX_date_of_release",
                            "Hashing power (Th/s)",
                            "Power (W)",
                        "Efficiency_J_Gh",
                        "Weight in kg",
                        "Efficiency:\nsuggested alternative(s)",
                        "Qty",
                        "UNIX_date_of_release_tran"
                            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"""
    
    value = zip(mining_equipment['Miner_name'],
           mining_equipment['Type'],
           mining_equipment['Date of release'],
           mining_equipment['UNIX_date_of_release'],
           mining_equipment['Hashing power (Th/s)'],
           mining_equipment['Power (W)'],
           mining_equipment['Efficiency_J_Gh'],
           mining_equipment['Weight in kg'],
           mining_equipment['Efficiency:\nsuggested alternative(s)'],
           mining_equipment['Qty'],
           mining_equipment['UNIX_date_of_release_tran']
          )
    with psycopg2.connect(**config['ewaste']) as connection:
        #create a cursor
        c = connection.cursor()
        drop_query = query_1
        create_query = query_2
        insert_query = query_3
        c.execute(drop_query)
        c.execute(create_query)
        for item in value:
            c.execute(insert_query,item)
        

    print('All data has been successfully written in db')