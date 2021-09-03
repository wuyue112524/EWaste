class EWaste:
    def __init__(self,miner_revenue,network_hashrate,mining_equipment):
        '''
        param:
            miner_revenue: dataframe
            network_hashrate: dataframe
            mining_equipment: dataframe

        attribute:
            miner_cost: dataframe
            miner_profitability: dataframe
        '''
        self.miner_revenue = miner_revenue
        self.network_hashrate = network_hashrate
        self.mining_equipment = mining_equipment
        self.miner_cost = None
        self.miner_profitability = None
        
    def calculate_daily_cost(self,electricity_cost):
        pass
        
    
    def calculate_daily_profitability(self):
        pass