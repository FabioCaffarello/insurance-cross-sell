import os
import joblib as jb
import pandas as pd

from flask import Flask, request, Response

from pipeline.Pipeline import insuranse_cross_sell



model = jb.load(open('model/model_xgb.pkl.z', 'rb'))



# Initialize API
app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def youtubePredict():
    test_JSON = request.get_json()

    if test_JSON: #there is data
        if isinstance(test_JSON, dict):
            df = pd.DataFrame(test_JSON, index=[0]) #unique example
        else:
            df = pd.DataFrame(test_JSON, columns=test_JSON[0].keys()) #multiple examples

        # Instantiate
        pipeline = insuranse_cross_sell()

        # Data Cleaning
        df01 = pipeline.data_cleaning(df)
        # Feature Engineering
        df02 = pipeline.feature_engineering(df01)
        # Data Preparation
        df03 = pipeline.data_preparation(df02)
        # Prediction
        df_response = pipeline.get_prediction(model, df03, df)

        return df_response

    else:
        return Response('{}', status=200, mimetype='application/json')


if __name__ == '__main__':
    port = os.environ.get( 'PORT', 5000)
    #app.run(host='localhost', port=port)
    app.run(host='0.0.0.0', port=port)
