import pandas as pd
import numpy as np
from utilities.utils import round_up, round_down
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import matplotlib as mpl
import matplotlib.font_manager as font_manager
mpl.rcParams['font.family'] = 'serif'
cmfont = font_manager.FontProperties(fname=mpl.get_data_path() + '/fonts/ttf/cmunrm.ttf')
mpl.rcParams['font.serif'] = cmfont.get_name()
mpl.rcParams['mathtext.fontset'] = 'cm'
mpl.rcParams['font.size'] = 11
mpl.rcParams['axes.unicode_minus'] = False

colors = mpl.cm.Pastel1(np.linspace(0, 1, 10))
mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=colors)


# %%

def plot_ordering_time_histogram(df_waiting_time_param, path_string):
    ax = df_waiting_time_param.hist(column='Time',
                                    bins=range(int(round_down(df_waiting_time_param['Time'].min(), 0)),
                                               int(round_up(df_waiting_time_param['Time'].max(),
                                                            0) + 1),
                                               1),
                                    grid=False, figsize=(6.29921, 4.19947), color='lightgrey',
                                    zorder=2, rwidth=0.9, density=False)

    ax = ax[0]
    for x in ax:
        # Despine
        x.spines['right'].set_visible(False)
        x.spines['top'].set_visible(False)
        x.spines['left'].set_visible(False)

        # Switch off ticks
        x.tick_params(axis="both", which="both", bottom="off", top=False, labelbottom="on", left="off", right=False,
                      labelleft="on")

        x.set_xticks(range(0, 25, 2))
        x.set_xticklabels(['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00',
                           '14:00', '16:00', '18:00', '20:00', '22:00', '24:00'])

        # Draw horizontal axis lines
        vals = x.get_yticks()
        for tick in vals:
            x.axhline(y=tick, linestyle='dashed', alpha=0.5, color='#eeeeee', zorder=1)

        # Remove title
        x.set_title("")

        # Set x-axis label
        x.set_xlabel("Time of day [h]", labelpad=5)

        # Set x-axis label
        x.set_ylabel("Order frequency", labelpad=10)

        # Format y-axis label
        # x.yaxis.set_major_formatter(StrMethodFormatter('{x:,g}'))
    # plt.show()
    plt.savefig(path_string / "ordering_time_histogram.pdf")
    # plt.show()

def plot_savings_histogram(df_savings_param, path_string):
    ax = df_savings_param.hist(column='Savings_Value',
                               bins=range(int(round_down(df_savings_param['Savings_Value'].min(), -1)),
                                          int(round_up(df_savings_param['Savings_Value'].max(), -1)) + 10, 10),
                               grid=False, figsize=(6.29921, 4.19947), color='lightgrey',
                               zorder=2, rwidth=0.9, density=True)

    ax = ax[0]
    for x in ax:
        # Despine
        x.spines['right'].set_visible(False)
        x.spines['top'].set_visible(False)
        x.spines['left'].set_visible(False)

        # Switch off ticks
        x.tick_params(axis="both", which="both", bottom="off", top=False, labelbottom="on", left="off", right=False,
                      labelleft="on")

        x.set_xticks(range(int(round_down(df_savings_param['Savings_Value'].min(), -1)),
                           int(round_up(df_savings_param['Savings_Value'].max(), -1)) + 10, 20))

        # Draw horizontal axis lines
        vals = x.get_yticks()
        for tick in vals:
            x.axhline(y=tick, linestyle='dashed', alpha=0.5, color='#eeeeee', zorder=1)

        x.axvline(x=df_savings_param['Savings_Value'].mean(),
                  label=f"Average savings = {round(df_savings_param['Savings_Value'].mean(), 2)}", linestyle='dashed',
                  alpha=0.6,
                  color='black')

        x.axvline(x=0, alpha=0.6, color='black')

        x.legend()
        x.legend(loc='upper right', bbox_to_anchor=(1.05, 1))

        # Remove title
        x.set_title("")

        # Set x-axis label
        x.set_xlabel("Savings Value [$]", labelpad=5)

        # Set y-axis label
        x.set_ylabel("Density", labelpad=10)

        # Format y-axis label
        # x.yaxis.set_major_formatter(StrMethodFormatter('{x:,g}'))

    plt.savefig(path_string / "savings_histogram.pdf")
    # plt.show()


def plot_waiting_time_histogram(df_waiting_time_param, path_string):
    ax = df_waiting_time_param.hist(column='Waiting_Time_Adjusted',
                                    bins=range(int(round_down(df_waiting_time_param['Waiting_Time_Adjusted'].min(), 0)),
                                               int(round_up(df_waiting_time_param['Waiting_Time_Adjusted'].max(),
                                                            0) + 1),
                                               1),
                                    grid=False, figsize=(6.29921, 4.19947), color='lightgrey',
                                    zorder=2, rwidth=0.9, density=True)

    ax = ax[0]
    for x in ax:
        # Despine
        x.spines['right'].set_visible(False)
        x.spines['top'].set_visible(False)
        x.spines['left'].set_visible(False)

        # Switch off ticks
        x.tick_params(axis="both", which="both", bottom="off", top=False, labelbottom="on", left="off", right=False,
                      labelleft="on")

        x.set_xticks(range(0, int(round_up(df_waiting_time_param['Waiting_Time_Adjusted'].max(), 0) + 1), 1))

        # Draw horizontal axis lines
        vals = x.get_yticks()
        for tick in vals:
            x.axhline(y=tick, linestyle='dashed', alpha=0.5, color='#eeeeee', zorder=1)

        x.axvline(x=df_waiting_time_param['Waiting_Time_Adjusted'].mean(),
                  label=f"Average waiting time = {round(df_waiting_time_param['Waiting_Time_Adjusted'].mean(), 2)}h",
                  linestyle='dashed',
                  alpha=0.6,
                  color='black')

        x.plot([], [], ' ', label=f"Maximum waiting time = {round(df_waiting_time_param['Waiting_Time_Adjusted'].max(), 2)}h")

        x.legend()

        # Remove title
        x.set_title("")

        # Set x-axis label
        x.set_xlabel("Waiting time [h]", labelpad=5)

        # Set y-axis label
        x.set_ylabel("Density", labelpad=10)

        # Format y-axis label
        # x.yaxis.set_major_formatter(StrMethodFormatter('{x:,g}'))

    plt.savefig(path_string / "waiting_time_histogram.pdf")

    # plt.show()

    def plot_delivery_costs(df_delivery_cost_param, path_string):
        ax = df_delivery_cost_param.plot(x='Time', y='Delivery_Cost', kind='line',
                                         grid=False, figsize=(6.29921, 4.19947), color='lightgrey',
                                         zorder=2, label='Delivery cost')
        # Despine
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)

        # Switch off ticks
        ax.tick_params(axis="both", which="both", bottom="off", top=False, labelbottom="on", left="off", right=False,
                       labelleft="on")

        ax.set_xticks(range(0, int(round_up(df_delivery_cost_param['Time'].max(), 0) + 1), 1))

        # get yticks
        vals = ax.get_yticks()

        # set yticks at correct position
        ax.set_yticks(vals)

        # Draw horizontal axis lines
        for tick in vals:
            ax.axhline(y=tick, linestyle='dashed', alpha=0.5, color='#eeeeee', zorder=1)

        # Remove title
        ax.set_title("")

        # Set x-axis label
        ax.set_xlabel("Time [days]", labelpad=5)

        # Set y-axis label
        ax.set_ylabel("Cost [$]", labelpad=10)

        # Format y-axis label
        # x.yaxis.set_major_formatter(StrMethodFormatter('{x:,g}'))

        plt.savefig(path_string / "delivery_cost.pdf")


def plot_delivery_costs(df_delivery_cost_param, path_string):
    ax = df_delivery_cost_param.plot(x='Time', y='Delivery_Cost', kind='line',
                                     grid=False, figsize=(6.29921, 4.19947), color='lightgrey',
                                     zorder=2, label='Delivery vehicle cost')
    # Despine
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Switch off ticks
    ax.tick_params(axis="both", which="both", bottom="off", top=False, labelbottom="on", left="off", right=False,
                   labelleft="on")

    ax.set_xticks(range(0, int(round_up(df_delivery_cost_param['Time'].max(), 0) + 1), 1))

    # get yticks
    vals = ax.get_yticks()

    # set yticks at correct position
    ax.set_yticks(vals)

    # Draw horizontal axis lines
    for tick in vals:
        ax.axhline(y=tick, linestyle='dashed', alpha=0.5, color='#eeeeee', zorder=1)

    # Remove title
    ax.set_title("")

    # Set x-axis label
    ax.set_xlabel("Time [days]", labelpad=5)

    # Set y-axis label
    ax.set_ylabel("Cost [$]", labelpad=10)

    # Format y-axis label
    # x.yaxis.set_major_formatter(StrMethodFormatter('{x:,g}'))

    plt.savefig(path_string / "delivery_cost.pdf")


def plot_incentives_paid(df_incentives_paid_param, path_string):
    ax = df_incentives_paid_param.plot(x='Time', y='Incentives_Paid', kind='line',
                                       grid=False, figsize=(6.29921, 4.19947), color='lightgrey',
                                       zorder=2, label='Incentives paid')
    # Despine
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Switch off ticks
    ax.tick_params(axis="both", which="both", bottom="off", top=False, labelbottom="on", left="off", right=False,
                   labelleft="on")

    ax.set_xticks(range(0, int(round_up(df_incentives_paid_param['Time'].max(), 0) + 1), 1))

    # get yticks
    vals = ax.get_yticks()

    # set yticks at correct position
    ax.set_yticks(vals)

    # Draw horizontal axis lines
    for tick in vals:
        ax.axhline(y=tick, linestyle='dashed', alpha=0.5, color='#eeeeee', zorder=1)

    # Remove title
    ax.set_title("")

    # Set x-axis label
    ax.set_xlabel("Time [days]", labelpad=5)

    # Set y-axis label
    ax.set_ylabel("Cost [$]", labelpad=10)

    # Format y-axis label
    # x.yaxis.set_major_formatter(StrMethodFormatter('{x:,g}'))

    plt.savefig(path_string / "incentives_paid.pdf")


def plot_cum_delivery_costs(df_delivery_cost_param, path_string):
    ax = df_delivery_cost_param.plot(x='Time', y='Cumulative_Delivery_Cost', kind='line',
                                     grid=False, figsize=(6.29921, 4.19947), color='lightgrey',
                                     zorder=2, drawstyle="steps-post", label='Cumulative delivery vehicle cost')
    # Despine
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Switch off ticks
    ax.tick_params(axis="both", which="both", bottom="off", top=False, labelbottom="on", left="off", right=False,
                   labelleft="on")

    ax.set_xticks(range(0, int(round_up(df_delivery_cost_param['Time'].max(), 0) + 1), 1))

    # set yticks at correct position
    ax.set_yticks(range(0, int(round_up(df_delivery_cost_param['Cumulative_Delivery_Cost'].max(), 0)) + 2000, 2000))

    vals = ax.get_yticks()

    # Draw horizontal axis lines
    for tick in vals:
        ax.axhline(y=tick, linestyle='dashed', alpha=0.5, color='#eeeeee', zorder=1)

    # Remove title
    ax.set_title("")

    # Set x-axis label
    ax.set_xlabel("Time [days]", labelpad=5)

    # Set y-axis label
    ax.set_ylabel("Cost [$]", labelpad=10)

    # Format y-axis label
    # x.yaxis.set_major_formatter(StrMethodFormatter('{x:,g}'))

    plt.savefig(path_string / "cumulative_delivery_cost.pdf")


def plot_cum_incentives_paid(df_incentives_paid_param, path_string):
    ax = df_incentives_paid_param.plot(x='Time', y='Cumulative_Incentives_Paid', kind='line',
                                       grid=False, figsize=(6.29921, 4.19947), color='lightgrey',
                                       zorder=2, drawstyle="steps-post", label='Cumulative incentives paid')
    # Despine
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Switch off ticks
    ax.tick_params(axis="both", which="both", bottom="off", top=False, labelbottom="on", left="off", right=False,
                   labelleft="on")

    ax.set_xticks(range(0, int(round_up(df_incentives_paid_param['Time'].max(), 0)) + 1, 1))

    # set yticks at correct position
    ax.set_yticks(range(0, int(round_up(df_incentives_paid_param['Cumulative_Incentives_Paid'].max(), 0)) + 500, 500))

    vals = ax.get_yticks()

    # Draw horizontal axis lines
    for tick in vals:
        ax.axhline(y=tick, linestyle='dashed', alpha=0.5, color='#eeeeee', zorder=1)

    # Remove title
    ax.set_title("")

    # Set x-axis label
    ax.set_xlabel("Time [days]", labelpad=5)

    # Set y-axis label
    ax.set_ylabel("Cost [$]", labelpad=10)

    # Format y-axis label
    # x.yaxis.set_major_formatter(StrMethodFormatter('{x:,g}'))

    plt.savefig(path_string / "cumulative_incentives_paid.pdf")

def plot_cum_total_costs(df_delivery_cost_param, df_incentives_paid_param, path_string):
    x1, y1 = df_delivery_cost_param['Time'], df_delivery_cost_param['Cumulative_Delivery_Cost']
    x2, y2 = df_incentives_paid_param['Time'], df_incentives_paid_param['Cumulative_Incentives_Paid']

    x = np.unique(np.concatenate((x1, x2)))
    yi1 = np.interp(x, df_delivery_cost_param['Time'], df_delivery_cost_param['Cumulative_Delivery_Cost'], left=0,
                    right=0)
    yi2 = np.interp(x, df_incentives_paid_param['Time'], df_incentives_paid_param['Cumulative_Incentives_Paid'], left=0,
                    right=0)

    df_total_costs = pd.DataFrame()
    df_total_costs['Time'] = x
    df_total_costs['yi1'] = yi1
    df_total_costs['yi2'] = yi2

    # print(df_total_costs)

    df_total_costs['yi1'] = df_total_costs['yi1'].replace(to_replace=0, method='ffill')
    df_total_costs['yi2'] = df_total_costs['yi2'].replace(to_replace=0, method='ffill')
    df_total_costs['Total_Cost'] = df_total_costs['yi1'] + df_total_costs['yi2']

    # df_total_costs['Cumulative_Total_Cost'] = df_total_costs['Total_Cost'].cumsum()

    # print(df_delivery_cost_param)
    # print(df_incentives_paid_param)
    # print(df_total_costs)

    ax = df_total_costs.plot(x='Time', y='Total_Cost', kind='line',
                             grid=False, figsize=(6.29921, 4.19947), zorder=2,
                             label=f'Total delivery cost')

    # ax = df_delivery_cost_param.plot(x='Time', y='Cumulative_Delivery_Cost', kind='line',
    #                                  grid=False, figsize=(6.29921, 4.19947),
    #                                  zorder=2, drawstyle="steps-post", label='Cumulative delivery cost')

    df_delivery_cost_param.plot(ax=ax, x='Time', y='Cumulative_Delivery_Cost',
                                label=f'Cumulative delivery vehicle cost ({round(df_delivery_cost_param["Cumulative_Delivery_Cost"].max()/df_total_costs["Total_Cost"].max()*100, 1)}%)')

    df_incentives_paid_param.plot(ax=ax, x='Time', y='Cumulative_Incentives_Paid',
                                  label=f'Cumulative incentives paid ({round(df_incentives_paid_param["Cumulative_Incentives_Paid"].max()/df_total_costs["Total_Cost"].max()*100,1)}%)')

    # Despine
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Switch off ticks
    ax.tick_params(axis="both", which="both", bottom="off", top=False, labelbottom="on", left="off", right=False,
                   labelleft="on")

    ax.set_xticks(range(0, int(round_up(df_total_costs['Time'].max(), 0)) + 1, 1))

    # set yticks at correct position
    ax.set_yticks(range(0, int(round_up(df_total_costs['Total_Cost'].max(), -3)) + 2000, 2000))

    vals = ax.get_yticks()

    # Draw horizontal axis lines
    for tick in vals:
        ax.axhline(y=tick, linestyle='dashed', alpha=0.5, color='#eeeeee', zorder=1)

    ax.legend(loc='upper right', bbox_to_anchor=(0.7, 1.0))

    # Remove title
    ax.set_title("")

    # Set x-axis label
    ax.set_xlabel("Time [days]", labelpad=5)

    # Set y-axis label
    ax.set_ylabel("Cost [$]", labelpad=10)

    # Format y-axis label
    # x.yaxis.set_major_formatter(StrMethodFormatter('{x:,g}'))

    plt.savefig(path_string / "cumulative_total_cost.pdf", bbox_inches='tight')






#%% Plot combined results of experiments

def plot_experiment_incentives_boxplot(savings_dict, path_string, experiment_parameter_name=""):
    fig, ax = plt.subplots(figsize=(6.29921, 4.19947))

    bplot = ax.boxplot(savings_dict.values(), patch_artist=True, medianprops=dict(linewidth=1.5, color='grey'))
    ax.set_xticklabels(savings_dict.keys())

    # set labels
    ax.set_ylabel("Incentives paid [$]", labelpad=10)
    ax.set_xlabel(experiment_parameter_name, labelpad=10)
    ax.yaxis.grid(True)


    for patch, color in zip(bplot['boxes'], colors):
        patch.set_facecolor(color)

    plt.savefig(path_string / "incentives_boxplot.pdf", bbox_inches='tight')



def plot_experiment_savings_boxplot(savings_dict, path_string, experiment_parameter_name=""):
    fig, ax = plt.subplots(figsize=(6.29921, 4.19947))

    bplot = ax.boxplot(savings_dict.values(), patch_artist=True, medianprops=dict(linewidth=1.5, color='grey'))
    ax.set_xticklabels(savings_dict.keys())

    # set labels
    ax.set_ylabel("Savings [$]", labelpad=10)
    ax.set_xlabel(experiment_parameter_name, labelpad=10)
    ax.yaxis.grid(True)


    for patch, color in zip(bplot['boxes'], colors):
        patch.set_facecolor(color)

    plt.savefig(path_string / "savings_boxplot.pdf", bbox_inches='tight')



def plot_experiment_waiting_time_boxplot(waiting_time_dict, path_string, experiment_parameter_name=""):
    fig, ax = plt.subplots(figsize=(6.29921, 4.19947))

    bplot = ax.boxplot(waiting_time_dict.values(), patch_artist=True, medianprops=dict(linewidth=1.5, color='grey'))
    ax.set_xticklabels(waiting_time_dict.keys())

    # set labels
    ax.set_ylabel("Waiting Time [h]", labelpad=10)
    ax.set_xlabel(experiment_parameter_name, labelpad=10)
    ax.yaxis.grid(True)

    for patch, color in zip(bplot['boxes'], colors):
        patch.set_facecolor(color)

    plt.savefig(path_string / "waiting_time_boxplot.pdf", bbox_inches='tight')



