from dash import Dash, html, dash_table, dcc
from dash.dependencies import Input, Output, State
import folium 
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


df = df.sample(frac=1, random_state=1).reset_index(drop=True)

df = df.head(5000)

df['Date mutation'] = pd.to_datetime(df['Date mutation'], dayfirst=True)

# Extrayez le mois de chaque date et créez une nouvelle colonne 'Mois'
df['Mois'] = df['Date mutation'].dt.month
df['annee'] = df['Date mutation'].dt.year

Local = list(df['Type local'].unique()) +['ALL']

annee = [2018, 2019, 2020, 2021] + ['ALL']

# Initialize the app
app = Dash(__name__)


tab1_layout = html.Div([
    html.H1('Statistiques'),
    html.Div(children='Petit tour sur nos données'),
    html.Label('Sélectionnez une année :', style= {'display': 'inline-block', 'marginRight': '20px'}),
    dcc.Dropdown(
        id='annee-dropdown',
        options=[{'label': str(anne), 'value': anne} for anne in annee],
        value='ALL',
        style= {'display': 'inline-block', 'width': '25%'}
    ),
    html.Label('Sélectionnez une Type de bien :', style={'display': 'inline-block', 'marginRight': '20px'}),
    dcc.Dropdown(
        id='local-dropdown',
        options=[{'label': str(l), 'value': l} for l in Local],
        value='ALL',
        style= {'display': 'inline-block', 'width': '35%'}
    ),
    html.Div(id='output-container'),
    dcc.Graph(id='histogram',style={'display': 'inline-block', 'width': '50%'}),
    dcc.Graph(id='graphique2', style={'display': 'inline-block', 'width': '50%'}),
    dcc.Graph(id='graphique3'),  
    dcc.Graph(id='graphique4') ,
    dash_table.DataTable(data=df.to_dict('records'), page_size=30)
])

tab2_layout = html.Div([
    html.H1('Carto'),
    dcc.Graph(id='graphique21'),
    dcc.Graph(id='map')  
])

tab3_layout = html.Div([
    html.H1('Prédire votre bien :'),
    html.Label('Nombre de pièces principales:'),
    dcc.Input(id='input-box-1', type='number', value=''),
    html.Label('Type local:'),
    dcc.Input(id='input-box-2', type='text', value=''),
    html.Label('Surface en m2:'),
    dcc.Input(id='input-box-3', type='number', value=0), 
    html.Button('OK', id='button'),
    html.Div(id='output')
])


# App layout
app.layout = html.Div([
     dcc.Tabs([
        dcc.Tab(label='Statistiques', children=tab1_layout),
        dcc.Tab(label='Cartographie', children=tab2_layout),
        dcc.Tab(label='Prédictions', children=tab3_layout),
    ])
])

@app.callback(
    [Output('histogram', 'figure'),
     Output('graphique2', 'figure'),
     Output('graphique3', 'figure'),
     Output('graphique4', 'figure'),
     Output('graphique21', 'figure'),
     Output('map', 'figure'),
     Output('output', 'children')
    ],
    [Input('annee-dropdown', 'value'),
    Input('local-dropdown', 'value'),
    Input('button', 'n_clicks'),],
    [State('input-box-1', 'value'),
    State('input-box-2', 'value'),
    State('input-box-3', 'value')]
)


def update_output(selected_year, selected_local, n_clicks,  input1, input2, input3):
    
    if (selected_local == 'ALL' and selected_year == 'ALL'):
        filtered_data = df
    
    if selected_local != 'ALL':
        filtered_data = df[df['Type local'] == selected_local]
    elif selected_year != 'ALL':   
        filtered_data = df[df['annee'] == selected_year]
        
    
    # Créer les graphiques en utilisant les données filtrées
    fig1 = px.histogram(filtered_data, x='Type local', y='Valeur fonciere', histfunc='avg', title=f'Histogram Moyenne des prix des biens par type de local en {selected_year} {selected_local}', color="Type local")
    fig2 = px.histogram(filtered_data, x='Type local', y='Surface terrain', histfunc='avg', title=f'Moyenne des surfaces des biens par type de local en {selected_year} {selected_local}', color="Type local")
    fig3 = px.scatter(filtered_data, x='Commune', y="Valeur fonciere", title=f'Prix des biens dans les communes en {selected_year} {selected_local}')
    fig4 = px.histogram(filtered_data, x="Mois",y='Valeur fonciere', title=f'Ventes par mois en {selected_year} {selected_local}', histfunc='count')
    
    fig21 = px.histogram(cartoM, x="nom", y='value', title=f'Prix du m2 par departement').update_xaxes(categoryorder= "total descending")
    
    carte = px.choropleth_mapbox(data_frame=cartoM,
        geojson='departements-version-simplifiee.geojson',
        locations='nom',  # Colonne contenant les codes des départements
        featureidkey="properties.nom",  # Clé pour faire correspondre les données avec le fichier GeoJSON
        color='value',  # Colonne dont les valeurs seront utilisées pour la coloration
        # Vous pouvez ajuster la portée (par exemple, 'france' pour la France)
        center={"lat": 46.603354, "lon": 1.888334},  # Coordonnées géographiques du centre de la France
        title='Carte prix du m2 par département',
    ) 

    carte.update_geos(
        visible=False,  # Masquer les frontières des pays ou des états, car vous affichez déjà les frontières des départements
        showland=True,  # Afficher les terres
        landcolor='rgb(217, 217, 217)',  # Couleur des terres
        showcoastlines=True,  # Afficher les lignes de côte
        coastlinecolor="RebeccaPurple",  # Couleur des lignes de côte
        showframe=False,  # Masquer le cadre
        projection_scale=3,  # Ajuster l'échelle de la projection pour agrandir ou réduire la carte
        lonaxis_range=[-20, 20],  # Plage de longitudes (ajuster selon vos besoins)
        lataxis_range=[30, 52]   # Plage de latitudes (ajuster selon vos besoins)
    )

   
    
    if n_clicks is None:
        texte = 'Cliquez sur le bouton pour prédire votre bien.'
    else:
        if input3 is None or input3 == 0:
            texte = 'Veuillez remplir les chmaps manquant'
        else:
        # Vous pouvez réutiliser les valeurs récupérées dans ces variables
        # Faites quelque chose avec ces variables ici, par exemple, imprimez-les
            print("Valeur du premier champ :", input1)
            print("Valeur du deuxième champ :", input2)
            print("Valeur du deuxième champ :", input3)
            # Retournez les valeurs pour les afficher dans l'interface utilisateur
            texte = f'Vous avez entré : "{input1}" dans le premier champ et "{input2}" dans le deuxième champ.'
    
    return fig1, fig2, fig3, fig4, carte, fig21, texte




# Run the app
if __name__ == '__main__':
    app.run(debug=True)