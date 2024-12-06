import pandas as pd

results = pd.read_csv("results_2324.csv")
prediction = pd.read_csv("prediction_2324.csv")

actWins = results["Wins_actual"]
actLoss = results["Losses_actual"]
predWins = prediction["Wins_pred"] 

win_perc_actual = (actWins/82).rename("Win_percentage_actual")
win_perc_pred = (predWins/82).rename("Win_percentage_predicted")
win_dif = abs(actWins - predWins).rename("Win_difference")
win_perc_dif = abs(win_perc_actual-win_perc_pred).rename("Win_percentage_differece")


modelPrediciton = pd.concat([prediction,win_perc_pred,actWins,actLoss,win_perc_actual,win_dif,win_perc_dif], axis = 1)

modelPrediciton.to_excel("results.xlsx",index=False)
