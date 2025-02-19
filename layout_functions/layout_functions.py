# Import libraries required for building the dashboard
import pandas as pd
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
from numpy.ma.core import resize


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

def line_graph(fig, data,x, y, title = None, x_axis=None, y_axis=None):

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
        plot_bgcolor = '#252a3b',  # Dark background
        paper_bgcolor = '#1E1E2F',  # Dark paper background
        font = dict(color='white')
    )

    return fig


def dual_axis_line_chart(fig, data,x, y1, y2, title = None, x_axis=None, y1_axis=None, y2_axis=None):

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
        legend=dict(title='Legend',x=1.2, y=1),
        plot_bgcolor="#252a3b",
        paper_bgcolor="#1E1E2F",
        font=dict(color="white")
    )

    return fig


def horizontal_bar_chart(df, prod_cons,orientation=None, title=None, x_axis=None, y_axis=None):

    # Convert year_month into year
    df['year'] = df['year_month'].str[:4]


    # Aggregate data by year
    df = df.iloc[:, 1:].groupby(['year']).sum().reset_index()

    df_long = df.melt(id_vars=['year'], value_vars=df.columns[1:-1], value_name=prod_cons)
    df_long = df_long.sort_values(by=['year', prod_cons], ascending=[True, True])
    df_long[prod_cons] = df_long[prod_cons]/12

    # Then take the average = average barrels of oil per day

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

    # Convert year_month into year
    #df['year'] = df['year_month'].str[:4]

    # Aggregate data by year
    df = df.iloc[:, 1:].groupby(['year_month']).sum().reset_index()

    if df.shape[1] > 3:
        df['total'] = df.iloc[:, 1:-1].sum(axis=1)
        fig = fig.add_trace(go.Scatter(
            x=df['year_month'],
            y=df['total'],
            mode='lines',
            stackgroup='one',
            name=label
            ))

    else:
        fig = fig.add_trace(go.Scatter(
            x=df['year_month'],
            y=df[y],
            mode='lines',
            stackgroup='one',
            name=label
        ))

    fig.update_layout(
        title="Yearly Oil Production, Consumption Compared to CO2 Emission from Petroleum Products",
        xaxis=dict(title="Year", type='category'),  # Ensure years are treated as categories
        yaxis=dict(title="Value"),
        plot_bgcolor="#252a3b",
        paper_bgcolor="#1E1E2F",
        font=dict(color="white")
    )

    return fig


def classify_country(df, prod_cons):

    oecd = [
        "Australia", "Austria", "Belgium", "Chile", "Colombia", "Costa Rica",
        "Czech Republic", "Denmark", "Estonia", "Finland", "France",
        "Germany", "Greece", "Hungary", "Iceland", "Ireland", "Israel",
        "Italy", "Japan", "Latvia", "Lithuania", "Luxembourg",
        "Netherlands", "New Zealand", "Norway", "Poland", "Portugal",
        "Slovakia", "Slovenia", "South Korea", "Spain", "Sweden",
        "Switzerland", "Turkey", "United Kingdom", "United States"
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

    # Convert year_month into year
    df['year'] = df['year_month'].str[:4]
    df = df.sort_values(by='year', ascending=False)

    # Aggregate data by year
    df = df.iloc[:, 1:].groupby(['year']).sum().reset_index()

    # Reshape data into long format
    df_long = df.melt(id_vars=['year'], value_vars=df.columns[1:-1], var_name='Group', value_name=prod_cons)
    df_long[prod_cons] = df_long[prod_cons]/12


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
        range_color=[0, global_max]
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
