from dash import Dash, html, dash_table, dcc
import pandas as pd
import plotly.express as px
import dash_leaflet as dl
import plotly.io as pio

# Incorporate data
import pickle

with open('dataframe.pkl', 'rb') as file:
    df = pickle.load(file)
    
with open('cartoM.pkl', 'rb') as file:
    cartoM = pickle.load(file)

df = df.head(5000)

df['Date mutation'] = pd.to_datetime(df['Date mutation'], dayfirst=True)

# Extrayez le mois de chaque date et créez une nouvelle colonne 'Mois'
df['Mois'] = df['Date mutation'].dt.month

#figure1 = px.histogram(df, x='Type local', y='Valeur fonciere', histfunc='avg', title='Moyenne des prix des biens par type')

# Initialize the app
app = Dash(__name__)

tab1_layout = html.Div([
    html.H1('Statistiques'),
    html.Div(children='Petit tour sur nos données'),
    dash_table.DataTable(data=df.to_dict('records'), page_size=10),
    dcc.Graph(figure=px.histogram(df, x='Type local', y='Valeur fonciere', histfunc='avg', title='Moyenne des prix des biens par type'), style={'display': 'inline-block', 'width': '50%'}, id='Graph_moyennes_valeurs'),
    #pio.write_image(figure1, 'graph_export.png'), 
    dcc.Graph(figure=px.scatter(df, x='Commune', y="Valeur fonciere", title='Prix des biens dans les communes')),
    dcc.Graph(figure=px.histogram(df, x="Mois",y='Valeur fonciere', title='Ventes par mois', histfunc='count'))
])

tab2_layout = html.Div([
    html.H1('Carto'),
    #dcc.Graph(figure=cartoM)
])

tab3_layout = html.Div([
    html.H1('Contenu de l\'onglet 3'),
    # Ajouter du contenu spécifique à l'onglet 2 ici
])


# App layout
app.layout = html.Div([
     dcc.Tabs([
        dcc.Tab(label='Statistiques', children=tab1_layout),
        dcc.Tab(label='Cartographie', children=tab2_layout),
        dcc.Tab(label='Prédictions', children=tab3_layout),
    ])
])

# Run the app
if __name__ == '__main__':
    app.run(debug=True)