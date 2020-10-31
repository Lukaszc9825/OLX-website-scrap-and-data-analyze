import pandas as pd
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

df = pd.read_json('otodom_full_data', orient = 'split')

df_temp = df.copy()
df['price'] = df['price'].str.replace('zł', '').str.replace(',', '.').str.replace(' ','').str.replace('~','')
df['area'] = df['area'].str.replace('m²', '').str.replace(',','.').str.replace(' ','')
df['localization'] = df_temp['localization'].str.split(',',expand = True)[0]
df['localization 1'] = df_temp['localization'].str.split(',',expand = True)[1]
df['localization 2'] = df_temp['localization'].str.split(',',expand = True)[2]
df['price'] = df.price.astype(float)
df['area'] = df.area.astype(float)
df['price/m'] = df['price']/df['area']
df = df.groupby(['localization'])[['price/m']].mean()
df.reset_index(inplace = True)

fig = px.bar(
	df,
	x = 'localization',
	y = 'price/m'
)

app.layout = html.Div([

	html.H1('Otodom data analyze', style = {'text-align': 'center'}),


	dcc.Graph(id = 'graph', figure = fig)

])


if __name__ == '__main__':
	app.run_server(debug = True)