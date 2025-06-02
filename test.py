import pandas as pd
import json

def print_full(x):
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 2000)
    pd.set_option('display.float_format', '{:20,.2f}'.format)
    pd.set_option('display.max_colwidth', None)
    print(x)
    pd.reset_option('display.max_rows')
    pd.reset_option('display.max_columns')
    pd.reset_option('display.width')
    pd.reset_option('display.float_format')
    pd.reset_option('display.max_colwidth')

with open("scrape_results/VNM.json", "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)
groupedByDF = pd.to_datetime(df['date'], format="%d/%m/%Y").sort_values(ascending=True)
print_full(groupedByDF)