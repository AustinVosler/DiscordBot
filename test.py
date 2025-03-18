import pandas as pd

FILE_PATH = "TestSheet.xlsx"

df = pd.read_excel(FILE_PATH, "Sheet1")

print(df.iloc[0])