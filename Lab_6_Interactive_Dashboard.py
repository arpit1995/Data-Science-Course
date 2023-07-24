# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
launch_sites = []
launch_sites.append({'label': 'All Sites', 'value': 'All Sites'})
for item in spacex_df["Launch Site"].value_counts().index:
    launch_sites.append({'label': item, 'value': item})

app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                dcc.Dropdown(id='site-dropdown', options = launch_sites, value = 'All Sites', placeholder = "Select a Launch Site here", searchable = True),
                                html.Br(),
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),
                                html.Div(dcc.Graph(id='success-pie-chart-2')),  # Second pie chart
                                html.Br(),
                                html.P("Payload range (Kg):"),
                                dcc.RangeSlider(id='payload-slider', min = 0, max = 10000, step = 1000, value = [min_payload, max_payload], 
                                                marks={ 2000: {'label': '2000 (Kg)'}, 5000: {'label': '5000 (Kg)'}, 8000: {'label': '8000 (Kg)'}}),
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

@app.callback( Output(component_id='success-pie-chart', component_property='figure'),
               Input(component_id='site-dropdown', component_property='value')
)
def select(inputt):
    if inputt == 'All Sites':
        new_df = spacex_df.groupby(['Launch Site'])["class"].sum().to_frame()
        new_df = new_df.reset_index()
        fig = px.pie(new_df, values='class', names='Launch Site', title='Total Success Launches by Site')
    else:
        new_df = spacex_df[spacex_df["Launch Site"] == inputt]["class"].value_counts().to_frame()
        new_df["name"] = ["Failure", "Success"]
        fig = px.pie(new_df, values='class', names='name', title='Total Success Launches for ' + inputt)
    return fig

@app.callback( Output(component_id='success-pie-chart-2', component_property='figure'),
               Input(component_id='site-dropdown', component_property='value')
)
def select_2(inputt):
    if inputt == 'All Sites':
        new_df = spacex_df.groupby(['Launch Site'])["class"].value_counts().unstack().reset_index()
        fig = go.Figure(data=[go.Pie(labels=['Failure', 'Success'], values=new_df.iloc[i, 1:], hole=.3) for i in range(new_df.shape[0])],
        layout=go.Layout(
            title_text="Success / Failure Outcomes by Site",
            updatemenus=[go.layout.Updatemenu(
                active=0,
                buttons=list([
                    dict(label=site, method="update", args=[{"visible": [False]*i + [True] + [False]*(new_df.shape[0]-i-1)}]) for i, site in enumerate(new_df['Launch Site'])]
                ))
            ]))
    else:
        new_df = spacex_df[spacex_df["Launch Site"] == inputt]["class"].value_counts().reset_index()
        new_df["name"] = ["Failure", "Success"]
        total = new_df['class'].sum()
        new_df['class'] = new_df['class']/total  # Calculate ratio
        fig = px.pie(new_df, values='class', names='name', title='Success vs Failure Ratio for ' + inputt)
    return fig

@app.callback( Output(component_id='success-payload-scatter-chart', component_property='figure'),
               Input(component_id='site-dropdown', component_property='value'), Input(component_id='payload-slider', component_property='value') 
)
def scatter(input1, input2):
    print(input1)
    print(input2)
    if input1 == 'All Sites':
        new_df = spacex_df
        new_df2 = new_df[new_df["Payload Mass (kg)"] >= input2[0]]
        new_df3 = new_df2[new_df2["Payload Mass (kg)"] <= input2[1]]
        fig2 = px.scatter(new_df3, y="class", x="Payload Mass (kg)", color="Booster Version Category")
    else:
        new_df = spacex_df[spacex_df["Launch Site"] == input1]
        new_df2 = new_df[new_df["Payload Mass (kg)"] >= input2[0]]
        new_df3 = new_df2[new_df2["Payload Mass (kg)"] <= input2[1]]
        fig2 = px.scatter(new_df3, y="class", x="Payload Mass (kg)", color="Booster Version Category")
    return fig2

# Run the app
if __name__ == '__main__':
    app.run_server()