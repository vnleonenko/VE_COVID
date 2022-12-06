from dash import Dash, Output, Input, dcc
import dash_leaflet as dl
from dash import html
import pandas as pd
from copy import deepcopy


def calc_virus_ratio(virus_titles: list):
    virus_types_ratio = {}
    for title in virus_titles:
        if title in list(virus_types_ratio.keys()):
            virus_types_ratio[title] += 1
        else:
            virus_types_ratio[title] = 1
    virus_types_ratio = {k: round(v / len(virus_titles), 5) for k, v in virus_types_ratio.items()}
    return virus_types_ratio


def get_strain_data(csv_path):
    strain_data = pd.read_csv(csv_path)
    filtered_data = strain_data.loc[:, ['location', 'collection_date',
                                 'pango_lineage', 'pangolin_version', 'variant',
                                 'latitude', 'longitude', 'city', 'subject', 'district']]

    filtered_data['collection_date'] = filtered_data['collection_date'].map(lambda x: x.rsplit('-', 1)[0])
    grouped_data = filtered_data.groupby(['collection_date', 'city',
                                          'subject', 'district']).agg({'location': lambda x: x.iloc[0],
                                                                       'pango_lineage': lambda x: list(x),
                                                                       'pangolin_version': lambda x: list(x),
                                                                       'variant': lambda x: x.iloc[0],
                                                                       'latitude': lambda x: x.iloc[0],
                                                                       'longitude': lambda x: x.iloc[0]})
    grouped_data.reset_index(inplace=True)
    grouped_data['pango_lineage'] = grouped_data['pango_lineage'].apply(calc_virus_ratio)
    grouped_data['pangolin_version'] = grouped_data['pangolin_version'].apply(calc_virus_ratio)
    return grouped_data


app = Dash(__name__)
csv_path = 'app/data/strains/20221020-MH93845-490.csv'
data = get_strain_data(csv_path)
data = data.query('collection_date == "2020-09"')

lats = data['latitude']
longs = data['longitude']

pie_charts = [dl.Minichart(lat=lat, lon=long, type="pie", id=f"pie-{i + 1}", width=20)
              for i, (lat, long) in enumerate(zip(lats, longs))]
outputs = [[Output(f"pie-{i + 1}", "data")] for i in range(len(pie_charts))]

tile_layer = dl.TileLayer(
url='http://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}'
)
data_dict = data.to_dict('records')
app.layout = html.Div([
    dcc.Store('shared-data', storage_type='session'),
    dl.Map([tile_layer,
            *pie_charts,
            html.Div(4, id="trigger")],
           zoom=2.5,
           center=[70, 105],
           style={'width': '70vw',
                  'height': '70vh'})])


@app.callback(
    Output('shared-data', 'data'),
    Input('trigger', 'children')
)
def update_storage(_):
    temp_data = deepcopy(data.query('collection_date == "2020-09"')).to_dict('records')
    print(temp_data)
    return temp_data


app.clientside_callback("""
function(data){  
    const virus_ratio = []
    for (let i of data){
    virus_ratio.push(Object.values(i.pango_lineage))
    }
    console.log(virus_ratio)    
    return virus_ratio
}
""", *outputs, Input("shared-data", "data"))

app.run_server(debug=True)
