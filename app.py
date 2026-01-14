# dash_sales_customer_dashboard_final.py
# Usage: python dash_sales_customer_dashboard_final.py

import pandas as pd
from datetime import datetime
from dash import Dash, html, dcc, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
df = pd.read_csv("./data/ecommerce_synthetic_dataset.csv") # uploaded dataset
print(df.head)
# Quick preprocessing
df.columns = [c.strip() for c in df.columns]

# Parse dates (handle dd-mm-YYYY safely)
for date_col in ['PurchaseDate', 'SignUpDate']:
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce', dayfirst=True)

# Ensure numeric fields
if 'Quantity' not in df.columns:
    df['Quantity'] = 1
if 'Price' not in df.columns:
    df['Price'] = 0.0
if 'TotalAmount' not in df.columns:
    try:
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0.0)
        df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(1)
    except Exception:
        pass
    df['TotalAmount'] = df['Price'] * df['Quantity']

# Fill categorical missing values
for c in ['Category', 'Country', 'Gender', 'ProductName', 'DeviceType', 'ReferralSource', 'UserName']:
    if c in df.columns:
        df[c] = df[c].fillna('Unknown')

# Add Date and Month fields (use parsed PurchaseDate)
if 'PurchaseDate' in df.columns and not df['PurchaseDate'].isna().all():
    df['Date'] = pd.to_datetime(df['PurchaseDate'], dayfirst=True, errors='coerce').dt.date
    df['Month'] = pd.to_datetime(df['PurchaseDate'], dayfirst=True, errors='coerce').dt.to_period('M').dt.to_timestamp()
else:
    today_ts = pd.to_datetime('today')
    df['Date'] = today_ts.date()
    df['Month'] = today_ts.to_period('M').to_timestamp()

# Ensure UserID exists

if 'UserID' not in df.columns and 'UserName' in df.columns:
    df['UserID'] = df['UserName'].astype(str)
elif 'UserID' not in df.columns:
    # fallback: create synthetic user ids
    df['UserID'] = df.index.astype(str)

app = Dash(__name__, title='Sales & Customer Dashboard — Colorful (fixed)')
server = app.server

# Inject CSS into the page head via app.index_string
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
body { font-family: 'Inter', Arial, sans-serif; background: linear-gradient(180deg,#f3f8ff 0%, #f7fbf9 100%); margin:0; }
.card:hover { transform: translateY(-6px); box-shadow: 0 14px 30px rgba(20,30,80,0.08); }
.kpi-value { font-weight: 700; font-size: 20px; }
.kpi-sub { color: rgba(0,0,0,0.6); font-size: 13px; }
.small-muted { color: rgba(0,0,0,0.55); font-size: 13px; }
.sidebar-label { font-weight:600; color: #222; margin-bottom:6px; display:block; }
.accent-pill { display:inline-block; padding:6px 10px; border-radius:999px; font-weight:600; font-size:13px; }
"""

app.index_string = f"""
<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{app.title}</title>
        {{%favicon%}}
        {{%css%}}
        <style>{CUSTOM_CSS}</style>
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>
"""

# Color palette (variables we'll reuse)
PRIMARY_GRADIENT = "linear-gradient(90deg,#6a11cb 0%, #2575fc 100%)"  # purple -> blue
ACCENT_1 = "#ff7a59"  # coral
ACCENT_2 = "#ffd166"  # yellow
ACCENT_3 = "#6ce3b8"  # mint
CARD_BG = "linear-gradient(180deg, rgba(255,255,255,0.95), rgba(250,250,255,0.95))"

# Card and header base styles
CARD_STYLE = {
    'padding': '14px',
    'borderRadius': '12px',
    'boxShadow': '0 6px 18px rgba(22,30,50,0.06)',
    'background': 'white',
    'boxSizing': 'border-box',
    'transition': 'transform 0.15s ease, box-shadow 0.15s ease'
}
HEADER_STYLE = {
    'background': PRIMARY_GRADIENT,
    'color': 'white',
    'padding': '20px',
    'borderRadius': '12px',
    'marginBottom': '14px',
    'boxShadow': '0 8px 20px rgba(37,117,252,0.12)'
}

MAIN_CHART_HEIGHT = '420px'
SIDE_CHART_HEIGHT = '340px'
SMALL_CHART_HEIGHT = '280px'

country_options = [{'label': c, 'value': c} for c in sorted(df['Country'].unique())] if 'Country' in df.columns else []
category_options = [{'label': c, 'value': c} for c in sorted(df['Category'].unique())] if 'Category' in df.columns else []

app.layout = html.Div([
    # Top header (badges removed)
    html.Div([
        html.Div([
            html.H2('📊 Sales & Customer Dashboard', style={'margin': 0, 'fontWeight': 700}),
            html.Div('Dashboard for e-commerce dataset', style={'opacity': 0.9})
        ])
    ], style=HEADER_STYLE),

    # Main container
    html.Div([
        # LEFT SIDEBAR
        html.Div([
            html.Div('Filters', style={'fontSize': 16, 'fontWeight': 700, 'marginBottom': 12}),
            html.Div([
                html.Label('Country', className='sidebar-label'),
                dcc.Dropdown(id='country-filter', options=country_options, value=[], multi=True, placeholder='All countries')
            ], style={'marginBottom': 10}),

            html.Div([
                html.Label('Category', className='sidebar-label'),
                dcc.Dropdown(id='category-filter', options=category_options, value=[], multi=True, placeholder='All categories')
            ], style={'marginBottom': 10}),
            html.Div([
                html.Label('Date Range', className='sidebar-label'),
                dcc.DatePickerRange(
                    id='date-range',
                    start_date=df['Date'].min() if 'Date' in df.columns else None,
                    end_date=df['Date'].max() if 'Date' in df.columns else None,
                    display_format='YYYY-MM-DD',
                    style={'width':'100%'}
                )
            ], style={'marginBottom': 12}),

            html.Div([
                html.Button('Download CSV', id='btn-download', style={
                    'width':'100%', 'padding':'10px 12px', 'borderRadius':'10px', 'border':'none',
                    'background': 'linear-gradient(90deg, #ff7a59, #ff9a76)', 'color':'white', 'fontWeight':700, 'cursor':'pointer'
                }),
                dcc.Download(id='download-csv')
            ], style={'marginBottom': 14}),

            html.Div([
                html.Div('Quick actions', style={'fontWeight':700, 'marginBottom':8}),
                html.Button('Export PNG (all)', id='btn-export-png', style={'width':'100%','padding':'8px','borderRadius':'8px','border':'1px solid rgba(0,0,0,0.06)','background':'white','cursor':'pointer'})
            ], style={'marginBottom': 18}),

            html.Hr(),
             html.Div([
                html.Div('Tips', style={'fontWeight':700, 'marginBottom':8}),
                html.Div('• Use filters to narrow down data.\n• Click Download to export the filtered dataset.\n• Hover charts to see details.', style={'whiteSpace':'pre-line', 'color':'#333', 'opacity':0.85})
            ], style={'fontSize':13, 'lineHeight':'1.4'}),

            html.Div(style={'height':'32px'})
        ],
        style={
            'width': '320px',
            'minWidth': '280px',
            'padding': '18px',
            'boxSizing': 'border-box',
            'borderRadius': '12px',
            'background': 'linear-gradient(180deg, #ffffff, #fcfdff)',
            'boxShadow': '0 8px 30px rgba(33,47,97,0.04)',
            'position': 'sticky',
            'top': '26px',
            'height': 'calc(100vh - 120px)',
            'overflowY': 'auto'
        }),
         # RIGHT MAIN
        html.Div([
            # KPI row (colorful)
            html.Div([
                html.Div([
                    html.Div(style={'display':'flex','justifyContent':'space-between','alignItems':'center'}, children=[
                        html.Div('Total Revenue', className='kpi-sub'),
                        html.Div('🔥', style={'fontSize':18})
                    ]),
                    html.H3(id='kpi-revenue', className='kpi-value', style={'marginTop':6}),
                    dcc.Graph(id='sparkline-revenue', config={'displayModeBar': False}, style={'height':'70px', 'marginTop':6})
                ], className='card', style={**CARD_STYLE, 'background': 'linear-gradient(90deg,#fff8f2, #fff6f9)'}),

                html.Div([
                    html.Div('Total Orders', className='kpi-sub'),
                    html.H3(id='kpi-orders', className='kpi-value', style={'marginTop':6}),
                ], className='card', style={**CARD_STYLE, 'background': 'linear-gradient(90deg,#f6fbff,#f0f9ff)'}),

                html.Div([
                    html.Div('Unique Customers', className='kpi-sub'),
                    html.H3(id='kpi-customers', className='kpi-value', style={'marginTop':6}),
                ], className='card', style={**CARD_STYLE, 'background': 'linear-gradient(90deg,#f9fff6,#f0fff0)'}),

                html.Div([
                    html.Div('Avg Order Value', className='kpi-sub'),
                    html.H3(id='kpi-aov', className='kpi-value', style={'marginTop':6}),
                ], className='card', style={**CARD_STYLE, 'background': 'linear-gradient(90deg,#fff8ff,#fff0ff)'}),
            ], style={'display':'grid', 'gridTemplateColumns':'repeat(auto-fit, minmax(180px, 1fr))', 'gap':'12px', 'marginBottom':20}),
            
            # Sales Over Time
            html.Div([
                html.Div('Sales Over Time', style={'fontWeight':700, 'marginBottom':8, 'color':'#123'}),
                dcc.Graph(id='sales-time-series', config={'displayModeBar': False}, style={'height': MAIN_CHART_HEIGHT})
            ], className='card', style={**CARD_STYLE, 'padding':'18px', 'marginBottom':18}),

            # World map
            html.Div([
                html.Div('Global Sales (by Country)', style={'fontWeight':700, 'marginBottom':8, 'color':'#123'}),
                dcc.Graph(id='sales-world-map', config={'displayModeBar': False}, style={'height': MAIN_CHART_HEIGHT})
            ], className='card', style={**CARD_STYLE, 'padding':'18px', 'marginBottom':18}),

            # Category + Top products stacked
            html.Div([
                html.Div('Revenue by Category', style={'fontWeight':700, 'marginBottom':8}),
                dcc.Graph(id='sales-by-category', config={'displayModeBar': False}, style={'height': SIDE_CHART_HEIGHT}),
            ], className='card', style={**CARD_STYLE, 'padding':'18px', 'marginBottom':16}),

            html.Div([
                html.Div('Top Products', style={'fontWeight':700, 'marginBottom':8}),
                dcc.Graph(id='top-products', config={'displayModeBar': False}, style={'height': SIDE_CHART_HEIGHT}),
            ], className='card', style={**CARD_STYLE, 'padding':'18px', 'marginBottom':16}),

            html.Div([
                html.Div('Category → Product (Sunburst)', style={'fontWeight':700, 'marginBottom':8}),
                dcc.Graph(id='category-sunburst', config={'displayModeBar': False}, style={'height': SIDE_CHART_HEIGHT}),
            ], className='card', style={**CARD_STYLE, 'padding':'18px', 'marginBottom':18}),
            
            # Customer charts
            html.Div([
                html.Div('Customers by Gender', style={'fontWeight':700, 'marginBottom':8}),
                dcc.Graph(id='gender-pie', style={'height': SMALL_CHART_HEIGHT})
            ], className='card', style={**CARD_STYLE, 'padding':'18px', 'marginBottom':16}),

            html.Div([
                html.Div('Referral Sources', style={'fontWeight':700, 'marginBottom':8}),
                dcc.Graph(id='referral-bar', style={'height': SMALL_CHART_HEIGHT})
            ], className='card', style={**CARD_STYLE, 'padding':'18px', 'marginBottom':16}),

            html.Div([
                html.Div('Session Duration vs Avg Order Value', style={'fontWeight':700, 'marginBottom':8}),
                dcc.Graph(id='session-scatter', style={'height': SMALL_CHART_HEIGHT})
            ], className='card', style={**CARD_STYLE, 'padding':'18px', 'marginBottom':36}),

        ], style={'flex': '1', 'paddingLeft': '22px', 'boxSizing': 'border-box', 'minWidth': 0})
    ], style={'display': 'flex', 'gap': '24px', 'alignItems': 'flex-start', 'paddingBottom': '40px'}),

], style={'padding': '22px'})
def filter_df(df_in, countries, categories, start_date, end_date):
    dff = df_in.copy()
    if countries:
        if isinstance(countries, str):
            countries = [countries]
        dff = dff[dff['Country'].isin(countries)]
    if categories:
        if isinstance(categories, str):
            categories = [categories]
        dff = dff[dff['Category'].isin(categories)]
    if start_date:
        try:
            sd = pd.to_datetime(start_date, dayfirst=True).date()
            dff = dff[dff['Date'] >= sd]
        except Exception:
            pass
    if end_date:
        try:
            ed = pd.to_datetime(end_date, dayfirst=True).date()
            dff = dff[dff['Date'] <= ed]
        except Exception:
            pass
    return dff
@app.callback(
    Output('kpi-revenue', 'children'),
    Output('kpi-orders', 'children'),
    Output('kpi-customers', 'children'),
    Output('kpi-aov', 'children'),
    Output('sparkline-revenue', 'figure'),
    Input('country-filter', 'value'),
    Input('category-filter', 'value'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date')
)
def update_kpis_and_sparkline(countries, categories, start_date, end_date):
    dff = filter_df(df, countries or [], categories or [], start_date, end_date)
    revenue = dff['TotalAmount'].sum() if 'TotalAmount' in dff.columns else 0
    orders = len(dff)
    customers = dff['UserID'].nunique() if 'UserID' in dff.columns else (dff['UserName'].nunique() if 'UserName' in dff.columns else 0)
    aov = revenue / orders if orders > 0 else 0

    ts_small = dff.groupby('Month', as_index=False)['TotalAmount'].sum().sort_values('Month') if 'Month' in dff.columns and 'TotalAmount' in dff.columns else pd.DataFrame()
    if ts_small.empty:
        fig_sp = go.Figure()
        fig_sp.add_annotation(text='No data', showarrow=False, xref='paper', yref='paper', x=0.5, y=0.5)
        fig_sp.update_layout(margin=dict(l=0, r=0, t=4, b=4), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    else:
        fig_sp = px.area(ts_small, x='Month', y='TotalAmount')
        fig_sp.update_traces(line=dict(width=1))
        fig_sp.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False),
                             margin=dict(l=0, r=0, t=4, b=4), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    return f"₹{revenue:,.2f}", f"{orders:,}", f"{customers:,}", f"₹{aov:,.2f}", fig_sp

@app.callback(
    Output('sales-time-series', 'figure'),
    Output('sales-by-category', 'figure'),
    Output('top-products', 'figure'),
    Input('country-filter', 'value'),
    Input('category-filter', 'value'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date')
)
def update_sales_charts(countries, categories, start_date, end_date):
    dff = filter_df(df, countries or [], categories or [], start_date, end_date)

    # time series
    if 'Month' in dff.columns and 'TotalAmount' in dff.columns:
        ts = dff.groupby('Month', as_index=False)['TotalAmount'].sum().sort_values('Month')
    else:
        ts = pd.DataFrame()
    if ts.empty:
        fig_ts = go.Figure()
        fig_ts.add_annotation(text='No data', showarrow=False, xref='paper', yref='paper', x=0.5, y=0.5)
    else:
        fig_ts = px.line(ts, x='Month', y='TotalAmount', title='Revenue over Time')
        fig_ts.update_layout(margin=dict(l=40, r=20, t=40, b=30))

    # category bars
    if 'Category' in dff.columns and not dff.empty and 'TotalAmount' in dff.columns:
        cat = dff.groupby('Category', as_index=False)['TotalAmount'].sum().sort_values('TotalAmount', ascending=False)
        fig_cat = px.bar(cat, x='TotalAmount', y='Category', orientation='h', title='Revenue by Category')
        fig_cat.update_layout(margin=dict(l=80, r=20, t=40, b=30))
    else:
        fig_cat = go.Figure()
        fig_cat.add_annotation(text='No category data', showarrow=False, xref='paper', yref='paper', x=0.5, y=0.5)
         # top products
    if 'ProductName' in dff.columns and not dff.empty and 'TotalAmount' in dff.columns:
        prod = dff.groupby('ProductName', as_index=False)['TotalAmount'].sum().sort_values('TotalAmount', ascending=False).head(10)
        fig_prod = px.bar(prod, x='TotalAmount', y='ProductName', orientation='h', title='Top 10 Products')
        fig_prod.update_layout(margin=dict(l=120, r=20, t=40, b=30))
    else:
        fig_prod = go.Figure()
        fig_prod.add_annotation(text='No product data', showarrow=False, xref='paper', yref='paper', x=0.5, y=0.5)

    return fig_ts, fig_cat, fig_prod

@app.callback(
    Output('sales-world-map', 'figure'),
    Output('category-sunburst', 'figure'),
    Input('country-filter', 'value'),
    Input('category-filter', 'value'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date')
)
def update_map_and_sunburst(countries, categories, start_date, end_date):
    dff = filter_df(df, countries or [], categories or [], start_date, end_date)

    # choropleth
    if 'Country' in dff.columns and not dff.empty and 'TotalAmount' in dff.columns:
        country_agg = dff.groupby('Country', as_index=False)['TotalAmount'].sum().sort_values('TotalAmount', ascending=False)
        fig_map = px.choropleth(country_agg, locations='Country', locationmode='country names',
                                color='TotalAmount', hover_name='Country',
                                color_continuous_scale='Blues', title='Revenue by Country')
        fig_map.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    else:
        fig_map = go.Figure()
        fig_map.add_annotation(text='No country data', showarrow=False, xref='paper', yref='paper', x=0.5, y=0.5)

    # sunburst
    if 'Category' in dff.columns and 'ProductName' in dff.columns and not dff.empty and 'TotalAmount' in dff.columns:
        sb = dff.groupby(['Category', 'ProductName'], as_index=False)['TotalAmount'].sum()
        fig_sb = px.sunburst(sb, path=['Category', 'ProductName'], values='TotalAmount', title='Revenue: Category → Product')
        fig_sb.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    else:
        fig_sb = go.Figure()
        fig_sb.add_annotation(text='No category/product data', showarrow=False, xref='paper', yref='paper', x=0.5, y=0.5)

    return fig_map, fig_sb

@app.callback(
    Output('gender-pie', 'figure'),
    Output('referral-bar', 'figure'),
    Output('session-scatter', 'figure'),
    Input('country-filter', 'value'),
    Input('category-filter', 'value'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date')
)
def update_customer_charts(countries, categories, start_date, end_date):
    dff = filter_df(df, countries or [], categories or [], start_date, end_date)

    if 'Gender' in dff.columns and not dff.empty:
        gender = dff['Gender'].value_counts().reset_index()
        gender.columns = ['Gender', 'Count']
        fig_gender = px.pie(gender, values='Count', names='Gender', title='Gender Distribution')
    else:
        fig_gender = go.Figure()
        fig_gender.add_annotation(text='No gender data', showarrow=False, xref='paper', yref='paper', x=0.5, y=0.5)

    if 'ReferralSource' in dff.columns and not dff.empty:
        ref = dff['ReferralSource'].value_counts().reset_index()
        ref.columns = ['ReferralSource', 'Count']
        fig_ref = px.bar(ref.head(10), x='Count', y='ReferralSource', orientation='h', title='Top Referral Sources')
    else:
        fig_ref = go.Figure()
        fig_ref.add_annotation(text='No referral data', showarrow=False, xref='paper', yref='paper', x=0.5, y=0.5)

    if 'SessionDuration' in dff.columns and 'UserID' in dff.columns and not dff.empty:
        cust = dff.groupby('UserID', as_index=False).agg({'SessionDuration': 'mean', 'TotalAmount': 'mean'}).rename(columns={'TotalAmount': 'AvgOrderValue'})
        if cust.empty:
            fig_scatter = go.Figure()
            fig_scatter.add_annotation(text='No session/customer data', showarrow=False, xref='paper', yref='paper', x=0.5, y=0.5)
        else:
            fig_scatter = px.scatter(cust, x='SessionDuration', y='AvgOrderValue', size='AvgOrderValue', title='Session Duration vs Avg Order Value')
    else:
        fig_scatter = go.Figure()
        fig_scatter.add_annotation(text='No session or user data', showarrow=False, xref='paper', yref='paper', x=0.5, y=0.5)

    for fig in (fig_gender, fig_ref, fig_scatter):
        fig.update_layout(margin=dict(l=30, r=20, t=40, b=30))

    return fig_gender, fig_ref, fig_scatter
@app.callback(
    Output('download-csv', 'data'),
    Input('btn-download', 'n_clicks'),
    State('country-filter', 'value'),
    State('category-filter', 'value'),
    State('date-range', 'start_date'),
    State('date-range', 'end_date'),
    prevent_initial_call=True
)
def generate_csv(n_clicks, countries, categories, start_date, end_date):
    dff = filter_df(df, countries or [], categories or [], start_date, end_date)
    return dcc.send_data_frame(dff.to_csv, filename='filtered_sales.csv', index=False)

if __name__ == '__main__':
    print('Starting colorful Dash app (fixed, no badges) on http://127.0.0.1:7860')
    app.run(debug=False, port=7860, host='0.0.0.0')
