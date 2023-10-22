from dash import Dash, html, dash_table, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import pandas as pd
import plotly.express as px
import json



# Incorporate data

#importer des dataframe
# with open('dataframe.pkl', 'rb') as file:
#     df = pickle.load(file)
    
# with open('dataframe2.pkl', 'rb') as file:
#     df2 = pickle.load(file)
    
# with open('cartoM.pkl', 'rb') as file:
#     cartoM = pickle.load(file)

import pickle
import requests
import joblib
    
url_dataframe = 'https://github.com/dounya-bourhani/ProjetPython/blob/main/dataframe_sample.pkl?raw=true'
url_dataframe2 = 'https://github.com/dounya-bourhani/ProjetPython/blob/main/dataframe2_sample.pkl?raw=true'
url_cartoM = 'https://github.com/dounya-bourhani/ProjetPython/blob/main/cartoM.pkl?raw=true'

response_dataframe = requests.get(url_dataframe,verify=False)
response_dataframe2 = requests.get(url_dataframe2,verify=False)
response_cartoM = requests.get(url_cartoM,verify=False)

with open('dataframe_sample.pkl', 'wb') as f:
    f.write(response_dataframe.content)
with open('dataframe2_sample.pkl', 'wb') as f:
    f.write(response_dataframe2.content)
with open('cartoM.pkl', 'wb') as f:
    f.write(response_cartoM.content)

df = joblib.load('dataframe_sample.pkl')
df2 = joblib.load('dataframe2_sample.pkl')
cartoM = joblib.load('cartoM.pkl')

#importer les modeles de classif et regerssion

url_model_class = 'https://github.com/dounya-bourhani/ProjetPython/blob/main/modele_classif.pkl'
response_model_clas = requests.get(url_model_class,verify=False)
with open('modele_classif.pkl', 'wb') as f:
    f.write(response_model_clas.content)
model_class = joblib.load('modele_classif.pkl')

# with open('modele_classif.pkl', 'rb') as file:
#     model_class = pickle.load(file)
            
    
    

cartoM.drop(columns={'geometry'})

carto2 = df2[['Code postal', 'moyenne_prix_par_m2_par_code_postal', 'Moyenne Taux Chomage']]
carto2 = carto2.drop_duplicates(subset='Code postal')

df = df.sample(frac=1, random_state=1).reset_index(drop=True)

df = df.head(8000)

df['Date mutation'] = pd.to_datetime(df['Date mutation'], dayfirst=True)

# Extrayez le mois de chaque date et créez une nouvelle colonne 'Mois'
df['Mois'] = df['Date mutation'].dt.month
df['annee'] = df['Date mutation'].dt.year

Local = list(df['Type local'].unique()) +['ALL']

annee = [2018, 2019, 2020, 2021] + ['ALL']


import geojson
with open('/Users/celia/Documents/GitHub/ProjetPython/departements-version-simplifiee.geojson', 'r') as geojson_file:
    geojson_data = json.load(geojson_file)
    
#graph = pd.DataFrame(df.groupby('Mois')['Valeur fonciere'].mean())



load_figure_template("pulse")

# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.PULSE])

# Pour le déploiement de l'app
server = app.server


###Layout STATS

tab1_layout = html.Div([
    html.Br(),
    html.H1('Statistiques', style={'textAlign': 'center'}),
    html.Br(),
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
    dcc.Graph(id='graphique6'),
    dcc.Graph(id='graphique7'),
    dcc.Graph(id='graphique4', style= {'display': 'inline-block', 'width': '50%'}),
    dcc.Graph(id='graphique5',style= {'display': 'inline-block', 'width': '50%'}),
    
    dcc.Graph(id='graphique3'), 
    dash_table.DataTable(data=df.to_dict('records'), page_size=30)
    
])

###LAYOUT CARTO

tab2_layout = html.Div([
    html.Br(),
    html.H1('Cartographie',  style={'textAlign': 'center'}),
    dcc.Graph(id='map', style= {'display': 'inline-block', 'width': '45%'}),
    dcc.Graph(id='map2', style= {'display': 'inline-block', 'width': '55%'}),
    dcc.Graph(id='graphique21'),
    
    
])

###LAYOUT PRED

tab3_layout = html.Div([
    html.Br(),
    html.H1('Estimez votre bien :',  style={'textAlign': 'center'}),
    html.Br(),
    html.Br(),
    html.Label('Type local:'),
    dcc.Input(id='input-box-1', type='text', value=''),
    html.Label('Surface reelle bati en m2:'),
    dcc.Input(id='input-box-2', type='number', value=''),
    html.Label('Surface terrain en m2:'),
    dcc.Input(id='input-box-3', type='number', value=0),
    html.Label('Nombre de pièces :'),   
    dcc.Input(id='input-box-4', type='number', value=''),
    html.Label('Nombre de lots:'),   
    dcc.Input(id='input-box-5', type='number', value='1'),
    html.Label('Code Departement:'),   
    dcc.Input(id='input-box-6', type='text', value='01' ,maxLength=2, minLength=2),
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
     Output('graphique6', 'figure'),
     Output('graphique7', 'figure'),
     Output('graphique21', 'figure'),
     Output('map', 'figure'),
     Output('map2', 'figure'),
     Output('output', 'children')
    ],
    [Input('annee-dropdown', 'value'),
    Input('local-dropdown', 'value'),
    Input('button', 'n_clicks'),],
    [State('input-box-1', 'value'),
    State('input-box-2', 'value'),
    State('input-box-3', 'value'),
    State('input-box-4', 'value'),
    State('input-box-5', 'value'),
    State('input-box-6', 'value')]
)

##
##
###UPDATE
##
##

def update_output(selected_year, selected_local, n_clicks,  L, SRB, ST, NbP, NbL, codeP):
    
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
    fig1 = px.histogram(filtered_data, x='Type local', y='Valeur fonciere', histfunc='avg', title=f'Moyenne des prix des biens par type de local en {selected_year} pour les biens {selected_local}', color="Type local")
    fig2 = px.histogram(filtered_data, x='Type local', y='Surface terrain', histfunc='avg', title=f'Moyenne des surfaces des biens par type de local en {selected_year} pour les biens {selected_local}', color="Type local")
    fig3 = px.scatter(filtered_data, x='Commune', y="Valeur fonciere", title=f'Prix des biens dans les communes en {selected_year} pour les biens {selected_local}')
    fig4 = px.histogram(filtered_data, x="Mois",y='Valeur fonciere', title=f'Nombre de Ventes par mois en {selected_year} pour les biens {selected_local}', histfunc='count')
    fig5 = px.histogram(filtered_data, x="Mois",y='Valeur fonciere', title=f'Moyennes des prix de ventes par mois en {selected_year} pour les biens {selected_local}', histfunc='avg')
    fig6 = px.scatter(filtered_data, x='Surface reelle bati', y="Valeur fonciere", title=f'Prix des biens avec leur superficie en {selected_year} pour les biens {selected_local}')
    fig6.update_xaxes(range=[10, 600]) 
    fig7 = px.histogram(filtered_data, x="Surface reelle bati", y="Valeur fonciere", color="Type local", marginal="rug", hover_data=filtered_data.columns)
    fig7.update_xaxes(range=[10, 500]) 
    
    
    
    ##
    ### CARTOGRAPHIE 
    ##
    
    
    
    carte = px.choropleth(
        data_frame=cartoM,
        geojson=geojson_data,
        locations='code',
        featureidkey="properties.code",
        color='value',
        title='Prix du m2 par départements',
        color_continuous_scale=px.colors.sequential.Plasma,
        labels={'valeur prix du m2'}
    )
    
    carte.update_geos(fitbounds="locations")
    
    carte2 = px.choropleth(
        data_frame=carto2,
        geojson=geojson_data,
        locations='Code postal',
        featureidkey="properties.code",
        color='Moyenne Taux Chomage',
        title='Taux de chômage par départements',
        color_continuous_scale=px.colors.sequential.Plasma,
        labels={'Taux chômage (%)'}
    )
    
    carte2.update_geos(fitbounds="locations")
    
    fig21 = px.histogram(cartoM, x="nom", y='value', title=f'Prix du m2 par departement').update_xaxes(categoryorder= "total descending")
    
    
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
            texte = f'Nous avons supposé que avez un(e) {L}, '
        # Vous pouvez réutiliser les valeurs récupérées dans ces variables
        # Faites quelque chose avec ces variables ici, par exemple, imprimez-les
        moy_tc = df2["Moyenne Taux Chomage"].mean()
        
        ### m2 Code dep
        
        filtre = df2['Code postal'] == codeP
        
        filtre = df2[filtre]
        
        m2R = filtre["moyenne_prix_par_m2_par_code_postal"].mean()
    
        m2 = df2["prix_par_m2"][0]
        
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
         
         ##on rappelle le pkl à chaque fois 
         
        url_model_reg = 'https://github.com/dounya-bourhani/ProjetPython/blob/main/decision_tree_model.pkl'
        response_model_reg = requests.get(url_model_reg,verify=False)
        with open('decision_tree_model.pkl', 'wb') as f:
            f.write(response_model_reg.content)
        model_reg = joblib.load('decision_tree_model.pkl')

        # with open('decision_tree_model.pkl', 'rb') as file:
        #     model_reg = pickle.load(file)   
        
            
                
        print("Valeur du premier champ :", L)
        print("ça marche ? ", TM)
        print("test ? ", TA)
        print("m2:", m2)
        print('m2dep:', m2R)
        
        valeur = model_reg.predict(reg)
        print(valeur)
        
        # Retournez les valeurs pour les afficher dans l'interface utilisateur
        texte = texte + f' Votre bien est estimé à : "{valeur}" dans le deuxième champ.'
        # file.close()

    return fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig21, carte, carte2, texte




# Run the app
if __name__ == '__main__':
    # app.run(debug=False)
    app.run_server(debug=True)