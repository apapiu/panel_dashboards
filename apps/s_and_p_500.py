#!/usr/bin/env python
# coding: utf-8

# App that looks at the variation in the Return for the SP500 stock index.
import numpy as np
import panel as pn
import pandas as pd
import hvplot.pandas
import panel.widgets as pnw
pn.extension()

df = pd.read_csv("data/snp500.csv", parse_dates=["Date"])
snp = df.set_index("Date").sort_index()["Close"]

# Computing the Annualized return:
# 
# To get the `N = num_years` we divide number of trading days by 250:
# 
# $$(1+r)^N = 1+p$$
# $$r = (1+p)^{(1/N)} - 1$$

def compute_perc_change(snp, time_range = 100, feat="Percent Change"):
    
    num_years = time_range/250    
    shifted_snp = snp.shift(time_range)
    shifted_snp.name = "Close_lag"

    tmp = pd.concat([snp,shifted_snp], 1)
    tmp["Percent Change"] = ((tmp["Close"] - tmp["Close_lag"])/tmp["Close_lag"])
    tmp["Annualized Return"] = ((1 + tmp["Percent Change"])**(1/num_years) - 1)*100
    
    percentile_outcomes = tmp[feat].quantile(np.arange(0, 1, 0.01))
    
    return tmp, percentile_outcomes

def plot_return_by_investment_date(tmp, feat="Annualized Return", time_range = 100):
    
    #shift back to have the date be the start of investment not the end
    #also average over two weeks for faster display time
    ann_return = tmp["Annualized Return"].shift(-time_range).groupby(tmp.index.floor("14D")).mean()
    return_by_time = ann_return.hvplot.line(title = "Return by Investment Date Start",
                                            grid=True)
    return return_by_time


def plot_hist(tmp, feat="Annualized Return"):
    plots =  tmp.hvplot.hist(feat, bins = 30, 
                          title="Distribution of Possible Returns",
                          xlim = (-30, 35),
                          padding = (0, 0.05)
                         )
    
    return plots
              

def plot_perc_change(percentile_outcomes, feat="Annualized Return"):
    
    t = percentile_outcomes.reset_index()
    t["Percentile"] = t.index
    perc_plot = t.hvplot.line(x="Percentile",
                              y=feat, 
                              title="Percentiles of Possible Returns",
                              ylim = (-20, 30),
                              grid=True)
    
    return perc_plot

def get_text_blurb(outcomes, time_range):
    
    avg_return = outcomes["Annualized Return"].mean()
    lb, median_return, ub = outcomes["Annualized Return"].quantile([0.05, 0.5, 0.95])
    
    returns = outcomes["Annualized Return"].dropna()
    proba_of_losing = 100*(((returns < 0).sum())/returns.shape[0])
    proba_of_losing = np.round(proba_of_losing, 2)

    text_desc = """The average annualized return for this time horizon is **{avg_return}** percent. <br>
                   The median annualized return is **{median_return}** percent. <br>
                   The 5th and 95th percentiles are **{lb}** and **{ub}** percent. <br>
                   Historically there has been a **{proba_of_losing}** percent probability of having a negative return
                   after {time_range} years invested in the S&P 500.
                """.format(avg_return=np.round(avg_return, 2),
                           median_return=np.round(median_return, 2),
                           lb=np.round(lb, 2),
                           ub=np.round(ub, 2),
                           proba_of_losing = proba_of_losing,
                           time_range = np.round(time_range, 2))
    
    return text_desc

time_range = pn.widgets.FloatSlider(start = 1,
                                    step = 0.05,
                                    end=40, 
                                    name='Years in the Market', 
                                    value=1)

panelz = pn.Column(pn.Column(pn.WidgetBox('#S&P 500 Historical Returns Simulator', 
                                          time_range,
                                          None,
                                          width = 500)), 
                   pn.Row(None), 
                   pn.Row(None),
                   pn.Row(None))

def update(event):
    feat = "Percent Change"
    feat = "Annualized Return"
    
    time_range_days = int(time_range.value*250)
    
    outcomes, percentile_outcomes = compute_perc_change(snp, 
                                                        time_range=time_range_days,
                                                        feat = feat)
    
    text_desc = get_text_blurb(outcomes, time_range.value)
    
    panelz[0][0][2] = text_desc
    
    panelz[1][0] = plot_perc_change(percentile_outcomes, feat=feat)
    panelz[2][0] = plot_hist(outcomes, feat=feat)
    panelz[3][0] = plot_return_by_investment_date(outcomes, feat=feat,
                                                  time_range=time_range_days)
    

time_range.param.watch(update, "value")
panelz.servable()

