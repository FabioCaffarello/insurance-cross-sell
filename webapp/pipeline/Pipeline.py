import bisect
import inflection

import pandas as pd
import joblib as jb


class Pipeline(object):
    def __init(self):
        age_scaler                = jb.load(open('../parameters/scalers/age.pkl.z', 'rb'))
        fe_age_stage              = jb.load(open('../parameters/encoders/fe_age_stage.pkl.z', 'rb'))
        vintage_scaler            = jb.load(open('../parameters/scalers/vintage.pkl.z', 'rb'))
        target_encode_gender      = jb.load(open('../parameters/encoders/target_encode_gender.pkl.z', 'rb'))
        annual_premium_scaler     = jb.load(open('../parameters/scalers/annual_premium.pkl.z', 'rb'))
        fe_policy_sales_channel   = jb.load(open('../parameters/encoders/fe_policy_sales_channel.pkl.z', 'rb'))
        target_encode_region_code = jb.load(open('../parameters/encoders/target_encode_region_code.pkl.z', 'rb'))



    def rename_columns(self, df):
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



    def data_cleaning(self, df):

        # rename dataset (snake_case)
        df = Pipeline.rename_columns(self, df)

        return df


    #============================================ Feature engineering ============================================#
    def feature_engineering(self, df):
        df1 = df.copy()
        # Vehicle Damage Number
        df1['vehicle_damage'] = df1['vehicle_damage'].apply(lambda x: 1 if x == 'Yes' else 0)

        # Vehicle Age
        df1['vehicle_age'] =  df1['vehicle_age'].apply(lambda x: 'over_2_years' if x == '> 2 Years' else 'between_1_2_year' if x == '1-2 Year' else 'below_1_year')

        # Age Stage
        df1['age_stage'] = df1['age'].apply(lambda row: Pipeline.age_stage(self, row))

        return df1


    #============================================== Data Preparation ==============================================#

    def data_preparation(self, df1):
        df2 = df1.copy()
        # age
        df2.loc[:, 'age'] = age_scaler.transform(df2[['age']].values)

        # age_stage
        df2.loc[:, 'age_stage'] = df2['age_stage'].map(fe_age_stage)

        # vintage
        df2.loc[:, 'vintage'] = vintage_scaler.transform(df2[['vintage']].values)

        # gender
        df2.loc[:, 'gender'] =  df2.loc[:, 'gender'].map(target_encode_gender)

        # annual_premium
        df2.loc[:, 'annual_premium'] = annual_premium_scaler.transform(df2[['annual_premium']].values)

        # policy_sales_channel
        df2.loc[:, 'policy_sales_channel'] = df2['policy_sales_channel'].map(fe_policy_sales_channel)

        # region_code
        df2.loc[:, 'region_code'] = df2.loc[:, 'region_code'].map(target_encode_region_code)

        # vehicle_age
        df2 = pd.get_dummies(df2, prefix='vehicle_age', columns=['vehicle_age'])

        # fillna
        df2 = df2.fillna(0)

        cols_selected = ['gender',
                         #'age',
                         'region_code',
                         'policy_sales_channel',
                         'vehicle_damage',
                         'previously_insured',
                         'annual_premium',
                         'vintage',
                         'age_stage',
                         'vehicle_age_below_1_year',
                         'vehicle_age_between_1_2_year']

        return df2[cols_selected]


    def predict(self, model, df3, real_data):

        predict_proba = model.predict_proba(df3)

        real_data['probality_prediction'] = predict_proba[:,1]

        real_data = real_data.sort_values('probality_prediction', ascending=False)

        return real_data