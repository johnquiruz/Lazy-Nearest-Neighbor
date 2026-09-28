import numpy as np
import pandas as pd


def _clean_address(address):
	cleaned = " ".join(str(address).replace("\n", " ").split()).lower()
	return cleaned.replace(" station ", " sta ")


def load_distance_data():
	file_path = "./dataset/WGUPS_Distance_Table.xlsx"
	df = pd.read_excel(file_path, header=None)
	addresses = tuple(df.iloc[7, 2:])
	values = df.iloc[8:, 2:].to_numpy(float)
	values = np.where(np.isnan(values), values.T, values)
	matrix = [tuple(float(value) for value in row) for row in values]
	return addresses, matrix