import dash
from dash import dcc, html, dash_table
import requests
import pandas as pd

# ✅ Initialize Dash App
app = dash.Dash(__name__)

# ✅ Fetch Data from Flask API
def get_data():
    try:
        response = requests.get("http://127.0.0.1:5000/get_data")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
    except:
        return pd.DataFrame()

# ✅ Layout for Dashboard
app.layout = html.Div([
    html.H1("📊 Real-Time Monitoring Dashboard"),
    
    # ✅ File Upload Section
    dcc.Upload(
        id="upload-data",
        children=html.Button("📂 Upload File"),
        multiple=False
    ),
    
    html.Div(id="upload-status"),

    # ✅ Data Table Section
    html.H2("📜 Extracted Data"),
    dash_table.DataTable(
        id="data-table",
        columns=[{"name": i, "id": i} for i in get_data().columns],
        data=get_data().to_dict("records"),
        page_size=10,
        style_table={"overflowX": "auto"}
    ),
    
    html.Button("🔄 Refresh Data", id="refresh-btn", n_clicks=0),
])

# ✅ Callback to Refresh Data
@app.callback(
    dash.Output("data-table", "data"),
    dash.Input("refresh-btn", "n_clicks")
)
def refresh_data(n_clicks):
    return get_data().to_dict("records")

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
