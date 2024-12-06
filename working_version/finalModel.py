
import pandas as pd
from sklearn.linear_model import ElasticNet
from sklearn.preprocessing import RobustScaler

#format player data for the 2022 2023 season
player_data = pd.read_csv("NBA_Player_Stats_2022_23_WS.csv")

needed_data = player_data[["Win_Shares","TEAM_ID"]]
winshare_data = needed_data.groupby(["TEAM_ID"]).mean()
data = pd.read_csv("games_with_team_stats_22.csv")

data['winner'] = (data['winner'] == data['home_team']).astype(int)

# Merge the win share data for home and away teams
data = data.merge(winshare_data, left_on='home_team', right_on='TEAM_ID', how='left')
data.rename(columns={'Win_Shares': 'home_winshare'}, inplace=True)


data = data.merge(winshare_data, left_on='away_team', right_on='TEAM_ID', how='left')
data.rename(columns={'Win_Shares': 'away_winshare'}, inplace=True)

# Reorganize columns: home_winshare after home_L, and away_winshare after away_L
home_cols_order = list(data.columns[:6]) + ['home_winshare'] + list(data.columns[6:])
away_cols_order = home_cols_order[:-1] + ['away_winshare'] + home_cols_order[-1:]
data = data[away_cols_order]

# Create the training datasets for the model
y = data['winner']
X = data.drop(columns=["winner"])

#format 23/24 player data
player_data_test = pd.read_csv("Player_data_2023_24.csv")

needed_data_test = player_data_test[["Win_Shares","TEAM_ID"]]
winshare_data_test = needed_data_test.groupby(["TEAM_ID"]).mean()
testData = pd.read_csv("merged_games_stats_23.csv")

# Merge the win share data for home and away teams
testData = testData.merge(winshare_data_test, left_on='home_team', right_on='TEAM_ID', how='left')
testData.rename(columns={'Win_Shares': 'home_winshare'}, inplace=True)

testData = testData.merge(winshare_data, left_on='away_team', right_on='TEAM_ID', how='left')
testData.rename(columns={'Win_Shares': 'away_winshare'}, inplace=True)

# Reorganize columns: home_winshare after home_L, and away_winshare after away_L
home_cols_order = list(testData.columns[:6]) + ['home_winshare'] + list(testData.columns[6:])
away_cols_order = home_cols_order[:-1] + ['away_winshare'] + home_cols_order[-1:]
testData = testData[away_cols_order]

#Create the test datasets wtih the 2023 2024 data
y_realTest = testData['winner']
X_realTest = testData.drop(columns=["winner"])

#Scale the variables
scaler = RobustScaler()
X_train_scaled = scaler.fit_transform(X)

#Creating the elastic net model
elastic_net_model = ElasticNet(alpha=0.02811768697974228,l1_ratio=0.4591836734693878)
elastic_net_model.fit(X_train_scaled,y)

#Predicting the 2023 2024 season
prediction = elastic_net_model.predict(X_realTest.values)
predCsv = testData[["home_team","away_team","winner"]]
prediction = (prediction >= 0).astype(int)
predCsv["winner"] = prediction

# Rename columns for better readability
data = predCsv.rename(columns={'home_team': 'Team', 'away_team': 'AwayTeam', 'winner': 'Winner'})

# Calculate wins and losses for each team
win_counts = data.groupby('Team')['Winner'].sum().add(
    data.groupby('AwayTeam')['Winner'].apply(lambda x: len(x) - x.sum()), fill_value=0).astype(int)
loss_counts = data.groupby('Team')['Winner'].apply(lambda x: len(x) - x.sum()).add(
    data.groupby('AwayTeam')['Winner'].sum(), fill_value=0).astype(int)

# Combine into a single DataFrame
team_stats = pd.DataFrame({'Wins_pred': win_counts, 'Losses_pred': loss_counts}).sort_index()
#Weird things because the dataframe structure is wonky
team_stats.to_csv("prediction_2324.csv")
team_stats = pd.read_csv("prediction_2324.csv")

team_data = pd.read_csv("NBA_Team_Stats_2022_23.csv")
team_id_to_name = team_data.set_index('TEAM_ID')['TEAM_NAME'].to_dict()
team_stats['Team'] = team_stats['Team'].map(team_id_to_name)

team_stats.to_csv("prediction_2324.csv",index=False)