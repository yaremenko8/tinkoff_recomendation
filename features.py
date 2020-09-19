from datetime import datetime, timedelta as td
from data_management import get_subjects, load_data
import numpy as np
import pandas as pd
from misc import cached
import scipy.stats as stats

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

@cached
def get_proper_income_subjects():
    proper_subjects = []
    subjects = get_subjects()
    for subject in subjects:
        income = get_subject_income_estimate(subject)
        if income == income and income >= 5000:
            proper_subjects.append(subject)
    return proper_subjects

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


def preprocess_peronal(vds):
    new_vds = np.copy(vds)
    new_vds = np.array([row for row in new_vds if row[-1] >= 5000])
    new_vds.T[-1] = np.log(new_vds.T[-1] / 1000) / np.log(2)
    new_vds = scale(new_vds, with_mean=False)
    return new_vds

@cached
def predict_proper_subject_cluster(proper_subject):
    i = get_proper_income_subjects().index(proper_subject)
    return load_data("DBSCAN_clusters")[i]

categories = {'Искусство', 'Одежда/Обувь', 'Дом/Ремонт', 'Развлечения', 'Книги', 'Частные услуги', 'Сувениры', 'Музыка', 'Другое', 'Финансовые услуги', 'Авиабилеты', 'Спорттовары', 'Наличные', 'Транспорт', 'Фаст Фуд', 'Фото/Видео', 'Красота', 'Связь/Телеком', 'Турагентства', 'Разные товары', 'Цветы', 'Кино', 'Рестораны', 'Сервисные услуги', 'Аптеки', 'Госсборы', 'Ж/д билеты', 'Отели', 'Автоуслуги', 'Аренда авто', 'Супермаркеты', 'Образование', 'НКО', 'Duty Free', 'Медицинские услуги', 'Животные', 'Топливо'}
@cached
def get_subject_spendings_data(subject, mode='median_of_monthly', transactions=None):
    if transactions is None:
        transactions = load_data("transactions")
    subject_transactions = transactions[transactions["party_rk"] == subject]
    if mode == 'median_of_monthly':
        subject_transactions = transactions[transactions["party_rk"] == subject]
        subject_transactions["transaction_dttm"] = subject_transactions["transaction_dttm"].map(to_datetime)
        current = datetime(subject_transactions["transaction_dttm"].min())
        final = datetime(subject_transactions["transaction_dttm"].max())
        current += td(days=30)
        spendings_by_month = []
        while current < final:
            monthly_spendings = {}
            transactions_of_this_month = \
                subject_transactions[(subject_transactions["transaction_dttm"] <= current) & \
                                     (subject_transactions["transaction_dttm"] > (current - td(days=30)))]
            for category in categories:
                monthly_spendings[category] = \
                    transactions_of_this_month[transactions_of_this_month["category"] == category]["transaction_amt_rur"].sum()
            spendings_by_month.append(monthly_spendings)
            current += td(days=30)
        spendings_data = {}
        for category in categories:
            spendings_data[category] = np.median([monthly[category] for monthly in spendings_by_month])
        return spendings_data
    else:
        raise NotImplementedError
    
        
@cached
def get_subject_actual_spendings(subject, start, end, transactions=None):
    if transactions is None:
        transactions = load_data("transactions")
    subject_transactions = transactions[transactions["party_rk"] == subject]
    subject_transactions["transaction_dttm"] = subject_transactions["transaction_dttm"].map(to_datetime)
    spendings = {}
    transactions_of_given_period = \
        subject_transactions[(subject_transactions["transaction_dttm"] <= end) & \
                             (subject_transactions["transaction_dttm"] > start)]
    for category in categories:
        spendings[category] = \
            transactions_of_given_period[transactions_of_given_period["category"] == category]["transaction_amt_rur"].sum()
        spendings[category] *= 30 / (end - start).days
    return spendings


def get_mode_enterprise_by_period(subject, category, start, end, transactions=None):
    if transactions is None:
        transactions = load_data("transactions")
    transactions_of_given_period = \
        subject_transactions[(transactions["transaction_dttm"] <= end) & \
                             (transactions["transaction_dttm"] > start)]
    return __uncached_get_mode_enterprise(subject, category, transactions=transactions_of_given_period)


def __uncached_get_mode_enterprise(subject, category, transactions=None):
    if transactions is None:
        transactions = load_data("transactions")
    subject_transactions = transactions[transactions["party_rk"] == subject]
    subject_transactions_in_category = subject_transactions[subject_transactions["category"] == category]
    return stats.mode(subject_transactions_in_category["merchant_group_rk"])[0][0]

#could be improved to return n-mode instead
@cached
def get_mode_enterprise(subject, category, transactions=None):
    if transactions is None:
        transactions = load_data("transactions")
    subject_transactions = transactions[transactions["party_rk"] == subject]
    subject_transactions_in_category = subject_transactions[subject_transactions["category"] == category]
    return stats.mode(subject_transactions_in_category["merchant_group_rk"])[0][0]
    
@cached   
def compare_subject_to_others(proprer_subject, category, start, end):
    cluster = predict_proper_subject_cluster(proper_subject)
    proper_subjects = get_proper_income_subjects()
    others = [subject in proper_subjects if predict_proper_subject_cluster(subject) == cluster]
    spendings = get_subject_actual_spendings(proper_subject, start, end)[category]
    spendings_of_others = [get_subject_spendings_data(subject)[category] for subject in others]
    median = np.median(spendings_of_others)
    if spendings * 0.98 <= median:
        return None
    else:
        submedian_others = [subject for subject in others if get_subject_spendings_data(subject)[category] < median]
        spendings_of_submedian_others = [get_subject_spendings_data(subject)[category] for subject in submedian_others]
        current_preference = get_mode_enterprise_by_period(proper_subject, category, start, end)
        submedian_preferences = [get_mode_enterprise(subject, category) for subject in submedian_others]
        submedian_preference_counts = \ 
            {preference : submedian_preferences.count(preference) for preference in set(submedian_preferences) if preference != -1}
        most_favoured = sorted(submedian_preference_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        print(most_favoured)
        most_favoured = list(dict(most_favoured))
        most_favoured_assessment = []
        for enterprise in most_favoured:
            submedian_others_enterprise_spendings = np.array(spendings_of_submedian_others)[np.array(submedian_preferences) == enterprise]
            most_favoured_assesment.append(np.mean(submedian_others_enterprise_spendings))
        return most_favoured[np.argmin(most_favoured_assesment)], spendings - np.min(most_favoured_assessment)
        















