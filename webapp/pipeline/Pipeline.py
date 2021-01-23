import bisect
import inflection

import joblib as jb
import pandas as pd



class insuranse_cross_sell(object):
    def __init__(self):
        # self.home_path          = 'D:/01-DataScience/04-Projetos/00-Git/insurance-cross-sell/webapp/'
        self.home_path          = ''
        self.age_stage_encoder  = jb.load(open(self.home_path + 'parameter/age_stage.pkl', 'rb'))
    
    def data_cleaning(self, df):
        # snakecase
        snakecase = lambda col: inflection.underscore(col)
        new_columns = list(map(snakecase, df.columns))

        # rename
        df.columns = new_columns

        return df
    
    def age_stage(self, num, breakpoints=[10, 20, 30, 45, 60, 70, 80, 120], result='01234567'):
        i = bisect.bisect(breakpoints, num-1)
        age_mapping = {
            0: 'Child',
            1: 'Teenager',
            2: 'Young',
            3: 'Adult',
            4: 'Midlife',
            5: 'Senior',
            6: 'Mature Adulthood',
            7: 'Late Adulthood'
        }
        return age_mapping[i]

    
    def feature_engineering(self, df):
        # Age Stage
        df['age_stage'] = df['age'].apply(lambda row: insuranse_cross_sell.age_stage(self,row))
        
        # vehicle age
        vehicle_age_mapping = {'< 1 Year':0,
                               '1-2 Year':1,
                               '> 2 Years':2}

        df['vehicle_age'] = df['vehicle_age'].map(vehicle_age_mapping)
        
        # vehicle demage versus license
        vehicle_damage_mapping = {'No':0,
                                  'Yes':1}

        df['vehicle_damage'] = df['vehicle_damage'].map(vehicle_damage_mapping)
        df['vehicle_damage_license'] = df.apply(lambda row: -(row['vehicle_damage'] + row['driving_license'])**2\
                                                 if row['driving_license'] == 0\
                                                 else (row['vehicle_damage'] + row['driving_license'])**2, axis=1)
        
        # vehicle_damage_vehicle_age
        df['vehicle_damage_vehicle_age'] = df.apply(lambda row: -(row['vehicle_damage'] + row['vehicle_age'])**2\
                                                    if row['vehicle_damage'] == 1\
                                                    else (row['vehicle_damage'] + row['vehicle_age'])**2, axis=1)

        # age / mean_age_by_region_code
        region_code_mean_age = pd.DataFrame(df.groupby('region_code')['age'].mean()).\
                                                    reset_index().rename(columns=
                                                                         {'age':'mean_age_by_region_code'})
        
        df = pd.merge(df, region_code_mean_age, how='left', on='region_code')
        df['age_mean_age_by_region_code'] = df['age'] / df['mean_age_by_region_code']


        # age / mean_age_by_policy_sales_channel
        policy_sales_channel_mean_age = pd.DataFrame(df.groupby('policy_sales_channel')['age'].mean()).\
                                                    reset_index().rename(columns=
                                                                         {'age':'mean_age_by_policy_sales_channel'})
        
        df = pd.merge(df, policy_sales_channel_mean_age, how='left', on='policy_sales_channel')
        df['age_mean_age_by_policy_sales_channel'] = df['age'] / df['mean_age_by_policy_sales_channel']


        # annual_premium / mean_annual_premium_by_region_code
        region_code_mean_annual_premium = pd.DataFrame(df.groupby('region_code')['annual_premium'].mean()).\
                                                    reset_index().rename(columns=
                                                                         {'annual_premium':'mean_annual_premium_by_region_code'})
        
        df = pd.merge(df, region_code_mean_annual_premium, how='left', on='region_code')
        df['annual_premium_mean_annual_premium_by_region_code'] = df['annual_premium'] / df['mean_annual_premium_by_region_code']


        # annual_premium / mean_annual_premium_by_policy_sales_channel
        policy_sales_channel_mean_annual_premium = pd.DataFrame(df.groupby('policy_sales_channel')['annual_premium'].mean()).\
                                               reset_index().rename(columns=
                                                                    {'annual_premium':'mean_annual_premium_by_policy_sales_channel'})
        
        df = pd.merge(df, policy_sales_channel_mean_annual_premium, how='left', on='policy_sales_channel')
        df['annual_premium_mean_annual_premium_by_policy_sales_channel'] = df['annual_premium'] /                             df['mean_annual_premium_by_policy_sales_channel']
        

        # age / vintage
        df['age_vintage'] = (df['age']*365) / df['vintage']

        
        return df
    
    
    
    
    def data_preparation(self, df):
        # age_stage encoder
        df['age_stage'] = self.age_stage_encoder.fit_transform(df['age_stage'])
        
        # gender encoder
        df['gender'] = df['gender'].apply(lambda row: 0 if row == 'Male' else 1)
        
        columns = ['previously_insured',
                   'vehicle_damage_license',
                   'vehicle_damage_vehicle_age',
                   'policy_sales_channel',
                   'region_code',
                   'vehicle_age',
                   'age_mean_age_by_region_code',
                   'age_mean_age_by_policy_sales_channel',
                   'annual_premium_mean_annual_premium_by_region_code',
                   'annual_premium_mean_annual_premium_by_policy_sales_channel',
                   'age_stage',
                   'vintage']
        
        return df[columns]
    
    
    
    
    def get_prediction(self, model, df, original_dataset):
        # Prediction
        yhat = model.predict(df)
        # Prediction Proba
        yhat_proba = model.predict_proba(df)[:,1]
        
        # Original dataset with predictions
        original_dataset['prediction'] = yhat
        original_dataset['prediction_probality'] = yhat_proba
        
        #sort original dataset by prediction_probality
        original_dataset = original_dataset.sort_values('prediction_probality', ascending=False)
        
        return original_dataset.to_json(orient='records', date_format='iso')