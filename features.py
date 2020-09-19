from datetime import datetime
from data_management import get_subjects, load_data
import numpy as np
import pandas as pd
from misc import cached

def to_datetime(s):
    return datetime(*list(map(int, s.split('-'))))

def get_subject_accounts(subject, account_x_balance=None):
    if account_x_balance is None:
        account_x_balance = load_data("account_x_balance")
    return set(account_x_balance[account_x_balance["party_rk"] == subject]["account_rk"])
        
@cached
def get_subject_income_estimate(subject, account_x_balance=None, transactions=None):
    if account_x_balance is None:
        account_x_balance = load_data("account_x_balance")
    if transactions is None:
        transactions = load_data("transactions")
    income_sample = []
    subject_transactions = transactions[transactions["party_rk"] == subject]
    subject_balance = account_x_balance[account_x_balance["party_rk"] == subject]
    subject_accounts = get_subject_accounts(subject, account_x_balance)
    recorded_months = set(zip(subject_balance['prev_month'].to_list(), subject_balance['cur_month'].to_list()))
    for month in recorded_months:
        current_change = subject_balance[subject_balance['prev_month'] == month[0]]['balance_chng'].sum() 
        current_transaction_mask = (subject_transactions['transaction_dttm'].map(to_datetime) < to_datetime(month[1])) & \
                                   (subject_transactions['transaction_dttm'].map(to_datetime) > to_datetime(month[0]))
        current_spendings = subject_transactions[current_transaction_mask]['transaction_amt_rur'].sum()
        income_sample.append(current_spendings + current_change) # sign?
    return np.median(income_sample)
    
#discrete -- strings    
@cached
def get_subject_personal_data(subject, party_x_socdem=None):
    if party_x_socdem is None:
        party_x_socdem = load_data("party_x_socdem")
    subject_socdem = dict(party_x_socdem[party_x_socdem["party_rk"] == subject].iloc[0])
    subject_socdem["income"] = get_subject_income_estimate(subject)
    subject_socdem["region_flg"] = str(subject_socdem["region_flg"])
    subject_socdem["children_cnt"] = str(subject_socdem["children_cnt"])
    del subject_socdem["party_rk"]
    return subject_socdem


#could be concatenated
def gather_data_set(feature_set, subjects=None):
    if subjects is None:
        subjects = get_subjects()
    return pd.DataFrame(list(map(feature_set, subjects)))

def vectorize(data_set_):
    data_set = data_set_.dropna()
    print(" | ".join(data_set.columns))
    sub_arrays = []
    for column in data_set.columns:
        discrete = type(dict(data_set.iloc[0])[column]) is str
        if not discrete:
            sub_arrays.append(np.array([data_set[column].to_numpy()]).T)
        else:
            values = data_set[column].to_list()
            value_kinds = list(set(values))
            repr_vectors = np.eye(len(value_kinds))
            final = [repr_vectors[value_kinds.index(value)] for value in values]
            sub_arrays.append(np.array(final))
            for value_kind, repr_vector in zip(value_kinds, list(repr_vectors)):
                print("%s :: %s -> %s" % (column, value_kind, repr_vector))
    return np.concatenate(sub_arrays, axis=1)


def get_subject_spendings_data(subject, mode='median_of_monthly', transactions=None):
    if transactions is None:
        transactions = load_data("transactions")
    subject_transactions = transactions[transactions["party_rk"] == subject]
    if mode == 'median_of_monthly':
        pass
    else:
        raise NotImplementedError


















