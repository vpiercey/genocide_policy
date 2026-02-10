import pandas
import os

_filename = os.path.join('..', 'data', 'ewp_final_excel_2024_06_25.csv')
df = pandas.read_csv(_filename)

