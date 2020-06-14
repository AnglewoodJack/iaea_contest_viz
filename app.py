# import libraries
import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.io as pio
import matplotlib.pyplot as plt

# white backgraound
pio.templates.default = 'plotly_white'


# define the dataset location
def data_url(filename):
    return os.path.join(os.getcwd(), 'data', filename)


# download all datasets

# countries
list_countries = pd.read_csv(data_url('country_list.csv'), sep=';')
# co2 emissions
co2_init = pd.read_csv(data_url('co2_init.csv'), sep=';')
# GDP
gdp_init = pd.read_csv(data_url('gdp_init.csv'), sep=';')
# electricity consumption
con_init = pd.read_csv(data_url('con_init.csv'), sep=';')
# population
pop_init = pd.read_csv(data_url('pop_init.csv'), sep=';')
# nuclear share
nuc_init = pd.read_csv(data_url('nuc_init.csv'), sep=';')
# renewables share
ren_init = pd.read_csv(data_url('ren_init.csv'), sep=';')
# groupping by neclear share in electricity production
grp_init = pd.read_csv(data_url('group_more.csv'), sep=';')


def select_countries(data, countries=list_countries):
    '''deletes data for countries not in the specified list;
    replaces NaN values and zeros with a low non-null value
    to make possible the use of log scale'''
    na_data = data.fillna(0.01)
    new_data = na_data.replace(0, 0.01)
    dataset = pd.DataFrame()
    for name in countries['TableName']:
        for country in new_data['Country_Name']:
            if name == country:
                dataset = dataset.append(
                    new_data.loc[new_data.Country_Name == country],
                    ignore_index=True)
    return dataset


# apply to all datasets
co2_temp = select_countries(co2_init)
gdp_temp = select_countries(gdp_init)
con_temp = select_countries(con_init)
pop_temp = select_countries(pop_init)
nuc_temp = select_countries(nuc_init)
ren_temp = select_countries(ren_init)
grp_temp = select_countries(grp_init)


# create lists of data for resulting dataset
def get_data_list(data_table):
    temp = []
    for i in range(0, 217):
        temp += data_table.loc[i].tolist()[2:]
    return temp


# creating columns with values by country
countries_column = list_countries.iloc[:, 2].tolist()
new_coun_column = []
for element in countries_column:
    new_coun_column += [element]*55

# creating the column with year values
years_column = list(range(1960, 2015, 1))*217

# create new dataframe
main_data = pd.DataFrame()
# write data
# countries
main_data['Country'] = new_coun_column
# groupes
main_data['Group'] = get_data_list(grp_temp)
# years
main_data['Year'] = years_column
# emissions
main_data['CO2_emissions'] = get_data_list(co2_temp)
# GDP
main_data['GDP'] = get_data_list(gdp_temp)
# electricity consumption
main_data['Electricity_consumption'] = get_data_list(con_temp)
# population
main_data['Population'] = get_data_list(pop_temp)
# nuclear share
main_data['Nuclear_share'] = get_data_list(nuc_temp)
# renewables share
main_data['Renewables_share'] = get_data_list(ren_temp)


# write to a file
main_data.to_csv('processed_data.csv', sep=';')

# read form file
data = pd.read_csv('processed_data.csv', sep=';')


# make a multiselection box for countries to compare
st.sidebar.subheader('Countries to compare')
choice = st.sidebar.multiselect('Select countries',
                                tuple(list_countries['TableName']
                                      .sort_values()), key='0')


# set title for the dashboard
st.title('Role of Nuclear Power in Climate Change Mitigation')
# add markdown text under the dashboard title
st.markdown('Bubble size corresponds to electricity consumption per capita')
# plot tweets counts for selected airlines using plotly histogram chart
if len(choice) > 0:
    # get data based on selection
    choice_country = list_countries[list_countries.TableName.isin(choice)]

    def choice(data, countries=list_countries):
        dataset = pd.DataFrame()
        for name in countries['TableName']:
            for country in data['Country']:
                if name == country:
                    dataset = dataset.append(data.loc[data.Country == country],
                                             ignore_index=True)
        return dataset

    choice_data = choice(data, countries=choice_country)

    fig = px.scatter(choice_data, x='GDP', y='CO2_emissions',
                     animation_frame='Year', animation_group='Country',
                     size='Electricity_consumption',
                     color='Nuclear_share', hover_name='Country',
                     text='Country',
                     labels=dict(Nuclear_share='Nuclear, %',
                                 CO2_emissions='CO2 emissions(metric tons per capita)',
                                 GDP='GDP per capita'), range_color=(0, 80),
                     log_x=True, log_y=True,
                     size_max=45, range_x=[400, 140000], range_y=[0.2, 100],
                     width=900, height=650)

    fig.update_traces(textposition='top center')
    fig.update_traces(textfont=dict(
        family='sans serif',
        size=10,
        color='Black'))

    st.plotly_chart(fig)
