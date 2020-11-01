import pandas as pd
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

df = pd.read_json('otodom_full_data', orient = 'split')
df = df[df['price'] != 'Zapytajocenę']
df['price'] = df.price.astype(float)
df['area'] = df.area.astype(float)
df['price/m'] = df['price']/df['area']
df = df.groupby(['localization','for rent/sale'])[['price/m']].mean()
df.reset_index(inplace = True)

app.layout = html.Div([

	html.H1('Otodom data analyze', style = {'text-align': 'center'}),

	dcc.Dropdown(id = 'rent/sale',
		options = [
			{'label': 'rent', 'value': 'rent'},
			{'label': 'sale', 'value': 'sale'}],
		multi = False,
		value = 'sale',
		style = {'width': '40%'}),

	dcc.Graph(id = 'graph')

])

@app.callback(
    Output(component_id='graph', component_property='figure'),
    [Input(component_id='rent/sale', component_property='value')])


def update_graph(option_slctd):

	dff = df.copy()
	dff = dff[dff['for rent/sale'] == option_slctd]

	# Plotly Express
	fig = px.bar(dff, x = 'localization', y = 'price/m')

	return fig

if __name__ == '__main__':
	app.run_server(debug = True)