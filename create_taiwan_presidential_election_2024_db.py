import os
import re
import sqlite3
import pandas as pd

class CreateTaiwanPresidentialElection2024DB:
    def __init__(self):
        file_names = os.listdir('data')
        county_names = []
        for file_name in file_names:
            if '.xlsx' in file_name:
                file_name_split = re.split('\\(|\\)', file_name)
                county_names.append(file_name_split[1])
        self.county_names = county_names 

    def tidy_country_dataframe(self, county_name: str):    
        file_path = f'data/總統-A05-4-候選人得票數一覽表-各投開票所({county_name}).xlsx'
        # 跳過合併的標頭並取地區、開票所、候選人
        df = pd.read_excel(file_path,skiprows=[0, 3, 4]).iloc[:, :6]
        # 取出候選人名稱
        candidates_info = list(df.iloc[0, 3:].values)
        df.columns = ['town', 'village', 'polling_place'] + candidates_info
        # 刪除行政區欄位頭尾多餘空白
        df['town'] = df['town'].ffill().str.strip()
        # 刪除因合併多的候選人資訊＆行政區小計而產生的空白列
        df.dropna(inplace=True)
        df['polling_place'] = df['polling_place'].astype(int)
        id_variables = ['town', 'village', 'polling_place']
        melted_df = df.melt(id_vars=id_variables, var_name='candidates_info', value_name='votes')
        melted_df['county'] = county_name
        return melted_df

    def concat_country_dataframe(self):
        country_df = pd.DataFrame()
        for county_name in self.county_names:
            county_df = self.tidy_country_dataframe(county_name)
            country_df = pd.concat([country_df, county_df])
        country_df.reset_index(drop=True,inplace=True)
        
        numbers, candidates = [], []
        for elem in country_df['candidates_info'].str.split('\n'):
            number = re.sub('\\(|\\)', '', elem[0])
            numbers.append(int(number))
            candidate = elem[1] + '/' + elem[2]
            candidates.append(candidate)
        
        presidential_votes = country_df.loc[:,['county', 'town', 'village', 'polling_place']]
        presidential_votes['number'] = numbers
        presidential_votes['candidate'] = candidates
        presidential_votes['votes'] = country_df['votes'].values
        return presidential_votes
    
    def create_database(self):
        presidential_votes = self.concat_country_dataframe()

        polling_places_df = presidential_votes.groupby(['county', 'town', 'village', 'polling_place']).count().reset_index()
        polling_places_df = polling_places_df[['county', 'town', 'village', 'polling_place']].reset_index() # 加一個index欄位做PK
        polling_places_df['index'] = polling_places_df['index'] + 1
        polling_places_df.rename(columns={'index': 'id'},inplace=True)

        candidates_df = presidential_votes.groupby(['number','candidate']).count().reset_index()
        candidates_df = candidates_df[['number', 'candidate']].reset_index()
        candidates_df['index'] = candidates_df['index'] + 1
        candidates_df.rename(columns={'index': 'id'},inplace=True)

        join_keys = ['county', 'town', 'village', 'polling_place']
        votes_df = pd.merge(presidential_votes, polling_places_df, left_on=join_keys, right_on=join_keys,how='left')
        votes_df = votes_df[['id', 'number', 'votes']]
        votes_df.rename(columns={'id': 'polling_place_id', 'number': 'candidate_id'}, inplace=True)

        connection = sqlite3.connect('data/taiwan_presidential_election_2024.db')
        polling_places_df.to_sql('polling_places', con=connection, if_exists='replace', index=False)
        candidates_df.to_sql('candidates', con=connection, if_exists='replace', index=False)
        votes_df.to_sql('votes', con=connection, if_exists='replace', index=False)
        cur = connection.cursor()
        drop_view_sql = '''DROP VIEW IF EXISTS votes_by_village'''
        create_view_sql = '''
        CREATE VIEW votes_by_village AS
        SELECT polling_places.county,
               polling_places.town,
               polling_places.village,
               candidates.number,
               candidates.candidate,
               SUM(votes.votes) AS sum_votes
          FROM votes
          LEFT JOIN polling_places
            ON votes.polling_place_id = polling_places.id
          LEFT JOIN candidates
            ON votes.candidate_id = candidates.id
          GROUP BY polling_places.county,
                   polling_places.town,
                   polling_places.village,
                   candidates.id;
        '''
        cur.execute(drop_view_sql)
        cur.execute(create_view_sql)
        connection.close()

create_taiwan_presidential_election_2024_db = CreateTaiwanPresidentialElection2024DB()
create_taiwan_presidential_election_2024_db.create_database()