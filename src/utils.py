import psycopg2
import pandas as pd

def read_table(config,database,table_name):
    with psycopg2.connect(**config[database]) as connection:
        c =  connection.cursor()
        query = "select * from {};".format(table_name)
        
        c.execute(query)
        values = c.fetchall()
        
        col_names = []
        for elt in c.description:
            col_names.append(elt[0])
        df = pd.DataFrame(values, columns = col_names)
    return df
