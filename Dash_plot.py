import pandas as pd
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import json
from urllib.request import urlopen


app = dash.Dash(__name__)


# pd.set_option('display.max_columns', None, 'display.max_rows', None)

# token to use map in dark mode
token = 'pk.eyJ1IjoibGNpZXNsdWsiLCJhIjoiY2toNnM3MG9lMDBhNDJydDM4a3EwYnEyYiJ9.-6g_IQr9CFIe_Z7UtG_tkw'

# open geojson with poland sistricts coordinates
with open('poland', encoding = 'utf-8') as f:
	poland = json.load(f)


# dict with colors of background and text
colors = {
    'background': '#1E1E23',
    'text': '#34B2D1'
}


# json file with all sraped data
df = pd.read_json('otodom_full_data', orient = 'split')


#------------------------------------------------------------------------------------
#Group dataframe to use in graphs
df1 = df.groupby(['for rent/sale','district','population','area of district']).agg({'district':'count','price/m':'mean'})\
	.rename(columns={'district':'count','price/m':'mean price/m'})
df1 = df1.reset_index()


df3 = df.groupby(['district', 'for rent/sale'])['counts'].count()
df3 = df3.reset_index()

#------------------------------------------------------------------------------------
# print(df1)

#------------------------------------------------------------------------------------
# Page html
app.layout = html.Div([
	
	html.Div([	
		html.H1('Real estate in Poland'),
		html.H4('Project by Łukasz Cieśluk')],
		className = 'banner'
		
	),
	html.Div([
		html.Div([

			html.P('Choose whether you want to view properties for sale or rent'),

			dcc.Dropdown(

				id = 'rent/sale',
				options = [
					{'label': 'rent', 'value': 'rent'},
					{'label': 'sale', 'value': 'sale'}],
				multi = False,
				value = 'sale'

			)],
			className = 'slider'
		),
		html.Div([
			html.Div([

				dcc.Graph(id = 'map'),
				html.A("Geojson by 'ppatrzyk'" ,href ="https://github.com/ppatrzyk/polska-geojson", target='_blank')],
				className = 'six columns box left'
			),

			html.Div([

				dcc.Graph(id = 'graph'),
				html.P('Size = area of district')],
				className = 'six columns box'
			)],
			className = 'row'
		)
	],className = 'big_box')

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
		zoom=5.5,
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