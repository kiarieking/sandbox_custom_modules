'''Sample importation file'''

import psycopg2
import sys
import pandas as pd

param_dic = {
    "host"      : "localhost",
    "database"  : "quatrix_core",
    "user"      : "quatrix",
    "password"  : "password"
}

def connect(params_dic):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params_dic)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        sys.exit(1) 
    print("Connection successful")
    return conn

def postgresql_to_dataframe_to_excel(conn, select_query, column_names):
    """
    Tranform a SELECT query into a pandas dataframe
    """
    cursor = conn.cursor()
    try:
        cursor.execute(select_query)
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        cursor.close()
        return 1
    
    tuples = cursor.fetchall()
    cursor.close()
    
    # Convert tuples to pandas dataframe
    df = pd.DataFrame(tuples, columns=column_names)
    df.to_excel('output3.xlsx', index=False)
    return df


select_query= """
        SELECT vehicle.id,  
            vehicle.licence_plate, 
            vehicle_driver.driver_id,
            vehicle_owner.owner_id            
        FROM vehicle_driver,vehicle_owner, vehicle
        WHERE vehicle.id = vehicle_driver.vehicle_id
        AND vehicle.id = vehicle_owner.vehicle_id;
    """
conn = connect(param_dic)
column_names = ["Vehicle ID", "License Plate", "Driver ID", "Carrier ID"]

postgresql_to_dataframe_to_excel(conn, select_query, column_names)