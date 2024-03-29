import plotly.graph_objects as go


map_colorbar = {'bgcolor': 'white',
                'orientation': 'v',
                'xanchor': 'center',
                'yanchor': 'middle',
                'tickmode': 'auto',
                'tickformat': ".0%",
                'ticks': 'outside',
                'tickfont': {'size': 13},
                'xpad': 20,
                'len': 0.7,
                'title': {'text': 'ЭB',
                          'font': {'size': 12}}}
map_colorscale = [(0, "#c4c4c4"), (0.25, "#c4c4c4"), (0.5, "#c4c4c4"),
                  (0.65, "#ff3333"), (0.85, "#ffff66"), (1, "#81c662")]


def plot_choropleth_map(borders, data, column_label, locations_label, title_text):
    map_figure = go.Figure(go.Choroplethmapbox(geojson=borders,
                                               locations=data[locations_label],
                                               featureidkey='properties.'+locations_label,
                                               z=data[column_label],
                                               zmax=1,
                                               zmin=-1,
                                               colorscale=map_colorscale,
                                               hovertemplate=' Субъект: %{location}<br> '
                                                             'ЭВ: %{z:.1%}<extra></extra>',
                                               colorbar=map_colorbar,
                                               hoverlabel={'font': {'size': 15},
                                                           'namelength': -1}))
    map_figure.update_layout(mapbox_style='white-bg',  # "white-bg",
                             autosize=True,
                             paper_bgcolor='white',
                             plot_bgcolor='white',
                             mapbox=dict(center=dict(lat=70, lon=105), zoom=1.6),
                             margin={"r": 0, "t": 120, "l": 0, "b": 0},
                             title={'text': title_text, 'font_color': 'black',
                                    'x': 0.5, 'y': 0.9, 'xanchor': 'center', 'yanchor': 'top'},
                             title_font_size=12)
    map_figure.update_geos(fitbounds="locations")
    return map_figure
