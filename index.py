import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import json
import folium
from folium.plugins import HeatMap

# Load your CSV data
df = pd.read_csv('dataset.csv')

# Get unique values in the "State" column
unique_states = df['State Name'].unique()

# Initialize the Dash app
app = dash.Dash(__name__)

# Load GeoJSON data from the text file
with open('Indian_States.txt', 'r') as geojson_file:
    india_states_geojson = json.load(geojson_file)
# Define a list of available visualization types
available_visualizations = {
    'Scatter Plot': 'scatter',
    'Bar Chart': 'bar',
    'Line Chart': 'line',
    'Pie Chart': 'pie',
    'Box Plot': 'box',
    'Area Chart': 'area',
    'Heatmap': 'heatmap',
    'Violin Plot': 'violin',
    'Histogram': 'histogram',
    'Polar Scatter Plot': 'scatterpolar',
    'Sunburst Chart': 'sunburst',
    'Choropleth Map': 'choropleth'
}

# Function to generate a folium choropleth map


def generate_folium_map(selected_column):
    m = folium.Map(location=[20.5937, 78.9629],
                   zoom_start=5)  # Center of India

    folium.Choropleth(
        geo_data=india_states_geojson,
        name='choropleth',
        data=df,
        columns=['State Name', selected_column],
        key_on='feature.properties.NAME_1',
        fill_color='YlGn',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=selected_column
    ).add_to(m)

    m.save('temp_map.html')

    with open('temp_map.html', 'r') as map_file:
        map_html = map_file.read()

    return map_html


# Define the layout of the dashboard
app.layout = html.Div([
    html.H1("Data Visualization Dashboard", style={
            'font-family': 'Arial, sans-serif'}),
    dcc.Dropdown(
        id='visualization-type-dropdown',
        options=[{'label': vis_type, 'value': vis_type}
                 for vis_type in available_visualizations.keys()],
        value='Scatter Plot',
        clearable=False
    ),
    dcc.Dropdown(
        id='x-axis-dropdown',
        options=[{'label': 'All States', 'value': 'All'}] +
        [{'label': state, 'value': state} for state in unique_states],
        multi=True,
        value=['All']
    ),
    dcc.Dropdown(
        id='y-axis-dropdown',
        options=[{'label': col, 'value': col}
                 for col in df.columns if col != 'State Name'],
        value=[df.columns[1]],
        multi=True
    ),
    html.Iframe(id='selected-visualization',
                style={'border': 'none', 'width': '100%', 'height': '400px'})
])

@app.callback(
    Output('selected-visualization', 'srcDoc'),
    [Input('visualization-type-dropdown', 'value'),
     Input('x-axis-dropdown', 'value'),
     Input('y-axis-dropdown', 'value')]
)
def update_output(selected_visualization, selected_x_states, selected_y_columns):
    if 'All' in selected_x_states:
        filtered_df = df  # If 'All' is selected, no need to filter
    else:
        filtered_df = df[df['State Name'].isin(selected_x_states)]

    if selected_visualization == 'Scatter Plot':
        if selected_y_columns:
            fig = px.scatter(filtered_df, x='State Name',
                             y=selected_y_columns[0], title='Scatter Plot')
        else:
            # Handle the case where no column is selected
            fig = go.Figure()

    elif selected_visualization == 'Bar Chart':
        if selected_y_columns:
            # Create a list of selected columns for the y-axis
            y_columns = [
                col for col in selected_y_columns if col != 'State Name']

            # Create the bar chart with multiple y-axis parameters
            fig = px.bar(filtered_df, x='State Name',
                         y=y_columns, title='Bar Chart')
        else:
            # Handle the case where no column is selected
            fig = go.Figure()

    elif selected_visualization == 'Line Chart':
        if selected_y_columns:
            fig = px.line(filtered_df, x='State Name', y=selected_y_columns,
                          title='Line Chart')  # Use selected_y_columns as a list
        else:
            # Handle the case where no column is selected for the heatmap
            fig = go.Figure()

    elif selected_visualization == 'Pie Chart':
        if selected_y_columns:
            fig = px.pie(filtered_df, names='State Name',
                         values=selected_y_columns[0], title='Pie Chart')
        else:
            # Handle the case where no column is selected for the heatmap
            fig = go.Figure()

    elif selected_visualization == 'Box Plot':
        if selected_y_columns:
            fig = px.box(filtered_df, x='State Name',
                         y=selected_y_columns[0], title='Box Plot')
            fig.update_layout(
                title=f'{selected_y_columns[0]} Box Plot',
                xaxis=dict(title='State'),
                yaxis=dict(title=f'{selected_y_columns[0]}')
            )
        else:
            # Handle the case where no column is selected
            fig = go.Figure()

    elif selected_visualization == 'Area Chart':
        if selected_y_columns:
            fig = px.area(filtered_df, x='State Name',
                          y=selected_y_columns, title='Area Chart')  # Use selected_y_columns as a list
            fig.update_layout(
                title=f'Area Chart',
                xaxis=dict(title='State'),
                yaxis=dict(title='Value')
            )
        else:
            # Handle the case where no column is selected
            fig = go.Figure()

    elif selected_visualization == 'Heatmap':
        if selected_y_columns:
            # Get the selected column name
            selected_column_name = selected_y_columns[0]
            # Pivot the DataFrame for the heatmap
            pivot_df = df.pivot(index='State Name', columns=selected_column_name,
                                values=selected_column_name)
            fig = go.Figure(data=go.Heatmap(z=pivot_df.values,
                            x=pivot_df.columns, y=pivot_df.index))
            fig.update_layout(
                title=f'{selected_column_name} Heatmap',
                # Use selected_column_name as x-axis label
                xaxis=dict(title=selected_column_name),
                yaxis=dict(title='State')
            )
        else:
            # Handle the case where no column is selected for the heatmap
            fig = go.Figure()

    elif selected_visualization == 'Violin Plot':
        if selected_y_columns:
            fig = px.violin(filtered_df, x='State Name',
                            y=selected_y_columns[0], box=True)
            fig.update_layout(
                title=f'{selected_y_columns[0]} Violin Plot',
                xaxis=dict(title='State'),
                yaxis=dict(title=f'{selected_y_columns[0]}')
            )
        else:
            # Handle the case where no column is selected
            fig = go.Figure()

    elif selected_visualization == 'Histogram':
        if selected_y_columns:
            fig = px.histogram(filtered_df, x=selected_y_columns,
                               color='State Name')
            fig.update_layout(
                title=f'Histogram',
                xaxis=dict(title='Value'),
                yaxis=dict(title='Count')
            )
        else:
            # Handle the case where no column is selected
            fig = go.Figure()

    elif selected_visualization == 'Polar Scatter Plot':
        if selected_y_columns:
            fig = px.scatter_polar(filtered_df, r=selected_y_columns[0],
                                   theta='State Name', color='State Name')
        else:
            # Handle the case where no column is selected
            fig = go.Figure()

    elif selected_visualization == 'Sunburst Chart':
        if selected_y_columns:
            fig = px.sunburst(
                filtered_df, path=['State Name', selected_y_columns[0]], values=selected_y_columns[0])
        else:
            # Handle the case where no column is selected
            fig = go.Figure()

    elif selected_visualization == 'Choropleth Map':
        map_html = generate_folium_map(selected_y_columns[0])
        return map_html  # Return the HTML string for the map

    # Convert the Plotly figure to an HTML string
    fig_html = fig.to_html()

    return fig_html


if __name__ == '__main__':
    app.run_server(debug=True)
