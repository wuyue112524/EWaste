import requests
import pandas as pd
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
from datetime import datetime

def unix_time_to_datetime(dataframe, column, new_column_name):
    df = dataframe.copy()
    df[new_column_name] = None
    for index, row in df.iterrows():
        time = datetime.utcfromtimestamp(int(row[column])).strftime('%Y-%m-%d')
        df.at[index,new_column_name] = time
    return df
        
        

class DataCollect:
    def __init__(self):
        pass

    
    def load_quandl_api(self,quandl_api_url,name_list):
        '''
        param:
        load data from quandl in json format
        name_list: list
            a list of column name for aquired data from quandl api, eg. ['date','miner_rev']

        '''
        response = requests.get(quandl_api_url).json()
        output = pd.DataFrame(response['dataset']['data'],columns = name_list)
        return output
    
    
    
    def pull_sheet(self,mining_equipment_url, range_name = 'SHA-256!A:J',
                   token_credential = 'C:/Users/clair/CCAF/google_credentials/google_sheet_token_credentials.pickle',
                   credentials = "C:/Users/clair/CCAF/google_credentials/google_sheet_credentials.json"):
        '''
        Get a google spread sheet from admin panel


        Parameter
        ----------
        sheet_id: str
        Google spread sheet id. A serial number in url after d/. 
        range_name: str
        Specify data area to load. Format is 
        sheet_name!begin:end

        Return
        ----------
        df: pandas.DataFrame
        google spreadsheet 
        '''
        sheet_id = mining_equipment_url.split('/')[-2]

        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(token_credential):
            with open(token_credential, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                  credentials, scopes)
                creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        #   with open('credential/token.pickle', 'wb') as token:
        #       pickle.dump(creds, token)

        service = build('sheets', 'v4', credentials=creds)
    

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=sheet_id,
                                range= range_name).execute()
        values = result.get('values', [])
       
        if not values:
            print('No data found.')
        else:
            print('Data Successfully loaded.')
            print("Data version: "+values[1][0])
            df = pd.DataFrame(values[4:], columns=values[3][0:9])
            df = df[pd.notnull(df['UNIX_date_of_release'])]
            df = df[df['Power (W)'] != '']
            
            ##change type: str to float
            column_list = ['Power (W)','Hashing power (Th/s)','Efficiency_J_Gh']
            for column in column_list:
                df[column] = df[column].str.replace(',','')
                df[column] = df[column].astype('float')
            
            df = df.reset_index(drop = True)
            print('The shape of data is {}'.format(df.shape))
            dataframe = unix_time_to_datetime(df, 'UNIX_date_of_release', 'UNIX_date_of_release_tran')
            return dataframe