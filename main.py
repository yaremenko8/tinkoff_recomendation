from features import *
from data_management import *
from datetime import datetime, timedelta
from forecast import *
import numpy as np

try:
    transactions = load_data('transactions')
except:
    print("ERROR!!! The program REQUIRES /data directory to be unpacked for it to be run. See readme.")
    print("Exiting...")

i = 1

ps = get_proper_income_subjects()
cluster = predict_proper_subject_cluster(ps[0])
others = [subject for subject in ps if predict_proper_subject_cluster(subject) == cluster]

subject_transactions = deepcopy(transactions[transactions["party_rk"] == others[i]])
subject_transactions["transaction_dttm"] = subject_transactions["transaction_dttm"].map(to_datetime)
current = subject_transactions["transaction_dttm"].min()

current = current.date() + timedelta(days=30)
current = datetime(year = current.year, month = current.month, day=1)

goal = 40000

print("Hello!")
print("This example demosntrates the planning, advising and forecasting functionalities of Mercury -- you personal savings advisor.")

print()
print("Meet Alexander. Alexander is 35 year married male with no kids and an income of approximately 60000 RUR.")
print("Alexander wants to save up %d RUR by the end of the month. However it's hard to keep track of day-to-day expenses without a personal financial advisor. So Alexander employs the help of Mercury, a software product named after the Roman god of traders, designed to help him in his endeavours. He tells Mercury about his goals. Immediately Mercury tells Alexander about the trends of his current spending habits and how much he would want to change them if he is to pursue his goals." % goal)
print('Press ENTER to see find out what Mercury told him...')
input()

forecast, daily, adjustment = forecast_and_advise(others[i], current, current + timedelta(days=15), current + timedelta(days=30), goal=goal, plot=True)

print('"Alexander, you will achieve your goal if you start spending %.1f RUR less daily. Actually if you carry on with your spendings the way you normally do and keep spending about %.1f RUR a day, you\'ll only have %.1f RUR by the end of this month"' % (adjustment, daily, forecast))

print('"But how do I cut down my expenses?"')

print('"Worry not, puny mortal. I will use my advanced multidimensional cluster insights to aid you in you endeavour."')
print("Press ENTER to witness the might of multidimensional cluster insights...")
input()
print("This may take some time...")

res = compare_subject_to_others(ps[i], 'Супермаркеты', datetime(2019, 9, 1), datetime(2019, 12, 1)))

print("")