import pandas as pd

data = pd.read_csv("updated_games_23.csv")

# Rename columns for better readability
data = data.rename(columns={'home_team_id': 'Team', 'away_team_id': 'AwayTeam', 'winner': 'Winner'})
print(data.head())
# Calculate wins and losses for each team
win_counts = data.groupby('Team')['Winner'].sum().add(
    data.groupby('AwayTeam')['Winner'].apply(lambda x: len(x) - x.sum()), fill_value=0).astype(int)
loss_counts = data.groupby('Team')['Winner'].apply(lambda x: len(x) - x.sum()).add(
    data.groupby('AwayTeam')['Winner'].sum(), fill_value=0).astype(int)

# Combine into a single DataFrame
team_stats = pd.DataFrame({'Wins_actual': win_counts, 'Losses_actual': loss_counts}).sort_index()
team_stats.to_csv("results_2324.csv")
team_stats = pd.read_csv("results_2324.csv")

team_data = pd.read_csv("NBA_Team_Stats_2022_23.csv")
team_id_to_name = team_data.set_index('TEAM_ID')['TEAM_NAME'].to_dict()
team_stats['Team'] = team_stats['Team'].map(team_id_to_name)

team_stats.to_csv("results_2324.csv",index=False)