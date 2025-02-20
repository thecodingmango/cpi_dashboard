# Import libraries required for building the dashboard
import pandas as pd
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from models import models

def header():
    header_layout = html.Div(
        id='header',
        className='header',
        children=[
            html.Div(
                children=[
                    html.H1(
                        children='Consumer Price Index (CPI) DashBoard',
                        className='header-title'
                    ),
                    html.H2(children='Visualizing CPI and Different Commodity',
                            className='header-description')
                ],
            )
        ]
    )

    return header_layout


def date_picker(data):
    # Convert 'year_month' to a unique sorted list for dropdown
    month_options = [{'label': ym, 'value': ym} for ym in sorted(data['year_month'].unique())]

    range_picker = html.Div(
        children=[
            html.Label("Select Start Month:"),
            dcc.Dropdown(
                id='start_month',
                options=month_options,
                value=data['year_month'].min(),  # Default to earliest available month
                clearable=False,
            ),

            html.Label("Select End Month:"),
            dcc.Dropdown(
                id='end_month',
                options=month_options,
                value=data['year_month'].max(),  # Default to latest available month
                clearable=False,
            ),
        ],
        className='date_picker_container'
    )

    return range_picker


def drop_down():
    menu = dcc.Dropdown(
        id='drop_down_menu',
        className='drop_down_menu',
        options=[
            {'label': 'Inflation & Energy Prices', 'value': 'Commodity Prices'},
            {'label': 'Energy Dependence by Region', 'value': 'Energy Dependence'},
            {'label': 'CPI & Oil Price Forecasting', 'value': 'Forecasting'},
            #{'label': 'Consumer Spending and CPI', 'value': 'Consumer Spending'}
        ],
        value='Commodity Prices',
        clearable=False
    )

    return menu


def line_graph(fig, data, x, y, title=None, x_axis=None, y_axis=None):
    fig.add_trace(go.Scatter(
        x=data[x],
        y=data[y],
        mode='lines',
        name=y
    ))

    fig.update_layout(
        title=title,
        xaxis_title=x_axis,
        yaxis_title=y_axis,
        showlegend=True,
        legend=dict(title="Legend"),
        plot_bgcolor='#252a3b',  # Dark background
        paper_bgcolor='#1E1E2F',  # Dark paper background
        font=dict(color='white')
    )

    return fig


def dual_axis_line_chart(fig, data, x, y1, y2, title=None, x_axis=None, y1_axis=None, y2_axis=None):
    for item in y1:
        fig.add_trace(go.Scatter(
            x=data[x],
            y=data[item],
            mode='lines',
            name=item,
            yaxis='y1'
        ))

    for item in y2:
        fig.add_trace(go.Scatter(
            x=data[x],
            y=data[item],
            mode="lines",
            name=item,
            yaxis='y2',
        ))

    # Update layout for dual axes
    fig.update_layout(
        title=title,
        autosize=True,
        xaxis=dict(title=x_axis),
        yaxis=dict(
            title=y1_axis,
            side="left",
            showgrid=False
        ),
        yaxis2=dict(
            title=y2_axis,
            overlaying="y",
            side="right",
            showgrid=False
        ),
        legend=dict(title='Legend', x=1.2, y=1),
        plot_bgcolor="#252a3b",
        paper_bgcolor="#1E1E2F",
        font=dict(color="white")
    )

    return fig


def horizontal_bar_chart(df, prod_cons, title=None, x_axis=None, y_axis=None):

    df = agg_year_month(df, 'year', 'year_month','mean')
    df_long = df.melt(id_vars=['year'], value_vars=df.columns[1:], value_name=prod_cons)
    df_long = df_long.sort_values(by=['year', prod_cons], ascending=[True, True])
    global_max = df_long[prod_cons].max()

    fig = px.bar(
        df_long,
        x=df_long[prod_cons],
        y=df_long['variable'],
        title=title,
        orientation='h',
        hover_name='variable',
        hover_data=prod_cons,
        animation_frame='year',
        color=prod_cons,
        range_color=[0, global_max],
        range_x=[0, global_max]
    )

    fig.update_layout(
        xaxis_title=x_axis,
        yaxis_title=y_axis,
        plot_bgcolor='#252a3b',
        paper_bgcolor='#1E1E2F',
        font=dict(color='white'),
        transition={"duration": 500, "easing": "cubic-in-out"}
    )

    return fig


def stacked_area_graph(fig, df, y=None, title=None, label=None):

    df = agg_year_month(df, 'year', 'year_month', 'mean')

    if df.shape[1] > 3:
        df['total'] = df.iloc[:, 1:-1].sum(axis=1)
        fig = fig.add_trace(go.Scatter(
            x=df['year'],
            y=df['total'],
            mode='lines',
            stackgroup='one',
            name=label
        ))

    else:
        fig = fig.add_trace(go.Scatter(
            x=df['year'],
            y=df[y],
            mode='lines',
            stackgroup='one',
            name=label
        ))

    fig.update_layout(
        title=title,
        xaxis=dict(title="Year", type='category'),  # Ensure years are treated as categories
        yaxis=dict(title="Value"),
        plot_bgcolor="#252a3b",
        paper_bgcolor="#1E1E2F",
        font=dict(color="white")
    )

    return fig

def agg_year_month(df, agg_by, column, method):

    if agg_by == 'year':
        df[agg_by] = df[column].str[:4]

    if method == 'mean':
        df = df.iloc[:, 1:].groupby([agg_by]).mean(numeric_only=True).reset_index()

    elif method == 'sum':
        df = df.iloc[:, 1:].groupby([agg_by]).sum(numeric_only=True).reset_index()

    return df


def classify_country(df, prod_cons):
    oecd = [
        "Australia", "Austria", "Belgium", "Chile", "Colombia", "Costa Rica",
        "Czech Republic", "Denmark", "Estonia", "Finland", "France",
        "Germany", "Greece", "Hungary", "Iceland", "Ireland", "Israel",
        "Italy", "Japan", "Latvia", "Lithuania", "Luxembourg",
        "Netherlands", "New Zealand", "Norway", "Poland", "Portugal",
        "Slovakia", "Slovenia", "South Korea", "Spain", "Sweden",
        "Switzerland", "Turkey", "United Kingdom"
    ]

    non_oecd = [
        "Afghanistan", "Albania", "Angola", "Antarctica", "Antigua and Barbuda",
        "Argentina", "Armenia", "Aruba", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados",
        "Belarus", "Belize", "Benin", "Bermuda", "Bhutan", "Bolivia", "Bosnia and Herzegovina",
        "Botswana", "Brazil", "British Virgin Islands", "Brunei", "Bulgaria", "Burkina Faso", "Myanmar",
        "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Cayman Islands", "Central African Republic",
        "Chad", "Comoros", "Democratic Republic of the Congo", "Cook Islands", "Ivory Coast",
        "Croatia", "Cuba", "Cyprus", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt",
        "El Salvador", "Eritrea", "Eswatini", "Ethiopia", "Falkland Islands", "Faroe Islands", "Fiji",
        "French Guiana", "French Polynesia", "Gambia", "Georgia", "Ghana", "Gibraltar", "Greenland",
        "Grenada", "Guadeloupe", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras",
        "Hong Kong", "India", "Indonesia", "Jamaica", "Jordan", "Kazakhstan", "Kenya", "Kiribati",
        "Kosovo", "Kyrgyzstan", "Laos", "Lebanon", "Lesotho", "Liberia", "Macau", "Madagascar", "Malawi",
        "Malaysia", "Maldives", "Mali", "Malta", "Martinique", "Mauritania", "Mauritius", "Micronesia",
        "Moldova", "Mongolia", "Montenegro", "Morocco", "Mozambique", "Namibia", "Nauru", "Nepal",
        "New Caledonia", "Nicaragua", "Niger", "Niue", "North Korea", "North Macedonia", "Northern Mariana Islands",
        "Oman", "Pakistan", "Palestine", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines",
        "Qatar", "Reunion", "Romania", "Rwanda", "Saint Helena", "Saint Kitts and Nevis",
        "Saint Lucia", "Saint Pierre and Miquelon", "Saint Vincent and the Grenadines", "Samoa",
        "Sao Tome and Principe", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore",
        "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Sri Lanka", "Sudan", "Suriname",
        "Syria", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "Timor-Leste", "Togo", "Tonga",
        "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "Uganda", "Ukraine", "Uruguay",
        "Uzbekistan", "Vanuatu", "Vietnam", "Yemen", "Zambia", "Zimbabwe"
    ]

    if 'OPEC' in df.columns:
        opec = [
            "Algeria", "Republic of the Congo", "Equatorial Guinea", "Gabon", "Iran", "Iraq",
            "Kuwait", "Libya", "Nigeria", "Saudi Arabia", "United Arab Emirates", "Venezuela"
        ]

    else:
        non_oecd += [
            "Algeria", "Republic of the Congo", "Equatorial Guinea", "Gabon", "Iran", "Iraq",
            "Kuwait", "Libya", "Nigeria", "Saudi Arabia", "United Arab Emirates", "Venezuela"
        ]


    df = agg_year_month(df, 'year', 'year_month','mean')

    # Reshape data into long format
    df_long = df.melt(id_vars=['year'], value_vars=df.columns[1:], var_name='Group', value_name=prod_cons)
    df_long[prod_cons] = df_long[prod_cons]

    # This is for handling dataframe having different datasets
    expanded_rows = []
    for _, row in df_long.iterrows():
        group = row['Group']
        if group == 'OECD':
            countries = oecd
        elif group == 'Non-OECD':
            countries = non_oecd
        elif group == 'OPEC':
            countries = opec
        else:
            countries = [group]

        for country in countries:
            expanded_rows.append({'year': row['year'], 'Country': country, 'Group': group,
                                  prod_cons: row[prod_cons]})

    return pd.DataFrame(expanded_rows)


def map_graph(df, prod_cons, title):

    global_max = classify_country(df, prod_cons)[prod_cons].max()

    fig = px.choropleth(
        classify_country(df, prod_cons),
        locations='Country',
        locationmode='country names',
        color=prod_cons,
        hover_name='Group',
        hover_data={'Group': True, prod_cons: True},
        title=title,
        animation_frame='year',
        range_color=[0, global_max],
        color_continuous_scale=[
        [0.0, "#FFEDA0"],  # Light Yellow
        [0.5, "#FD8D3C"],  # Bright Orange
        [1.0, "#B10026"] # Deep Red
        ]
    )

    # Apply full dark theme styling and remove excess space
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='#1E1E2F',
        font=dict(color='white'),
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor="white",
            showland=True,
            landcolor='#1E1E2F',
            showocean=True,
            oceancolor='#252a3b',
            showlakes=True,
            lakecolor='#252a3b',
            bgcolor='rgba(0,0,0,0)',
            projection_type="equirectangular",
            center={"lat": 10, "lon": 0},
            lonaxis=dict(range=[-180, 180]),
            lataxis=dict(range=[-60, 85])
        ),
        margin=dict(l=0, r=0, t=50, b=0),
    )

    return fig


def cd_chart(df1, df2,prod_cons,title=None, x_axis=None, y_axis=None):
    df_long = agg_year_month(df1, 'year', 'year_month', 'mean')

    df_long['Total Consumption'] = agg_year_month(df1,'year', 'year_month', 'mean').sum(
            numeric_only=True, axis=1).reset_index()[0]

    df_long.iloc[:, 1:-1] = df_long.iloc[:, 1:-1].div(df_long['Total Consumption'], axis=0).mul(
        agg_year_month(df2, 'year', 'year_month', 'mean').iloc[:, 1], axis=0)
    df_long = df_long.drop('Total Consumption', axis=1)
    df_long = df_long.melt(id_vars=['year'], value_vars=df_long.columns[1:],
                           value_name='CO2 Emission from Petroleum Products')

    df_long_2 = agg_year_month(df1, 'year', 'year_month', 'mean')
    df_long_2 = df_long_2.melt(id_vars=['year'], value_vars=df_long_2.columns[1:], value_name=prod_cons)

    df_merge = df_long_2.merge(df_long, how='left', on=['year', 'variable'])
    print(df_merge)

    df_merge = df_merge.sort_values(by=['year', prod_cons], ascending=[True, True])

    fig = px.scatter(
        df_merge,
        x=prod_cons,
        y='CO2 Emission from Petroleum Products',
        size='CO2 Emission from Petroleum Products',
        color='variable',
        text='variable',
        animation_frame='year',
        size_max=120,
        log_x=True
    )

    fig.update_layout(
        plot_bgcolor="#252a3b",
        paper_bgcolor="#1E1E2F",
        title=title,
        font=dict(color="white"),
        xaxis=dict(title=x_axis,range=[0, 2],showgrid=False),
        yaxis=dict(title=y_axis, range=[0, 6],showgrid=False),
        legend=dict(title='Country'),
        transition={"duration": 500, "easing": "cubic-in-out"}
    )

    return fig
