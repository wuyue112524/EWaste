import pandas as pd
class InsDiscardModel:
    
    def __init__(self, miner_equipment, miner_revenue,miner_profitability):
        self.miner_equipment = miner_equipment
        self.miner_revenue  = miner_revenue
        self.miner_profitability = miner_profitability
        self.miner_hashrate_attribution = None
        self.miner_ewaste = None
    
    def attribute_hashrate(self,instant_discard_days = 1):
        miner_prof_date = self.miner_profitability.columns[0]
        self.miner_profitability[miner_prof_date] = pd.to_datetime(self.miner_profitability[miner_prof_date])
        date_list = self.miner_profitability[miner_prof_date].unique()
        df_list = []
        for date in date_list:
            storage = {}
            sub_df = self.miner_profitability[self.miner_profitability[miner_prof_date] == date]
            num_profitable_model = sub_df[sub_df['cum_unprofitable_days'] < instant_discard_days].shape[0]
            network_hashrate = sub_df['network_hashrate'].unique()[0]
            storage[miner_prof_date] = date
            storage['profitable_model'] = num_profitable_model
            storage['network_hashrate'] = network_hashrate
            df_list.append(storage)
        output = pd.DataFrame(df_list)
        output['Ths attribution per model'] = output['network_hashrate'] / output['profitable_model']
        self.miner_hashrate_attribution  = output
        return self.miner_hashrate_attribution
    
    def calculate_ewaste(self,instant_discard_days = 1):
        miner_list = self.miner_profitability['Miner_name'].unique()
        miner_prof_date = self.miner_profitability.columns[0]
        df_list = []
        for miner in miner_list:
            storage = {}
            storage['Miner_name'] = miner
            sub_df = self.miner_profitability[self.miner_profitability['Miner_name'] == miner]
            sub_df = sub_df[sub_df['cum_unprofitable_days'] == instant_discard_days]
            if sub_df.shape[0]> 0:
                sub_df = sub_df.sort_values(miner_prof_date,ascending = True)
                sub_df = sub_df.reset_index(drop = True)
                ## check if the miner is still profitable
                end_of_life = sub_df.loc[0,miner_prof_date]
                storage['End of life'] = end_of_life
                max_hash = self.miner_hashrate_attribution[self.miner_hashrate_attribution[miner_prof_date]<end_of_life]
                max_hash = max_hash['Ths attribution per model'].max()
                storage['Max Ths'] = max_hash
                df_list.append(storage)
            else:
                pass
        output = pd.DataFrame(df_list)
        df_to_merge = self.miner_equipment[['Miner_name','Weight in kg','Th/s of Miner','UNIX_date_of_release_tran']]
        output = pd.merge(output, df_to_merge, how = 'left', on = 'Miner_name')
        output['Max miner quantity'] = output['Max Ths'] / output['Th/s of Miner']
        output['Ewatste in kg'] = output['Max miner quantity'] * output['Weight in kg']
        self.miner_ewaste = output
        return self.miner_ewaste

            
        
        
            
            
    
        