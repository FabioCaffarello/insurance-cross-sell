import os
import pandas as pd
from sqlalchemy import create_engine, inspect

class Postgres(object):
    def __init__(self):
        self.host = 'comunidade-ds-postgres.c50pcakiuwi3.us-east-1.rds.amazonaws.com'
        self.usenamer = os.environ.get('POSTGRES_CDS_USERNAME')
        self.password = os.environ.get('POSTGRES_CDS_PASSWORD')
        self.port = 5432
        self.database = 'comunidadedsdb'
        
    def engine(self):
        '''
        creates the engine with the database in which the parameters for connection were determined at class initialization
        
        Return
        ------
        The postgres engine
        '''
        engine = create_engine(f"postgresql://{self.usenamer}:{self.password}@{self.host}:{self.port}/{self.database}")
        return engine
    
    def inspect_schema(self, engine=None):
        '''
        Performs the inspection of the database to check the schemas and their respective tables in each schema
        
        Paramns
        -------
        
        engine: postgres engine
        
        Return
        ------
        Returns a dictionary where the keys are the schemas (the information_schema and public schemas are filtered)
        and the names of the tables contained in each schema as a list in the dictionary values.
        '''
        # inspect
        if not engine: 
            engine = Postgres.engine(self)
        
        inspector = inspect(engine)
        
        # get schemas
        schemas = inspector.get_schema_names()
        
        dict_schema = {}
        for schema in schemas:
            if (schema != 'information_schema') & (schema != 'public'):
                # list of tables in each schema
                tables_schema = [table_name for table_name in inspector.get_table_names(schema=schema)]
                dict_schema[schema] = tables_schema
                
        return dict_schema
                
    def get_data(self):
        '''
        Perform querys of all tables of all schemas except for information_schema and public
        
        Return
        ------
        Returns a dictionary where the keys are the tables related in the dictionary values that the insp_schema function returns.
        The dictionary values are dated that contain the respective tables in the postgres
        '''
        engine = Postgres.engine(self)
        dict_schema = Postgres.inspect_schema(self, engine)
        dict_tables = {}
        with engine.connect() as conn:
            for schema in dict_schema.keys():
                for table in dict_schema[schema]:
                    dict_tables[table] = pd.read_sql_table(table, conn, schema)

        return dict_tables #users, vehicle, insurance