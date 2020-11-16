import pandas as pd
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import json
from urllib.request import urlopen


app = dash.Dash(__name__)
pd.set_option('display.max_columns', None, 'display.max_rows', None)

token = 'pk.eyJ1IjoibGNpZXNsdWsiLCJhIjoiY2toNnM3MG9lMDBhNDJydDM4a3EwYnEyYiJ9.-6g_IQr9CFIe_Z7UtG_tkw'

pop = pd.read_excel('population.xlsx')
pop = pop.rename(columns = {'Powiat':'district','Powierzchnia [km²]': 'area of district','Liczba ludności [osoby]':'population' })

for i, p in enumerate(pop['district']):
	if p.split(' ')[0] != 'powiat':
		
		pop.at[i,'district'] = 'powiat ' + p

# pop['district'] = 'powiat '+ pop['district'].str.replace('m.st.','').str.strip().str.split('[',expand=True)[0]

# load geojson to use in Choropleth map
with open('poland', encoding = 'utf-8') as f:
	poland = json.load(f)

# dict with colors of background and text
colors = {
    'background': '#3D3A3E',
    'text': '#E1E1E7'
}

#------------------------------------------------------------------------------------
#add new columns
df = pd.read_json('otodom_full_data', orient = 'split')
df = df[df['price'] != 'Zapytajocenę']
df = df.reset_index()
df['price'] = df.price.astype(float)
df['area'] = df.area.astype(float)
df['price/m'] = df['price']/df['area']
df['counts'] = 0
df['population'] = '0'
df['area of district'] = '0'

#------------------------------------------------------------------------------------

for i, dis in enumerate(df['district']):

	if pop[pop['district'] == dis].empty == False:
		temp = pop[pop['district'] == dis]
		temp = temp.groupby(['district']).agg({'population': 'sum', 'area of district': 'sum'})
		temp = temp.reset_index()
		df.at[i,'population'] = temp.iloc[0]['population']
		df.at[i,'area of district'] = temp.iloc[0]['area of district']

# print(df.index[df['powiat aleksandrowski']].tolist())



#------------------------------------------------------------------------------------
#Group dataframe to use in graphs
df1 = df.groupby(['for rent/sale','district','population','area of district']).agg({'district':'count','price/m':'mean'})\
	.rename(columns={'district':'count','price/m':'mean price/m'})
df1 = df1.reset_index()


df3 = df.groupby(['district', 'for rent/sale'])['counts'].count()
df3 = df3.reset_index()

#------------------------------------------------------------------------------------
print(df1)

#------------------------------------------------------------------------------------
# Page html
app.layout = html.Div([
	
	html.Div([	
		html.H1('Real estate in Poland'),
		html.H4('Project by Łukasz Cieśluk')],
		className = 'banner'
		
	),

	html.Div(
	
		dcc.Dropdown(

			id = 'rent/sale',
			options = [
				{'label': 'rent', 'value': 'rent'},
				{'label': 'sale', 'value': 'sale'}],
			multi = False,
			value = 'sale',
			

		),className = 'dropdown'
	),
	html.Div([
		html.Div(

			dcc.Graph(id = 'map'),
			className = 'six columns box'
		),

		html.Div(

			dcc.Graph(id = 'graph'),
			className = 'six columns box'
		)],
		className = 'row'
	)

])
#------------------------------------------------------------------------------------


@app.callback(
    [Output(component_id='graph', component_property='figure'),
    Output(component_id = 'map', component_property = 'figure')],
    [Input(component_id='rent/sale', component_property='value')])


def update_graph(option_slctd):

	dff = df1.copy()
	dff = dff[dff['for rent/sale'] == option_slctd]

	dff3 = df3.copy()
	dff3 = dff3[dff3['for rent/sale'] == option_slctd]

	#------------------------------------------------------------------------------------
	# scatter graph
	fig = px.scatter(dff, x = 'count', y = 'mean price/m', color = 'population',
		log_x = True,
		log_y = True,
		size = 'area of district',
		hover_name = 'district',
		labels ={'count': 'number of apartments', 'area of district': 'area of district [km²]','mean price/m':'mean price/m [PLN]'})

	fig.update_layout(
		height = 900,
		plot_bgcolor=colors['background'],
		paper_bgcolor=colors['background'],
		font_color=colors['text']
	)
	#------------------------------------------------------------------------------------


	#------------------------------------------------------------------------------------
	# Map graph
	fig3 = px.choropleth_mapbox(
		dff3,
		geojson = poland,
		locations = 'district',
		color = 'counts',
		featureidkey='properties.nazwa',
		color_continuous_scale='Plasma',
		# range_color = (0,round(dff3['counts'].max(),-2)),
		zoom=5,
		center = {"lat": 52.1127, "lon": 19.2119},
		labels = {'counts': 'number of apartments'}
	)

	fig3.update_layout(mapbox_accesstoken=token,
		mapbox_style='mapbox://styles/lciesluk/ckh6savza1jn719qe0y5lzd4i',
		height = 900, margin = {'r':0, 'l':20, 't':20, 'b':20},
	    plot_bgcolor=colors['background'],
    	paper_bgcolor=colors['background'],
    	font_color=colors['text']
	)
	#------------------------------------------------------------------------------------

	return fig, fig3

if __name__ == '__main__':
	app.run_server(debug = True)