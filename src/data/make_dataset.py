import os
import zipfile
import pandas as pd

from sqlalchemy                     import create_engine
from kaggle.api.kaggle_api_extended import KaggleApi


class Dataset(object):
	def __init__(self):
		self.host     = os.environ.get('POSTGRES_CDS_HOST')
		self.usenamer = os.environ.get('POSTGRES_CDS_USERNAME')
		self.password = os.environ.get('POSTGRES_CDS_PASSWORD')
		self.port     = os.environ.get('POSTGRES_CDS_PORT')
		self.database = os.environ.get('POSTGRES_CDS_DATABASE')

		self.api      = KaggleApi()

	def create_engine(self):
		engine = create_engine(f"postgresql://{self.usenamer}:{self.password}@{self.host}:{self.port}/{self.database}")
		return engine


	def get_train_data(self, path='../../query/raw_data.sql'):
		with open(path, mode='r', encoding='utf-8-sig') as query:
			query_raw_data = query.read()

		with Dataset.create_engine(self).connect() as conn:
			df_train = pd.read_sql(query_raw_data, conn)

		return df_train

	def get_test_data(self, path='../../zip'):		
		self.api.authenticate()

		self.api.dataset_download_file(dataset='anmolkumar/health-insurance-cross-sell-prediction',
								   		file_name='test.csv', path=path)

		with zipfile.ZipFile(path + '/test.csv.zip','r') as zipref:
			zipref.extractall(path=path[:-3] + 'data/raw')

