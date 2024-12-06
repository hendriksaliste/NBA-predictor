import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, classification_report
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import Lasso
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import Ridge, ElasticNet
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import RandomizedSearchCV
import numpy as np
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


data = pd.read_csv("games_with_team_stats_22.csv")
data['winner'] = (data['winner'] == data['home_team']).astype(int)
# Update the target variable
y = data['winner']
X = data.drop(columns=["winner"])
# Re-split the data with the updated target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

testData = pd.read_csv("merged_games_stats_23.csv")

y_realTest = testData['winner']
X_realTest = testData.drop(columns=["winner"])

scaler = RobustScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
X_realTest_scaled = scaler.fit_transform(X_realTest)

""" elastic_net_param_grid = {
    'alpha': np.logspace(-4, 4, 50),  # Alpha on a logarithmic scale
    'l1_ratio': np.linspace(0.1, 0.9, 50)  # Fine-grained l1_ratio
}

# RandomizedSearchCV for better exploration
elastic_net_random_search = RandomizedSearchCV(
    ElasticNet(), 
    elastic_net_param_grid, 
    scoring='neg_mean_squared_error', 
    cv=5, 
    n_iter=100, 
    random_state=42
)
elastic_net_random_search.fit(X_train_scaled, y_train)

# Best parameters
best_params = elastic_net_random_search.best_params_
print("Best ElasticNet params:", best_params) """


elastic_net_model = ElasticNet(alpha=0.02811768697974228,l1_ratio=0.4591836734693878)
elastic_net_model.fit(X_train_scaled,y_train)
elastic_net_model_pred = elastic_net_model.predict(X_test_scaled)
print("ElasticNet MSE:", mean_squared_error(y_test, elastic_net_model_pred))
print(roc_auc_score(y_test,elastic_net_model_pred))

""" def find_best_cutoff(y_true, y_prob, metric):
    cutoffs = np.arange(0.0, 1.01, 0.01)  # Generate cutoffs from 0 to 1
    best_cutoff = 0.0
    best_metric = 0.0

    for cutoff in cutoffs:
        y_pred = (y_prob >= cutoff).astype(int)
        
        if metric == 'accuracy':
            score = accuracy_score(y_true, y_pred)
        elif metric == 'precision':
            score = precision_score(y_true, y_pred, zero_division=0)
        elif metric == 'recall':
            score = recall_score(y_true, y_pred, zero_division=0)
        elif metric == 'f1':
            score = f1_score(y_true, y_pred, zero_division=0)
        else:
            raise ValueError("Invalid metric. Choose from 'accuracy', 'precision', 'recall', 'f1'.")
        
        if score > best_metric:
            best_metric = score
            best_cutoff = cutoff

    return best_cutoff, best_metric

best_cutoff, best_metric = find_best_cutoff(y_test, elastic_net_model_pred, metric='precision')
print(f"Best Cutoff: {best_cutoff}, Best F1-Score: {best_metric}")
 """
prediction = elastic_net_model.predict(X_realTest.values)
print(prediction)
print(roc_auc_score(y_realTest,prediction))
predCsv = testData[["home_team","away_team","winner"]]
for i in range(len(prediction)):
    if prediction[i] < 0.9:
        prediction[i] = 0
    else:
        prediction[i] = 1
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
team_stats.to_csv("prediction_2324.csv")
team_stats = pd.read_csv("prediction_2324.csv")

team_data = pd.read_csv("NBA_Team_Stats_2022_23.csv")
team_id_to_name = team_data.set_index('TEAM_ID')['TEAM_NAME'].to_dict()
team_stats['Team'] = team_stats['Team'].map(team_id_to_name)

team_stats.to_csv("prediction_2324.csv",index=False)



