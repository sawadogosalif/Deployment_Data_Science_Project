from dash import Dash, html, dcc, dash_table, Input, Output, State
import pandas as pd
from utils import load_data, format_number
import dash_bootstrap_components as dbc

pd.options.display.float_format = '${:.2f}'.format

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

# Load the data once when the app starts
df = load_data()

# Apply the formatting function to the DataFrame
data_preview = (df.sample(30).map(format_number)).to_dict('records')
selected_data = df.copy()  # Use a copy of the data loaded when the app started

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1('IMF Dashboard', className="bg-secondary h-100"),
        ], width=12),
    ]),
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H4('Select Columns:', style={'color': 'maroon'}),
                dcc.Dropdown(id='column-dropdown', multi=True, options=[{'label': col, 'value': col} for col in df.columns]),
                html.H4('Start Year:', style={'color': 'maroon'}),
                dcc.Input(id='start-year', type='number', placeholder='Start Year'),
                html.H4('End Year:', style={'color': 'maroon'}),
                dcc.Input(id='end-year', type='number', placeholder='End Year'),
                html.H4('Select Country:', style={'color': 'maroon'}),
                dcc.Dropdown(id='country-dropdown', multi=True, options=[{'label': country, 'value': country} for country in df['pays'].unique()]),
                html.Button("Load Data", id="btn-update-data", style={'background-color': 'maroon', 'color': 'white'}),
                html.Br(),
                html.Br(),
                html.Button("Download data Excel", id="btn_xlsx", style={'background-color': 'maroon', 'color': 'white'}),
                dcc.Download(id="download-data")
            ]),
        ], width=2, className="bg-secondary h-100", style={"height": "100vh"}),
        dbc.Col([
            html.Div([
                html.H1('Data Table', style={'color': 'maroon'}),
                dash_table.DataTable(
                    data=data_preview,
                    columns=[{"name": i, "id": i} for i in data_preview[0].keys()],
                    style_table={'overflowX': 'auto', 'maxWidth': '950px'},
                    style_header={'backgroundColor': 'maroon', 'color': 'white'},
                    style_cell={
                        'height': 'auto',
                        'minWidth': '120px',
                        'whiteSpace': 'normal'
                    },
                    id='data-table',
                ),
            ]),
        ], width=8),
    ]),
], fluid=True)

@app.callback(
    [Output('data-table', 'data'),
     Output('data-table', 'columns')],
    [Input('btn-update-data', 'n_clicks')],
    [State('column-dropdown', 'value'),
     State('start-year', 'value'),
     State('end-year', 'value'),
     State('country-dropdown', 'value')],
    prevent_initial_call=True,
)
def update_data(n_clicks, selected_columns, start_year, end_year, selected_countries):
    if n_clicks is None:
        raise PreventUpdate

    global selected_data

    # Filter the data based on user input

    if selected_columns:
        selected_columns = selected_columns + ["Year", "pays", "counterpart_area"]
        missing_features = [col for col in df.columns if col not in selected_columns]
        selected_data = selected_data.drop(columns=missing_features)
    if start_year:
        selected_data = selected_data[selected_data['Year'] >= str(start_year)]
    if end_year:
        selected_data = selected_data[selected_data['Year'] <= str(end_year)]
    if selected_countries:
        selected_data = selected_data[selected_data['pays'].isin(selected_countries)]

    # Apply the formatting function
    formatted_data = selected_data.sample(40).map(format_number).to_dict('records')

    # Extract the column names from the keys of the first dictionary in formatted_data
    column_names = [{'name': col, 'id': col} for col in selected_data.columns]

    return formatted_data, column_names
    




@app.callback(Output("download-data", "data"), [Input("btn_xlsx", "n_clicks")])
def generate_csv(n_nlicks):
    return dcc.send_data_frame(selected_data.to_csv, filename="IMF.csv")
    
application = app.server
    
if __name__ == '__main__':   
    application.run( port="7860")