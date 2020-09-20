from features import *
from data_management import *
from datetime import datetime, timedelta
from forecast import *
import numpy as np

transactions = load_data('transactions')

i = 1

ps = get_proper_income_subjects()
cluster = predict_proper_subject_cluster(ps[0])
others = [subject for subject in ps if predict_proper_subject_cluster(subject) == cluster]

subject_transactions = deepcopy(transactions[transactions["party_rk"] == others[i]])
subject_transactions["transaction_dttm"] = subject_transactions["transaction_dttm"].map(to_datetime)
current = subject_transactions["transaction_dttm"].min()

current = current.date() + timedelta(days=30)
current = datetime()

print("Hello!")
print("This example demosntrates the planning, advising and forecasting functionalities of Mercury -- you personal savings advisor.")


print(get_subject_personal_data(others[i]))

forecast_and_advise(others[i], datetime(2019, 10, 1), datetime(2019, 11, 1), datetime(2019, 10, 15), plot=True)
'''
tr = load_data('transactions')


i = 0
#print(tr[tr.party_rk == ps[i]]['transaction_dttm'])

print(compare_subject_to_others(ps[i], 'Супермаркеты', datetime(2019, 9, 1), datetime(2019, 12, 1)))

'''