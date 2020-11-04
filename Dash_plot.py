import pandas as pd
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import json
from urllib.request import urlopen

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets = external_stylesheets)


# load geojson to use in Choropleth map
with urlopen('https://raw.githubusercontent.com/ppatrzyk/polska-geojson/master/powiaty/powiaty-max.geojson') as response:
    poland = json.load(response)    

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}
#------------------------------------------------------------------------------------
#add new columns
df = pd.read_json('otodom_full_data', orient = 'split')
df = df[df['price'] != 'Zapytajocenę']
df['price'] = df.price.astype(float)
df['area'] = df.area.astype(float)
df['price/m'] = df['price']/df['area']
df['counts'] = 0

#------------------------------------------------------------------------------------


#------------------------------------------------------------------------------------
#Group dataframe to use in graphs
df1 = df.groupby(['localization','for rent/sale'])['price/m'].mean()
df1 = df1.reset_index()

df2 = df.groupby(['localization', 'for rent/sale'])['counts'].count()
df2 = df2.reset_index()

df3 = df.groupby(['district', 'for rent/sale'])['counts'].count()
df3 = df3.reset_index()

#------------------------------------------------------------------------------------


#------------------------------------------------------------------------------------
# Page html
app.layout = html.Div(style = {'backgroundColor': colors['background']},
	children = [html.H1('Otodom data analyze', style = {'text-align': 'center', 'color':colors['text']}),
	dcc.Dropdown(id = 'rent/sale',
		options = [
			{'label': 'rent', 'value': 'rent'},
			{'label': 'sale', 'value': 'sale'}],
		multi = False,
		value = 'sale',
		style = {'width': '40%'}),

	html.Div(
		children = dcc.Graph(id = 'map', style = {"display": "block", "margin-left": "auto","margin-right": "auto"}),
		className = 'six columns'
		),

	dcc.Graph(id = 'graph'),

	dcc.Graph(id = 'count_city')

])
#------------------------------------------------------------------------------------


@app.callback(
    [Output(component_id='graph', component_property='figure'),
    Output(component_id = 'count_city', component_property = 'figure'),
    Output(component_id = 'map', component_property = 'figure')],
    [Input(component_id='rent/sale', component_property='value')])


def update_graph(option_slctd):

	dff = df1.copy()
	dff = dff[dff['for rent/sale'] == option_slctd]

	dff2 = df2.copy()
	dff2 = dff2[dff2['for rent/sale'] == option_slctd]

	dff3 = df3.copy()
	dff3 = dff3[dff3['for rent/sale'] == option_slctd]

	#------------------------------------------------------------------------------------
	# Bar Graphs
	fig = px.bar(dff, x = 'localization', y = 'price/m', text = 'price/m', labels={'price/m':'price/m [PLN]'})
	fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
	fig.update_layout(uniformtext_minsize=4, uniformtext_mode='hide')


	fig2 = px.bar(dff2, x = 'localization', y = 'counts',text = 'counts', labels ={'counts': 'number of apartments'})
	fig2.update_traces(textposition='outside')
	fig2.update_layout(uniformtext_minsize=4, uniformtext_mode='hide')
	#------------------------------------------------------------------------------------


	#------------------------------------------------------------------------------------
	# Map graph
	fig3 = px.choropleth_mapbox(dff3,
		geojson = poland,
		locations = 'district',
		color = 'counts',
		featureidkey='properties.nazwa',
		mapbox_style="carto-positron",
		color_continuous_scale="Viridis",
		range_color = (0,round(dff3['counts'].max(),-2)),
		zoom=6,
		center = {"lat": 52.1127, "lon": 19.2119},
		labels = {'counts': 'number of apartments'}
		)

	fig3.update_layout(width =1100, height = 900, margin = {'r':20, 'l':20, 't':20, 'b':20},
		plot_bgcolor = colors['background'],paper_bgcolor = colors['background'], font_color = colors['text'])
	

	return fig, fig2, fig3

if __name__ == '__main__':
	app.run_server(debug = True)