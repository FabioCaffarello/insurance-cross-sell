import os

import joblib as jb
import pandas as pd

from pipeline.Pipeline import Pipeline
from flask import Flask, request, Response


# Loding Model
model = jb.load(open('../models/cat_tuned.pkl.z', 'rb'))

# Initialize API
app = Flask(__name__)

@app.route('/insurance-cross-sell/predict', methods=['POST'])
def insurance_cross_sell_prediction():
    test_json = request.get_json()
    
    if test_json: #there is data
        if isinstance(test_json, dict):
            teste_raw = pd.DataFrame(test_json, index=[0]) #unique example
        else:
            teste_raw = pd.DataFrame(test_json, columns=test_json[0].keys()) #multiple examples

		# Instantiate
        pipeline = Pipeline()

        # Data Cleaning
        df1 = pipeline.data_cleaning(teste_raw)
        # Feature Engineering
        df2 = pipeline.feature_engineering(df1)
        # Data Preparation
        df3 = pipeline.data_preparation(df2)
        # Prediction
        df_response = pipeline.predict(model, df3, teste_raw)
        
        return df_response
    
    else:
        return Response('{}', status=200, mimetype='application/json')

if __name__ == '__main__':
    port = os.environ.get('PORT', 5000)
    #app.run(host='0.0.0.0', port=port)
    app.run(host='localhost', port=port)