import pandas as pd
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import json
from urllib.request import urlopen

app = dash.Dash(__name__)


# load geojson to use in Choropleth map
with urlopen('https://raw.githubusercontent.com/ppatrzyk/polska-geojson/master/powiaty/powiaty-max.geojson') as response:
    poland = json.load(response)

districts = pd.read_excel('districts.xlsx')
districts = districts.drop(columns = ['Gmina', 'Województwo',
 'Identyfikator miejscowości z krajowego rejestru urzędowego podziału terytorialnego kraju TERYT','Dopełniacz','Przymiotnik'])


#------------------------------------------------------------------------------------
#add new columns
df = pd.read_json('otodom_full_data', orient = 'split')
df = df[df['price'] != 'Zapytajocenę']
df['price'] = df.price.astype(float)
df['area'] = df.area.astype(float)
df['price/m'] = df['price']/df['area']
df['counts'] = 0
df['district'] = '0'
#------------------------------------------------------------------------------------

temp =[]
for i,city in enumerate(df['localization']):

	if districts.loc[(districts['Nazwa miejscowości '] == city) & (districts['Rodzaj'] == 'miasto')].empty ==  False:
		d = districts.loc[(districts['Nazwa miejscowości '] == city) & (districts['Rodzaj'] == 'miasto')]
		# print(i)
		# print(d)
		temp.append(d.iloc[0]['Powiat (miasto na prawach powiatu)'])
	elif districts.loc[(districts['Nazwa miejscowości '] == city) & (districts['Rodzaj'] == 'wieś')].empty ==  False:
		# print(i)
		# print(d)
		temp.append(d.iloc[0]['Powiat (miasto na prawach powiatu)'])
	elif districts.loc[(districts['Nazwa miejscowości '] == city) & (districts['Rodzaj'] == 'osada')].empty ==  False:
		temp.append(d.iloc[0]['Powiat (miasto na prawach powiatu)'])
	elif districts.loc[(districts['Nazwa miejscowości '] == city) & (districts['Rodzaj'] == 'kolonia')].empty ==  False:
		temp.append(d.iloc[0]['Powiat (miasto na prawach powiatu)'])
	elif city == 'Stargard':
		temp.append('stargardzki')
	else:
		print(city)


#------------------------------------------------------------------------------------
#Group dataframe to use in graphs
df1 = df.groupby(['localization','for rent/sale'])['price/m'].mean()
df1 = df1.reset_index()

df2 = df.groupby(['localization', 'for rent/sale'])['counts'].count()
df2 = df2.reset_index()
#------------------------------------------------------------------------------------


#------------------------------------------------------------------------------------
# Page html
app.layout = html.Div([

	html.H1('Otodom data analyze', style = {'text-align': 'center'}),

	dcc.Dropdown(id = 'rent/sale',
		options = [
			{'label': 'rent', 'value': 'rent'},
			{'label': 'sale', 'value': 'sale'}],
		multi = False,
		value = 'sale',
		style = {'width': '40%'}),

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
	fig3 = px.choropleth_mapbox(dff2, geojson = poland)


	return fig, fig2

if __name__ == '__main__':
	app.run_server(debug = True)