import dash
from dash import dcc, html, dash_table
import requests
import pandas as pd

app = dash.Dash(__name__)
server = app.server  # Needed to deploy with Flask

API_URL = "http://127.0.0.1:5000/data"

def fetch_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    return pd.DataFrame()

df = fetch_data()

app.layout = html.Div([
    html.H1("📊 Student Performance Dashboard"),
    dcc.Interval(id='interval-update', interval=5000, n_intervals=0),
    dash_table.DataTable(
        id='data-table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("records"),
        page_size=10,
        style_table={'overflowX': 'auto'}
    )
])

@app.callback(
    dash.Output('data-table', 'data'),
    [dash.Input('interval-update', 'n_intervals')]
)
def update_data(n):
    return fetch_data().to_dict("records")

if __name__ == "__main__":
    app.run_server(debug=True)
