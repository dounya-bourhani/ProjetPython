from dash import Dash, html, dash_table, dcc
from dash.dependencies import Input, Output, State
import requests
import pandas as pd
import plotly.express as px



# Incorporate data

#importer des dataframe
import pickle


with open('dataframe.pkl', 'rb') as file:
    df = pickle.load(file)
    
with open('dataframe2.pkl', 'rb') as file:
    df2 = pickle.load(file)
    
with open('cartoM.pkl', 'rb') as file:
    cartoM = pickle.load(file)
    
#importer les modeles de classif et regerssion

with open('modele_classif.pkl', 'rb') as file:
    model_class = pickle.load(file)
    
with open('decision_tree_model.pkl', 'rb') as file:
    model_reg = pickle.load(file)
    
    

cartoM.drop(columns={'geometry'})


df = df.sample(frac=1, random_state=1).reset_index(drop=True)

df = df.head(2000)

df['Date mutation'] = pd.to_datetime(df['Date mutation'], dayfirst=True)

# Extrayez le mois de chaque date et créez une nouvelle colonne 'Mois'
df['Mois'] = df['Date mutation'].dt.month
df['annee'] = df['Date mutation'].dt.year

Local = list(df['Type local'].unique()) +['ALL']

annee = [2018, 2019, 2020, 2021] + ['ALL']


import geojson
with open("/Users/celia/Documents/GitHub/ProjetPython/departements-version-simplifiee.geojson") as f:
    carte_dep = geojson.load(f)
#graph = pd.DataFrame(df.groupby('Mois')['Valeur fonciere'].mean())

# Initialize the app
app = Dash(__name__)

###Layout STATS

tab1_layout = html.Div([
    html.H1('Statistiques', style={'textAlign': 'center'}),
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
    dcc.Graph(id='histogram',style={'display': 'inline-block'}),
    dcc.Graph(id='graphique2', style={'display': 'inline-block'}),
    dcc.Graph(id='graphique3'),  
    dcc.Graph(id='graphique4'),
    dcc.Graph(id='graphique5'),
    dash_table.DataTable(data=df.to_dict('records'), page_size=30)
    
])

###LAYOUT CARTO

tab2_layout = html.Div([
    html.H1('Carto',  style={'textAlign': 'center'}),
    #dcc.Graph(id='map'),
    dcc.Graph(id='graphique21'),
    dcc.Graph(figure= px.choropleth_mapbox(data_frame=cartoM,
        geojson= carte_dep,
        locations='code',  # Colonne contenant les codes des départements
        featureidkey="properties.code",  # Clé pour faire correspondre les données avec le fichier GeoJSON
        color='value',  # Colonne dont les valeurs seront utilisées pour la coloration
        # Vous pouvez ajuster la portée (par exemple, 'france' pour la France)
        center={"lat": 46.603354, "lon": 1.888334},  # Coordonnées géographiques du centre de la France
        title='Carte prix du m2 par département')),
    
])

###LAYOUT PRED

tab3_layout = html.Div([
    html.H1('Estimez votre bien :',  style={'textAlign': 'center'}),
    html.Br(),
    html.Br(),
    html.Label('Type local:'),
    dcc.Input(id='input-box-1', type='text', value=''),
    html.Label('Surface reelle bati en m2:'),
    dcc.Input(id='input-box-2', type='text', value=''),
    html.Label('Surface terrain en m2:'),
    dcc.Input(id='input-box-3', type='number', value=0),
    html.Label('Nombre de pièces :'),   
    dcc.Input(id='input-box-4', type='number', value=''),
    html.Label('Nombre de lots:'),   
    dcc.Input(id='input-box-5', type='number', value='1'),
    html.Br(),
    html.Br(),
    html.Button('Estimer', id='button', style= {'display': 'inline-block', 'width': '10%', 'borderWidth': '2px 2px 6px 2px'}),
    html.Br(),
    html.Br(),
    html.Div(id='output')
])

###LE MENU 

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
     Output('graphique5', 'figure'),
     Output('graphique21', 'figure'),
     #Output('map', 'figure'),
     Output('output', 'children')
    ],
    [Input('annee-dropdown', 'value'),
    Input('local-dropdown', 'value'),
    Input('button', 'n_clicks'),],
    [State('input-box-1', 'value'),
    State('input-box-2', 'value'),
    State('input-box-3', 'value'),
    State('input-box-4', 'value'),
    State('input-box-5', 'value')]
)

##
##
###UPDATE
##
##

def update_output(selected_year, selected_local, n_clicks,  L, SRB, ST, NbP, NbL):
    
    ##
    ### STATS 
    ##
    
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
    fig4 = px.histogram(filtered_data, x="Mois",y='Valeur fonciere', title=f'Nombre de Ventes par mois en {selected_year} {selected_local}', histfunc='count')
    fig5 = px.histogram(filtered_data, x="Mois",y='Valeur fonciere', title=f'Moyennes des prix de ventes par mois en {selected_year} {selected_local}', histfunc='avg')
    
    
    ##
    ### CARTOGRAPHIE 
    ##
    
    fig21 = px.histogram(cartoM, x="nom", y='value', title=f'Prix du m2 par departement').update_xaxes(categoryorder= "total descending")
    
    # carte = px.choropleth(data_frame=cartoM,
    #     geojson='departements-version-simplifiee.geojson',
    #     locations='nom',  # Colonne contenant les codes des départements
    #     featureidkey="properties.nom",  # Clé pour faire correspondre les données avec le fichier GeoJSON
    #     color='value',  # Colonne dont les valeurs seront utilisées pour la coloration
    #     # Vous pouvez ajuster la portée (par exemple, 'france' pour la France)
    #     center={"lat": 46.603354, "lon": 1.888334},  # Coordonnées géographiques du centre de la France
    #     title='Carte prix du m2 par département',
    # ) 

    # carte.update_geos(
    #     fitbounds="locations",
    #     visible=False,  # Masquer les frontières des pays ou des états, car vous affichez déjà les frontières des départements
    #     showland=True,  # Afficher les terres
    #     landcolor='rgb(217, 217, 217)',  # Couleur des terres
    #     showcoastlines=True,  # Afficher les lignes de côte
    #     coastlinecolor="RebeccaPurple",  # Couleur des lignes de côte
    #     showframe=False,  # Masquer le cadre
    #     projection_scale=3,  # Ajuster l'échelle de la projection pour agrandir ou réduire la carte
    #     lonaxis_range=[-20, 20],  # Plage de longitudes (ajuster selon vos besoins)
    #     lataxis_range=[30, 52]   # Plage de latitudes (ajuster selon vos besoins)
    # )
    
    ##
    ### PREDICTIONS
    ##
    
    texte = f''
    if n_clicks is None:
        texte = f'Cliquez sur le bouton pour prédire votre bien.'
    else:
        while SRB is None or SRB == 0 or NbP == 0 or NbP is None:
            texte = f'Veuillez remplir les chmaps manquant ou erreur d orthographe vérifier'
        if L not in {'Maison', 'Appartement', 'Dépendance', 'Local industriel. commercial ou assimilé'}:
            code_com = df["Code commune"].mean()
            classif = pd.DataFrame([[SRB, ST, NbP, NbL,  code_com]], columns=["Surface reelle bati", "Surface terrain", "Nombre pieces principales", "Nombre de lots","Code commune"])
            L = model_class.predict(classif)
            print(L)
            texte = f'Nous avons supposé que avez un(e) {L}'
        # Vous pouvez réutiliser les valeurs récupérées dans ces variables
        # Faites quelque chose avec ces variables ici, par exemple, imprimez-les
        moy_tc = df2["Moyenne Taux Chomage"].mean()
        m2 = df2["prix_par_m2"].mean()
        m2R = df2["moyenne_prix_par_m2_par_code_postal"].mean()
        if(L =='Maison'):
            TM = 1
            TA = 0
            TD = 0
            TZ = 0
        elif(L == 'Appartement'):
            TA = 1 
            TM = 0
            TD = 0
            TZ = 0
        elif(L == 'Dépendance'):
            TD = 1
            TA = 0
            TM = 0
            TZ = 0
        else :
            TZ = 1
            TA = 0
            TD = 0
            TM = 0  
        reg = pd.DataFrame([[NbP, SRB, ST, NbL, moy_tc,  m2, m2R, TA, TD, TZ, TM]], columns= ['Nombre pieces principales', 'Surface reelle bati', 'Surface terrain', 'Nombre de lots', 'Moyenne Taux Chomage',
                                                                                              'prix_par_m2', 'moyenne_prix_par_m2_par_code_postal','Type local_Appartement', 'Type local_Dépendance', 'Type local_Local industriel. commercial ou assimilé', 'Type local_Maison'])
                
        print("Valeur du premier champ :", L)
        print("ça marche ? ", TM)
        print("test ? ", TA)
        valeur = model_reg.predict(reg)
        # Retournez les valeurs pour les afficher dans l'interface utilisateur
        texte = texte + f'Votre bien est estimé à : "{valeur}" dans le deuxième champ.'

    return fig1, fig2, fig3, fig4, fig5, fig21, texte




# Run the app
if __name__ == '__main__':
    app.run(debug=True)