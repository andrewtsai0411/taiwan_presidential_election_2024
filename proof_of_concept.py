import sqlite3
import numpy as np
import pandas as pd

def calculate_cosine_similarity():
    connection = sqlite3.connect('data/taiwan_presidential_election_2024.db')
    votes_by_village = pd.read_sql('SELECT * FROM votes_by_village;',con=connection)
    connection.close()

    # 全國得票率
    total_votes = votes_by_village['sum_votes'].sum()
    country_percentage = votes_by_village.groupby('number')['sum_votes'].sum() / total_votes
    vector_a = country_percentage.values

    # 村鄰里得票率
    groupby_variables = ['county', 'town', 'village']
    village_total_votes = votes_by_village.groupby(groupby_variables)['sum_votes'].sum().reset_index()
    merged = pd.merge(votes_by_village, village_total_votes, on=groupby_variables, how='left')
    merged['village_percentage'] = merged['sum_votes_x'] / merged['sum_votes_y']
    merged = merged[['county', 'town', 'village', 'number', 'village_percentage']]

    pivot_df = merged.pivot(index=['county', 'town', 'village'], columns='number', values='village_percentage').reset_index()
    pivot_df.rename_axis(None, axis=1,inplace=True)

    # 計算餘弦相似度
    cosine_similarities = []
    length_vector_a = pow((vector_a**2).sum(), .5)
    for row in pivot_df.iterrows():
        vector_bi = np.array([row[1][1], row[1][2], row[1][3]])
        vector_a_dot_vector_bi = np.dot(vector_a, vector_bi)
        length_vector_bi = pow((vector_bi**2).sum(), .5)
        cosine_similarity = vector_a_dot_vector_bi / (length_vector_a * length_vector_bi)
        cosine_similarities.append(cosine_similarity)

    cosine_similarity_df = pivot_df.iloc[:,:]
    cosine_similarity_df['cosine_similarity'] = cosine_similarities
    cosine_similarity_df = cosine_similarity_df.sort_values(['cosine_similarity', 'county', 'town', 'village'],ascending=[False, True, True, True])
    cosine_similarity_df = cosine_similarity_df.reset_index(drop=True).reset_index()
    # 以index欄位當作rank
    cosine_similarity_df['index'] = cosine_similarity_df['index'] + 1
    column_names_to_revise ={'index': 'similarity_rank', 1:'candidate_1', 2: 'candidate_2', 3: 'candidate_3'}
    cosine_similarity_df = cosine_similarity_df.rename(columns=column_names_to_revise)
    return vector_a, cosine_similarity_df

def filter_county_town_village(df, county_name: str, town_name: str, village_name: str):
    county_condition = df['county'] == county_name
    town_condition = df['town'] == town_name
    village_condition = df['village'] == village_name
    return df[county_condition & town_condition & village_condition]

cosine_similarity_tuple = calculate_cosine_similarity()