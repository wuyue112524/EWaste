import pandas as pd
class InsDiscardModel:
    
    def __init__(self, miner_equipment, miner_revenue,miner_profitability):
        self.miner_equipment = miner_equipment
        self.miner_revenue  = miner_revenue
        self.miner_profitability = miner_profitability
        self.miner_hashrate_attribution = None
        self.miner_ewaste = None
        self.graph_data =  None
    
    def attribute_hashrate(self,instant_discard_days = 1):
        miner_prof_date = self.miner_profitability.columns[0]
        def func(x,discard_days):
            if x <= discard_days:
             return True
            else:
                return False
            
        self.miner_profitability['is_active'] = self.miner_profitability['cum_unprofitable_days'].apply(func,discard_days = instant_discard_days)
        self.miner_hashrate_attribution = self.miner_profitability.groupby(miner_prof_date,as_index = False).agg({'is_active':'sum','network_hashrate':'max'})
        self.miner_hashrate_attribution.columns = [miner_prof_date,'profitable_model','network_hashrate']
        self.miner_hashrate_attribution['Ths attribution per model'] = self.miner_hashrate_attribution['network_hashrate'] / self.miner_hashrate_attribution['profitable_model']
        
        
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
        df_to_merge = self.miner_equipment[['Miner_name','Weight in kg','Th/s of Miner','UNIX_date_of_release_tran','electricity_cost']]
        output = pd.merge(output, df_to_merge, how = 'left', on = 'Miner_name')
        output['Max miner quantity'] = output['Max Ths'] / output['Th/s of Miner']
        output['Ewaste in kg'] = output['Max miner quantity'] * output['Weight in kg']
        self.miner_ewaste = output
        return self.miner_ewaste
    
    def graph_data_export(self):
        df = self.miner_ewaste.copy()
        df['year'] = df['End of life'].dt.year
        df['year'] = df['year'].astype('str') +'-01-01'
        df['Ewaste in t'] = df['Ewaste in kg'] / 1000
        graph = df.groupby('year')[['Ewaste in t','electricity_cost']].agg({'Ewaste in t':'sum',
                                                                            'electricity_cost':'max'}).reset_index(drop = False)
        graph.columns = ['year','Ewaste in t','electricity_cost']
        self.graph_data = graph
        return self.graph_data
        
        

            
        
        
            
            
    
        