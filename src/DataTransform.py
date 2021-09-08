import pandas as pd
class DataTransform:
    def __init__(self,miner_revenue,network_hashrate,mining_equipment):
        '''
        param:
            miner_revenue: dataframe
            network_hashrate: dataframe
            mining_equipment: dataframe

        attribute:
            miner_rev: dataframe
            miner_profitability: dataframe
        '''
        self.miner_revenue = miner_revenue
        self.network_hashrate = network_hashrate
        self.mining_equipment = mining_equipment
        self.miner_profitability = None
        
    def calculate_daily_cost(self,electricity_cost):
        self.mining_equipment['Costs per day in $'] = self.mining_equipment['Power (W)'] / 1000 * electricity_cost * 24
        self.mining_equipment['Th/s of Miner'] = self.mining_equipment['Power (W)'] / self.mining_equipment['Efficiency_J_Gh']/1000
        self.mining_equipment['Costs per Thash/s in $'] = 1 / self.mining_equipment['Th/s of Miner'] * self.mining_equipment['Costs per day in $']
        
        return self.mining_equipment
        
        
    
    def calculate_daily_rev(self):
        ## get data for miner revenue per Th/s
        miner_rev_date = self.miner_revenue.columns[0]
        miner_rev_colname = self.miner_revenue.columns[1]
        network_hash_date = self.network_hashrate.columns[0]
        network_hash__colname = self.network_hashrate.columns[1]
        
        self.miner_revenue = pd.merge(self.miner_revenue,self.network_hashrate, how = 'left', 
                                      left_on = miner_rev_date,right_on = network_hash_date)
        self.miner_revenue['Rev per Thash/s in $'] = self.miner_revenue[miner_rev_colname] / self.miner_revenue[network_hash__colname]
        self.miner_revenue[miner_rev_date] = pd.to_datetime(self.miner_revenue[miner_rev_date])
        
        return self.miner_revenue
    
    def calculate_profitability(self):
        ## change format to datetime
        miner_rev_date = self.miner_revenue.columns[0]
        storage = []
        self.mining_equipment['UNIX_date_of_release_tran'] = pd.to_datetime(self.mining_equipment['UNIX_date_of_release_tran'])
        for index, row in self.mining_equipment.iterrows():
            release_date = row['UNIX_date_of_release_tran']
            equipment_name = row['Miner_name']
            cost_per_ths = row['Costs per Thash/s in $']
            sub_rev = self.miner_revenue[self.miner_revenue[miner_rev_date]>= release_date]
            sub_rev['Miner_name'] = equipment_name
            sub_rev['UNIX_date_of_release_tran'] = release_date
            sub_rev['is_release'] = True
            sub_rev['Costs per Thash/s in $'] = cost_per_ths
            storage.append(sub_rev)
            
        output = pd.concat(storage)
        output = output.reset_index(drop = True)
        output['is_profitable'] = None
        for index, row in output.iterrows():
            if row['Rev per Thash/s in $'] - row['Costs per Thash/s in $'] >= 0:
                output.at[index,'is_profitable'] = True
            else:
                output.at[index,'is_profitable'] = False
        self.miner_profitability = output
        return self.miner_profitability
            