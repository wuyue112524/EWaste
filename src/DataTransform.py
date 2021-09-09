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
        self.mining_equipment['Th/s of Miner'] = round(self.mining_equipment['Power (W)'] / self.mining_equipment['Efficiency_J_Gh']/1000,4)
        self.mining_equipment['Costs per Thash/s in $'] = 1 / self.mining_equipment['Th/s of Miner'] * self.mining_equipment['Costs per day in $']
        self.mining_equipment['electricity_cost'] = electricity_cost
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
        
        
        ## calculate is_profitable and cumulative unprofitable days
        output['profit'] = output['Rev per Thash/s in $'] - output['Costs per Thash/s in $']
        output['is_profitable'] = output['profit'].apply(self.__is_profitable)
        output['is_profitable_num'] = output['is_profitable'].apply(self.__is_profitable_num)
        
        ## generate a pivot table to calculate cum unprofitable days for each miner
        unprofitable = pd.pivot(output,index = miner_rev_date, columns= 'Miner_name',
                                values = 'is_profitable_num')
        unprofitable_cum = pd.DataFrame()
        
        for column in unprofitable.columns:
            unprofitable_cum[column] = unprofitable[column].cumsum()
        
        ## melt back to long format
        unprofitable_cum_long = pd.melt(unprofitable_cum,value_vars= None,var_name = 'Miner_name',
                    value_name= 'cum_unprofitable_days',ignore_index= False)
        
        unprofitable_cum_long = unprofitable_cum_long.reset_index(drop = False)
        output_2 = pd.merge(output, unprofitable_cum_long, how = 'left', on = [miner_rev_date,'Miner_name'])
        
        
        
        # storage_2 = []
        # output['is_profitable'] = None
        # output['cum_unprofitable_days'] = None
        # miner_name_list = output['Miner_name'].unique()
        # for miner in miner_name_list:
        #     sub_df = output[output['Miner_name'] == miner]
        #     sub_df = sub_df.sort_values(miner_rev_date,ascending= True)
        #     sub_df = sub_df.reset_index(drop = True)
        #     i = 0
        #     for index, row in sub_df.iterrows():
        #         if row['Rev per Thash/s in $'] - row['Costs per Thash/s in $'] >= 0:
        #             sub_df.at[index,'is_profitable'] = True
        #             sub_df.at[index,'cum_unprofitable_days'] = i
        #         else:
        #             sub_df.at[index,'is_profitable'] = False
        #             i += 1
        #             sub_df.at[index,'cum_unprofitable_days'] = i
        #    storage_2.append(sub_df)
        
        #output_2 = pd.concat(storage_2)
                
        
    
        self.miner_profitability = output_2
        return self.miner_profitability
    
    def __is_profitable(self,x):
        if x >= 0:
            return True
        else:
            return False
    
    def __is_profitable_num(self,x):
        if x == True:
            return 0
        else:
            return 1
        
            