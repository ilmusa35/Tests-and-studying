"""
In this project, I will explore salary data for Data Scientists around the world.
As a result, my goal is to create a tool that can assist in choosing the best locations and specializations for Data Scientists.
For this project I used dataset from Kaggle - https://www.kaggle.com/datasets/iamsouravbanerjee/data-science-salaries-2023

Since I'm using Dash, I opted for Plotly over Seaborn and Matplotlib for graphical display due to its higher compatibility.
"""

from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

pd.plotting.register_matplotlib_converters()


# This function makes our dataset ready for displaying on the dashboard
def data_preprocessing():
    file_filepath = "v3_Latest_Data_Science_Salaries.csv"
    full_df = pd.read_csv(file_filepath)

    # After a brief overview, we can see that the columns 'Experience Level' and 'Expertise Level' contain the same
    # information(Senior=Expert, Mid=Intermediate, Entry=Junior, and so on).
    # Additionally, for the purpose of comparison, I will only use the USD equivalent of the salary.
    # Therefore, I can drop the 'Employment Type', 'Expertise Level', 'Salary', and 'Salary Currency' columns.

    main_df = full_df.copy()
    main_df.drop(labels=["Employment Type", "Expertise Level", "Salary", "Salary Currency"], axis=1, inplace=True)
    main_df = main_df.rename(columns={'Salary in USD': 'Salary'})

    # First of all, let's find out which job titles have a higher salary (across each level)
    groupby_title = main_df.groupby(["Job Title", "Experience Level"])['Salary'].mean()
    groupby_title = pd.DataFrame(groupby_title)
    groupby_title = groupby_title.reset_index()

    # The next dataframe will be used for looking at the salary over time
    groupby_year = main_df.groupby(["Experience Level", "Year"])['Salary'].mean()
    groupby_year = pd.DataFrame(groupby_year)
    groupby_year = groupby_year.reset_index()

    # This dataframe will help us understand, where is the best country for Data Scientists
    groupby_country = main_df.groupby(["Employee Residence", "Experience Level"])['Salary'].mean()
    groupby_country = pd.DataFrame(groupby_country)
    groupby_country = groupby_country.reset_index()

    return main_df, groupby_title, groupby_year, groupby_country


df, groupby_title, groupby_year, groupby_country = data_preprocessing()

# Take a CSS style recommended by the official website.
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)

# Let's create a structure for the dashboard.
app.layout = html.Div([
    html.Div(className='row', children='Explore the salary of Data Scientists.',
             style={'textAlign': 'center', 'color': 'red', 'fontSize': 50}),
    html.Div(className='row', children='Choose the best country and specialization and compare salary expectations',
             style={'textAlign': 'center', 'color': 'blue', 'fontSize': 30}),
    html.Div(className='row', children='Choose the experience level you are interested in:',
             style={'textAlign': 'left', 'color': 'black', 'fontSize': 20}),
    html.Div(className='row', children=[
        dcc.RadioItems(options=['Executive', 'Senior', 'Mid', 'Entry'], value='Mid', id='controls-and-radio-item')]),
    html.Div(className='row', children=[
            html.Div(className='six columns', children=[dcc.Graph(figure={}, id='box-graph')]),
            html.Div(className='six columns', children=[dcc.Graph(figure={}, id='line-graph')])
        ]),
    html.Div(className='row', children=[
        html.Div(className='six columns', children=[dcc.Graph(figure={}, id='scatter-geo-plot')]),
        html.Div(className='six columns', children=[dcc.Graph(figure={}, id='histogram-graph')])
        ]),
    html.Div(className='row', children='The next two graphs do not depend on the filter,'
                                       ' and will help you more fully navigate your choice',
             style={'textAlign': 'center', 'color': 'blue', 'fontSize': 30}),
    html.Div(className='row', children=[dcc.Graph(figure={}, id='heatmap')]),
    html.Div(className='row', children=[dcc.Graph(figure={}, id='strip-graph')])
])


# Add controls to build the interaction
@callback(
    Output(component_id='box-graph', component_property='figure'),
    Output(component_id='line-graph', component_property='figure'),
    Output(component_id='scatter-geo-plot', component_property='figure'),
    Output(component_id='histogram-graph', component_property='figure'),
    Output(component_id='heatmap', component_property='figure'),
    Output(component_id='strip-graph', component_property='figure'),
    Input(component_id='controls-and-radio-item', component_property='value')
)
def update_graph(level_chosen):

    new_df = groupby_title[groupby_title['Experience Level'] == level_chosen]

    # Update the box plot
    box_fig = px.box(new_df, x='Salary', y='Experience Level', title=f'Salary Distribution for {level_chosen} '
                                                                     f'(hover over for details)')

    # Update the line chart
    line_df = groupby_year[groupby_year['Experience Level'] == level_chosen]
    line_fig = px.line(line_df, x='Year', y='Salary', title=f'Salary Year-by-Year for {level_chosen}')

    # Update the scatter_geo plot
    scatter_geo_df = groupby_country[groupby_country['Experience Level'] == level_chosen]
    scatter_geo_fig = px.scatter_geo(
        scatter_geo_df,
        locations='Employee Residence',
        locationmode='country names',
        color='Salary',
        size='Salary',
        hover_name='Employee Residence',
        title=f'Salary Distribution by Country for {level_chosen} (hover over and scroll for details)'
    )
    scatter_geo_fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='equirectangular'
        ),
        height=500,
        width=1000
    )

    new_df1 = new_df.sort_values('Salary', ascending=False).head(10)
    new_df1 = new_df1.sort_values('Salary')
    histogram_fig = px.histogram(new_df1, x='Salary', y='Job Title', histfunc='avg',
                                 title=f'Top-10 Titles for {level_chosen} (will help you to find best specialization)')

    # Update the heatmap
    heatmap_fig = go.Figure(data=go.Heatmap(
        z=groupby_country['Salary'],
        x=groupby_country['Employee Residence'],
        y=groupby_country['Experience Level'],
        colorscale='Viridis',
        colorbar=dict(title='Salary')
    ))
    heatmap_fig.update_layout(
        title='Heatmap by countries (It looks like a lot of data is missing, but dont give up! '
              'You are a Data Scientist, and you can definitely find value in this data!)'
    )

    # Update the strip plot
    strip_fig = px.strip(groupby_title, x='Salary', y='Experience Level', title=f'Salary distribution by levels ('
                                                                                f'take a closer look at what awaits you)')
    strip_fig.update_layout(
        xaxis=dict(
            title_text='Salary',
            title_standoff=10
        ),
        yaxis=dict(
            title_text='Experience Level',
            title_standoff=10
        )
    )

    return box_fig, line_fig, scatter_geo_fig, histogram_fig, heatmap_fig, strip_fig,


if __name__ == '__main__':
    app.run(debug=True)
