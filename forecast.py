from data_management import *
from features import *
from datetime import timedelta
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from copy import deepcopy
import matplotlib.dates as mdates


def forecast_and_advise(proper_subject, from_, till, now, goal=0, plot=False):
    income = get_subject_income_estimate(proper_subject)
    transactions = load_data("transactions")
    subject_transactions = deepcopy(transactions[transactions.party_rk == proper_subject])
    subject_transactions["transaction_dttm"] = subject_transactions["transaction_dttm"].map(to_datetime)
    current_transactions = subject_transactions[(subject_transactions["transaction_dttm"] <= now) & \
                                                (subject_transactions["transaction_dttm"] >= from_)]    
    current_transactions_sorted = current_transactions.sort_values("transaction_dttm").copy()
    y = income - np.cumsum(current_transactions_sorted["transaction_amt_rur"].to_numpy())
    x = np.array([list(map(lambda x: (x.to_pydatetime() - from_).total_seconds(), current_transactions_sorted["transaction_dttm"].tolist()))]).T
    reg = LinearRegression(fit_intercept=False).fit(x, y - income)
    seconds = (till - from_).total_seconds()
    days = seconds // (60 * 60 * 24)
    forecast = reg.predict([[(till - from_).total_seconds()]])[0] + income
    daily = (income - forecast) / days
    adjustment = (goal - forecast) / days
    # adjustemnt = np.min(adjustment, 0)
    if plot:
        plt.style.use("seaborn-pastel")
        x_dates = [from_ + timedelta(seconds=int(value)) for value in x.T[0]]
        fig, ax = plt.subplots()
        ax.scatter([from_] + x_dates, np.concatenate(([income], y)), label='balance')
        date_range = [from_ + timedelta(seconds=int(value)) for value in np.linspace(0, seconds, int(seconds) + 1)]
        ax.plot(date_range[::3600], reg.predict(np.array([np.linspace(0, seconds, int(seconds) + 1)]).T[::3600]) + income, label="current trend (%.0f per day)" % daily)
        ax.plot(date_range, [goal] * (int(seconds) + 1), label="goal")
        ax.plot(date_range[::3600], np.linspace(income, goal, int(seconds) + 1)[::3600], label="Optimal trend (%0.f per day)" % (daily - adjustment))
        #plt.xlim(date_range[0], date_range[1])
        ax.legend()
        ax.locator_params(nbins=5, axis='x')
        plt.xlim(from_, till)
        #plt.ylim(-30000, 15000)
        myFmt = mdates.DateFormatter('%d-%m')
        ax.xaxis.set_major_formatter(myFmt)        
        plt.ylabel("Savings (RUR)")
        plt.xlabel("Date")
        plt.title("Current trend vs Optimal trend as of %s" % str(now))
        plt.show()
    return forecast, daily, -adjustment
        
    