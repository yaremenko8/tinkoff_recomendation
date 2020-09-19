from datetime import datetime
from data_management import get_subjects, load_data


def get_subject_accounts(subject, account_x_balance=None):
    if account_x_balance is None:
        account_x_balance = load_data("account_x_balance")
    return set(account_x_balance[account_x_balance["party_rk"] == subject]["account_rk"])
        
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
        current_change = subject_balance[subject_balance['prev_month'] == month[0]].sum() 
        current_transactions = (subject_transactions['transaction_dttm'].map(datetime) < datetime(month[1])) & \
                               (subject_transactions['transaction_dttm'].map(datetime) > datetime(month[0]))
    
    