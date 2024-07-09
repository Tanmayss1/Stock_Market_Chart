import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import os

# Initialize the Dash app
app = dash.Dash(__name__)

# Directory containing CSV files
csv_dir =' put file path here'  # Change this to the correct path

# Get the list of CSV files
csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]

# Check if csv_files is empty
if not csv_files:
    raise FileNotFoundError("No CSV files found in the specified directory.")

# Print the list of CSV files for debugging
print("CSV files found:", csv_files)

stock_options = [{'label': f.split('.')[0], 'value': os.path.join(csv_dir, f)} for f in csv_files]

# Define the layout of the app
app.layout = html.Div([
    dcc.Dropdown(
        id='stock-dropdown',
        options=stock_options,
        value=stock_options[0]['value'],  # Use stock_options instead of csv_files
        clearable=False
    ),
    dcc.RadioItems(
        id='chart-type',
        options=[
            {'label': 'Candlestick', 'value': 'candlestick'},
            {'label': 'Line', 'value': 'line'},
            {'label': 'Bar', 'value': 'bar'},
        ],
        value='candlestick'
    ),
    dcc.Graph(id='stock-chart')
])

# Define the callback to update the chart
@app.callback(
    Output('stock-chart', 'figure'),
    [Input('stock-dropdown', 'value'), Input('chart-type', 'value')]
)
def update_chart(selected_stock, chart_type):
    df = pd.read_csv(selected_stock)
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values('Date', inplace=True)

    # Identify maximum and minimum points in 14-day windows
    max_points = []
    min_points = []
    window_size = 14

    for i in range(0, len(df), window_size):
        window_df = df.iloc[i:i + window_size]
        if not window_df.empty:
            max_idx = window_df['High'].idxmax()
            min_idx = window_df['Low'].idxmin()
            max_points.append((df.loc[max_idx, 'Date'], df.loc[max_idx, 'High']))
            min_points.append((df.loc[min_idx, 'Date'], df.loc[min_idx, 'Low']))

    if chart_type == 'candlestick':
        fig = go.Figure(data=[go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close']
        )])
    elif chart_type == 'line':
        fig = go.Figure(data=[go.Scatter(
            x=df['Date'],
            y=df['Close'],
            mode='lines'
        )])
    elif chart_type == 'bar':
        fig = go.Figure(data=[go.Bar(
            x=df['Date'],
            y=df['Close']
        )])

    # Add maximum points as red circles
    fig.add_trace(go.Scatter(
        x=[point[0] for point in max_points],
        y=[point[1] for point in max_points],
        mode='markers',
        marker=dict(color='red', size=2, symbol='circle'),
        name='Max Points'
    ))

    # Add minimum points as green circles
    fig.add_trace(go.Scatter(
        x=[point[0] for point in min_points],
        y=[point[1] for point in min_points],
        mode='markers',
        marker=dict(color='green', size=2, symbol='circle'),
        name='Min Points'
    ))

    fig.update_layout(title=f'Stock Price for {os.path.basename(selected_stock).split(".")[0]}')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
