import pandas as pd
class GraDiscardModel:
    
    def __init__(self, miner_equipment, miner_revenue,miner_profitability):
        self.miner_equipment = miner_equipment
        self.miner_revenue  = miner_revenue
        self.miner_profitability = miner_profitability
        self.miner_hashrate_attribution = None
        self.miner_ewaste = None
        self.discard_days = 365
        
    def calculate_deprecation_percentage(self,discard_days = 365):
        self.discard_days = discard_days
        def func(x):
            y = x/discard_days
            if y<= 1:
                return y
            else:
                return 1
        self.miner_profitability['depreciation_percentage'] = self.miner_profitability['cum_unprofitable_days'].apply(func)
        
    
    def attribute_hashrate(self):
        
        miner_prof_date = self.miner_profitability.columns[0]
        def func(x,discard_days):
            if x <= discard_days:
             return True
            else:
                return False
            
        self.miner_profitability['is_active'] = self.miner_profitability['cum_unprofitable_days'].apply(func,discard_days = self.discard_days)
        self.miner_profitability['is_ever_profitable'] = self.miner_profitability['cum_unprofitable_days'].apply(func,discard_days = 0)
        self.miner_hashrate_attribution = self.miner_profitability.groupby(miner_prof_date,as_index = False).agg({'is_active':'sum','is_ever_profitable':'sum','network_hashrate':'max'})
        self.miner_hashrate_attribution.columns = [miner_prof_date,'profitable_model','ever_profitable_model','network_hashrate']
        self.miner_hashrate_attribution['Ths attribution per model'] = self.miner_hashrate_attribution['network_hashrate'] / self.miner_hashrate_attribution['profitable_model']

        
    
    def miner_mix_1st_round(self):
        miner_prof_date = self.miner_profitability.columns[0]
        efficiency_to_merge = self.miner_equipment[['Miner_name','Th/s of Miner']]
        self.miner_profitability = pd.merge(self.miner_profitability, efficiency_to_merge, how = 'left', on ='Miner_name')
        df_to_merge = self.miner_hashrate_attribution[[miner_prof_date,'Ths attribution per model']]
        self.miner_profitability = pd.merge(self.miner_profitability,df_to_merge, how = 'left', on = miner_prof_date)
        self.miner_profitability['quantity_before_adjust'] = self.miner_profitability['Ths attribution per model'] / self.miner_profitability['Th/s of Miner']
        self.miner_profitability['quantity_adjust_1st_round'] = self.miner_profitability['quantity_before_adjust'] * (1 - self.miner_profitability['depreciation_percentage'])
        self.miner_profitability['depreciation_hashrate_1st_round'] = self.miner_profitability['quantity_adjust_1st_round'] * self.miner_profitability['Th/s of Miner']
        depreciation_df = self.miner_profitability.groupby(miner_prof_date,as_index= False)['depreciation_hashrate_1st_round'].sum()
        self.miner_hashrate_attribution = pd.merge(self.miner_hashrate_attribution, depreciation_df, how = 'left', on = miner_prof_date)
        self.miner_hashrate_attribution['1st_round_difference'] = self.miner_hashrate_attribution['network_hashrate'] - self.miner_hashrate_attribution['depreciation_hashrate_1st_round']
        self.miner_hashrate_attribution['1st_round_difference'] = self.miner_hashrate_attribution['1st_round_difference'].round(4)
        
    
    def miner_mix_2nd_round(self):
        miner_prof_date = self.miner_profitability.columns[0]
        self.miner_hashrate_attribution['everprofitable_distributed_hashrate'] = self.miner_hashrate_attribution['1st_round_difference'] / self.miner_hashrate_attribution['ever_profitable_model']
        df_to_merge = self.miner_hashrate_attribution[[miner_prof_date,'everprofitable_distributed_hashrate']]
        self.miner_profitability = pd.merge(self.miner_profitability, df_to_merge, how = 'left', on = miner_prof_date)
        def func(row):
            if row['cum_unprofitable_days'] == 0:
                return row['everprofitable_distributed_hashrate']
            else:
                return 0
        self.miner_profitability['everprofitable_distributed_hashrate_adjust'] = self.miner_profitability.apply(func,axis = 1)
        self.miner_profitability.drop('everprofitable_distributed_hashrate',axis = 1,inplace = True)
        self.miner_profitability['quantity_adjust_2nd_round'] = self.miner_profitability['quantity_adjust_1st_round'] + self.miner_profitability['everprofitable_distributed_hashrate_adjust']/ self.miner_profitability['Th/s of Miner']
        
    
    def calculate_miner_quantity(self,discard_days = 365):
        self.calculate_deprecation_percentage(discard_days)
        self.attribute_hashrate()
        self.miner_mix_1st_round()
        self.miner_mix_2nd_round()
        
    
    def calculate_ewaste(self):
        max_quantity = {}
        model_list = self.miner_profitability['Miner_name'].unique()
        for model in model_list:
            sub_df = self.miner_profitability[(self.miner_profitability['Miner_name'] == model) & (self.miner_profitability['cum_unprofitable_days'] == 0)]
            max_quantity[model] = sub_df['quantity_adjust_2nd_round'].max()
        def func(row):
            if (row['cum_unprofitable_days'] <= self.discard_days) & (row['is_profitable'] == False):
                return max_quantity[row['Miner_name']]/self.discard_days
            else:
                return 0
        self.miner_profitability['daily_discard_quantity'] = self.miner_profitability.apply(func,axis = 1)
        miner_weight = self.miner_equipment[['Miner_name','Weight in kg']]
        self.miner_profitability = pd.merge(self.miner_profitability,miner_weight, how = 'left', on = 'Miner_name')
        
        self.miner_profitability['daily_discard_ewaste_in_tons'] = self.miner_profitability['daily_discard_quantity'] * self.miner_profitability['Weight in kg'] / 1000
        
        
        
        
        miner_prof_date = self.miner_profitability.columns[0]
        ewaste = self.miner_profitability[[miner_prof_date,'daily_discard_ewaste_in_tons']]
        ewaste['year'] = ewaste[miner_prof_date].dt.year
        ewaste['month'] = ewaste[miner_prof_date].dt.month
        self.miner_ewaste = ewaste.groupby(['year','month'],as_index = False)['daily_discard_ewaste_in_tons'].sum()
        self.miner_ewaste['year'] = self.miner_ewaste['year'].astype('int').astype('str')
        self.miner_ewaste['month'] = self.miner_ewaste['month'].astype('int').astype('str')
        self.miner_ewaste[miner_prof_date] = self.miner_ewaste['year'] + '-'+ self.miner_ewaste['month'] + '-01'
        self.miner_ewaste.drop(['year','month'],axis = 1, inplace = True)
        
        return self.miner_ewaste
        
        
        