# pandas and numpy are only used here to read the excel file and fill in the missing half of the table
# the data is turned into a tuple of addresses and a list of tuples before it's returned,
# so the rest of the program only works with built-in python structures


import numpy as np
import pandas as pd

def load_distance_data():
	file_path = "./dataset/WGUPS_Distance_Table.xlsx"
	df = pd.read_excel(file_path, header=None)
	addresses = tuple(df.iloc[7, 2:])
	values = df.iloc[8:, 2:].to_numpy(float)
	values = np.where(np.isnan(values), values.T, values)
	matrix = [tuple(float(value) for value in row) for row in values]
	return addresses, matrix