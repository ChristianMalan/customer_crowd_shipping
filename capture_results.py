# %%
import json
import os
import numpy as np
import pandas as pd
from utilities.utils import round_up, round_down
from pathlib import Path
import datetime
import csv
from collections import defaultdict

from utilities.utils_statistical_analysis import anova_test, mannwhitneyu_func, paired_t_test, shapiro_wilk_normality, confidence_intervals

from utilities.plot_utils import plot_savings_histogram, plot_waiting_time_histogram, plot_delivery_costs, \
    plot_incentives_paid, plot_cum_delivery_costs, plot_cum_incentives_paid, plot_cum_total_costs, \
    plot_ordering_time_histogram, plot_experiment_incentives_boxplot, plot_experiment_savings_boxplot, \
    plot_experiment_waiting_time_boxplot, plot_experiment_delivery_cost_boxplot, \
    plot_experiment_incentives_total_boxplot, plot_experiment_incentives_count_boxplot, \
    plot_experiment_percentage_savings_boxplot, plot_incentive_time_histogram

from statistics import mean, stdev, median

import matplotlib as mpl
import matplotlib.font_manager as font_manager
from matplotlib.ticker import StrMethodFormatter

mpl.rcParams['font.family'] = 'serif'
cmfont = font_manager.FontProperties(fname=mpl.get_data_path() + '/fonts/ttf/cmunrm.ttf')
mpl.rcParams['font.serif'] = cmfont.get_name()
mpl.rcParams['mathtext.fontset'] = 'cm'
mpl.rcParams['font.size'] = 12
mpl.rcParams['axes.unicode_minus'] = False

colors = mpl.cm.Pastel1(np.linspace(0, 1, 10))
mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=colors)

import matplotlib.pyplot as plt


# %%

def plot_experiment_order_time_average_histogram(order_time_dict, path_string_param, experiment_parameter_name=""):
    for key in order_time_dict:
        # print(path_string_param)
        path_string = path_string_param / (experiment_parameter_name + "_" + key)
        if not path_string.exists():
            os.makedirs(path_string)
        # print(path_string)
        # print("Key", key)
        df_order_time = pd.DataFrame(order_time_dict[key], columns=["Time"])
        # print(df_order_time)
        plot_ordering_time_histogram(df_order_time, path_string)


def plot_experiment_incentive_time_average_histogram(incentive_time_dict, path_string_param,
                                                     experiment_parameter_name=""):
    for key in incentive_time_dict:
        # print(path_string_param)
        path_string = path_string_param / (experiment_parameter_name + "_" + key)
        if not path_string.exists():
            os.makedirs(path_string)
        # print(path_string)
        # print("Key", key)
        df_incentive_time = pd.DataFrame(incentive_time_dict[key], columns=["Time"])
        # print(df_order_time)
        plot_incentive_time_histogram(df_incentive_time, path_string)


def plot_OD_VOT_histogram(df_VOT_param, path_string):
    ax = df_VOT_param.hist(column='Value_of_time', bins=15,
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

        # Draw horizontal axis lines
        vals = x.get_yticks()
        for tick in vals:
            x.axhline(y=tick, linestyle='dashed', alpha=0.5, color='#eeeeee', zorder=1)

        # x.set_xticks(range(0, 16, 2))

        # Remove title
        x.set_title("")

        # Set x-axis label
        x.set_xlabel("Value of time", labelpad=5)

        # Set x-axis label
        x.set_ylabel("Number of ODs", labelpad=10)

        # Format y-axis label
        # x.yaxis.set_major_formatter(StrMethodFormatter('{x:,g}'))
    # plt.show()
    plt.savefig(path_string / "vot_histogram.pdf")
    # plt.show()


def adjust_waiting_time(waiting_time_row):
    # Business hours start at 08:00.
    # That is 8 hours after 24... 24+8=32
    # 32 - 17 = 15

    # The case where you ordered after working hours, subtract the time between next morning 8 and order time

    # if order is placed after hours on a regular day
    if waiting_time_row['Time'] > 17:
        waiting_time = waiting_time_row['Waiting_Time'] - (32 - waiting_time_row['Time'])
    # if order is too late for delivery on a regular day
    elif waiting_time_row['Waiting_Time'] > 15:
        waiting_time = waiting_time_row['Waiting_Time'] - 15
    else:
        waiting_time = waiting_time_row['Waiting_Time']

    # The case where you ordered in working hours, but it was after the final delivery
    return waiting_time


# %%


def capture_run_results(data_path_param, fixed_incentive_param, variable_rate_param, deliveries_per_day_param,
                        od_percentage_param, min_vot_param,
                        customer_rate_param, OD_rate_param, cost_per_distance_param, loss_aversion_param,
                        OD_VOT_dataset, deliveries_dataset, incentives_dataset, savings_dataset, original_route_dataset,
                        waiting_time_dataset,
                        run_duration):
    ###################################################
    # Capture input parameters
    ###################################################
    data_path_param = data_path_param[:-5]
    data_path_param = data_path_param.partition('/')[2]
    data_path_param = data_path_param.partition('/')[2]

    stats_overall = {
        'run_end_time': datetime.datetime.now()  # enter the begin time
    }

    run_parameters = {
        'run_duration': run_duration * (1 / 60000),  # capture the simulation run time
        'dataset_code': data_path_param,
        'fixed_incentive': round(fixed_incentive_param, 1),
        'variable_incentive': round(variable_rate_param, 2),
        'deliveries_per_day': round(deliveries_per_day_param),
        'od_percentage': round(od_percentage_param, 1),
        'od_min_vot': round(min_vot_param, 1),
        'customer_order_rate': customer_rate_param,
        'OD_arrival_rate': round(OD_rate_param, 1),
        'cost_per_distance': round(cost_per_distance_param, 1),
        'loss_aversion_parameter': round(loss_aversion_param, 1)
    }

    ###########################
    # Set results directory
    ###########################
    # print(run_parameters['loss_aversion_parameter'])
    ################################################################################################
    # Change this manually for [Parameter_Variation / Sensitivity_Analysis / etc]
    ###############################################################################################
    # Scenario_1_savings_OD_1_5_vot_3
    experiment_type = "variable_rate_9_sept_no_max"
    param_tested = run_parameters['variable_incentive']
    param_tested_name = "Variable incentive [$/km]"
    param_pre_string = "variable_incentive"
    ###########################################################################################
    param_string = f"{param_pre_string}_{param_tested}"

    path_parent_folder = Path(os.path.dirname(os.getcwd()))

    experiment_folder = path_parent_folder / ("Experiment_Results" + "/" + experiment_type)
    experiment_combined_data_path = experiment_folder / ("Combined_Run_Data")

    path_results = experiment_folder / (
            "Results" + "_" + param_string + "_" + stats_overall['run_end_time'].strftime("%Y%m%d_%H%M%S"))

    if not path_results.exists():
        os.makedirs(path_results)

    with open(path_results / "run_parameters.json", 'w') as fp:
        json.dump(run_parameters, fp)

    ###################################################
    # Generate and save figures and other information
    ###################################################

    od_vot_dictionary = json.loads(OD_VOT_dataset)
    deliveries_dictionary = json.loads(deliveries_dataset)
    incentives_dictionary = json.loads(incentives_dataset)
    savings_dictionary = json.loads(savings_dataset)
    original_route_dictionary = json.loads(original_route_dataset)
    waiting_time_dictionary = json.loads(waiting_time_dataset)

    df_od_vot = pd.DataFrame(od_vot_dictionary["plainDataTable"], columns=['Time', 'Value_of_time'])
    df_delivery_costs = pd.DataFrame(deliveries_dictionary["plainDataTable"], columns=['Time', 'Delivery_Cost'])
    df_incentives_paid = pd.DataFrame(incentives_dictionary["plainDataTable"], columns=['Time', 'Incentives_Paid'])
    df_savings = pd.DataFrame(savings_dictionary["plainDataTable"], columns=['Time', 'Savings_Value'])
    df_original_delivery_costs = pd.DataFrame(original_route_dictionary["plainDataTable"],
                                              columns=['Time', 'Delivery_Cost'])

    df_waiting_time = pd.DataFrame(waiting_time_dictionary["plainDataTable"], columns=['Time', 'Waiting_Time'])

    # drop the values from the first day (for warm-up period)

    df_original_delivery_costs = df_original_delivery_costs.iloc[run_parameters["deliveries_per_day"]:]
    df_delivery_costs = df_delivery_costs.iloc[run_parameters["deliveries_per_day"]:]
    df_savings = df_savings.iloc[run_parameters["deliveries_per_day"]:]

    # print(df_od_vot)
    # BELOW.... the +8 for all time values are because the model time starts at 08:00
    # we therefore adjust from the model's "relative" reference of time
    # to the "absolute" time

    # this should not be done when dataset is empty
    if not df_incentives_paid.empty:
        # print("not empty")
        df_incentives_paid['Time'] = ((df_incentives_paid['Time'] + 8 * 60) * (1 / 60)) % 24
        df_incentives_paid['Cumulative_Incentives_Paid'] = df_incentives_paid['Incentives_Paid'].cumsum()
    # print("here4.25")

    df_waiting_time['Waiting_Time'].fillna(df_waiting_time['Waiting_Time'].mean())
    df_delivery_costs['Time'] = (df_delivery_costs['Time'] + 8 * 60) * (1 / (60 * 24))

    df_waiting_time['Day_of_week'] = ((df_waiting_time['Time'] + 8 * 60) * (1 / (60 * 24))) % 7

    # change time from simulation time to time of day
    df_waiting_time['Time'] = ((df_waiting_time['Time'] + 8 * 60) * (1 / 60)) % 24
    # change waiting time from minutes to hours
    df_waiting_time['Waiting_Time'] = df_waiting_time['Waiting_Time'] * (1 / 60)
    # print(df_waiting_time)
    # adjust waiting time
    df_waiting_time['Waiting_Time_Adjusted'] = df_waiting_time.apply(lambda row:
                                                                     adjust_waiting_time(row),
                                                                     axis=1)
    # print(df_waiting_time)

    df_delivery_costs['Cumulative_Delivery_Cost'] = df_delivery_costs['Delivery_Cost'].cumsum()

    # change savings into a daily savings
    # print(df_savings)
    df_savings = df_savings.groupby(df_savings.index // deliveries_per_day_param).sum()

    # print(df_incentives_paid.head(5))
    # print(df_delivery_costs.head(5))
    # print(df_savings.head(5))

    # print(df_waiting_time.head(5))
    # print(df_waiting_time.tail(5))
    # print("here5")

    # %%
    ###################################################
    # Create output capturing essential information
    ###################################################

    run_output = {
        'run_duration': run_duration * (1 / 60000),  # capture the simulation run time
        'min_waiting_time': df_waiting_time["Waiting_Time_Adjusted"].min(),
        'max_waiting_time': df_waiting_time["Waiting_Time_Adjusted"].max(),
        'mean_waiting_time': df_waiting_time["Waiting_Time_Adjusted"].mean(),
        'total_orders': len(df_waiting_time),
    }

    with open(path_results / "run_output.json", 'w') as fp:
        json.dump(run_output, fp)

    # %% Append to experiment results
    run_order_time_dict = {f"{param_tested}": df_waiting_time["Time"].to_list()}
    run_incentive_time_dict = {f"{param_tested}": df_incentives_paid["Time"].to_list()}
    run_savings_dict = {f"{param_tested}": df_savings["Savings_Value"].to_list()}
    run_waiting_time_dict = {f"{param_tested}": df_waiting_time["Waiting_Time_Adjusted"].to_list()}
    run_incentive_dict = {f"{param_tested}": df_incentives_paid["Incentives_Paid"].to_list()}

    if not experiment_combined_data_path.exists():
        os.makedirs(experiment_combined_data_path)
        # regular results
        with open(experiment_combined_data_path / "run_incentive_time_results.json", 'w') as fp:
            json.dump(run_incentive_time_dict, fp, indent=4)
        with open(experiment_combined_data_path / "run_order_time_results.json", 'w') as fp:
            json.dump(run_order_time_dict, fp, indent=4)
        with open(experiment_combined_data_path / "run_savings_results.json", 'w') as fp:
            json.dump(run_savings_dict, fp, indent=4)
        with open(experiment_combined_data_path / "run_waiting_time_results.json", 'w') as fp:
            json.dump(run_waiting_time_dict, fp, indent=4)
        with open(experiment_combined_data_path / "run_incentives_results.json", 'w') as fp:
            json.dump(run_incentive_dict, fp, indent=4)

        # means results
        with open(experiment_combined_data_path / "experiment_incentive_means.json", 'w') as fp:
            json.dump({f"{param_tested}": [df_incentives_paid["Incentives_Paid"].mean()]}, fp, indent=4)
        with open(experiment_combined_data_path / "experiment_incentive_totals.json", 'w') as fp:
            json.dump({f"{param_tested}": [df_incentives_paid["Incentives_Paid"].sum()]}, fp, indent=4)
        with open(experiment_combined_data_path / "experiment_incentive_count.json", 'w') as fp:
            json.dump({f"{param_tested}": [len(df_incentives_paid["Incentives_Paid"])]}, fp, indent=4)
        with open(experiment_combined_data_path / "experiment_waiting_time_means.json", 'w') as fp:
            json.dump({f"{param_tested}": [df_waiting_time["Waiting_Time_Adjusted"].mean()]}, fp, indent=4)
        with open(experiment_combined_data_path / "experiment_delivery_cost_sum.json", 'w') as fp:
            json.dump({f"{param_tested}": [df_delivery_costs['Cumulative_Delivery_Cost'].iloc[-1]]}, fp, indent=4)
        with open(experiment_combined_data_path / "experiment_savings_sum.json", 'w') as fp:
            json.dump({f"{param_tested}": [df_savings["Savings_Value"].sum()]}, fp, indent=4)


        with open(experiment_combined_data_path / "experiment_savings_percentage.json", 'w') as fp:
            json.dump({f"{param_tested}": [
                (df_savings["Savings_Value"].sum() / df_original_delivery_costs['Delivery_Cost'].sum()) * 100]}, fp,
                indent=4)
        with open(experiment_combined_data_path / "total_orders.json", 'w') as fp:
            json.dump({f"{param_tested}": [len(df_waiting_time["Waiting_Time_Adjusted"])]}, fp, indent=4)

    else:
        # append to combined run reults
        # with open(experiment_combined_data_path / "run_incentive_time_results.json", 'r+') as file:
        #     data = json.load(file)
        #     if f"{param_tested}" in data:
        #         data[f"{param_tested}"].extend(df_incentives_paid["Time"].to_list())
        #     else:
        #         data.update(run_incentive_time_dict)
        #     file.seek(0)
        #     json.dump(data, file, indent=4)

        # with open(experiment_combined_data_path / "run_order_time_results.json", 'r+') as file:
        #     data = json.load(file)
        #     if f"{param_tested}" in data:
        #         data[f"{param_tested}"].extend(df_waiting_time["Time"].to_list())
        #     else:
        #         data.update(run_order_time_dict)
        #     file.seek(0)
        #     json.dump(data, file, indent=4)

        # with open(experiment_combined_data_path / "run_savings_results.json", 'r+') as file:
        #     data = json.load(file)
        #     if f"{param_tested}" in data:
        #         data[f"{param_tested}"].extend(df_savings["Savings_Value"].to_list())
        #     else:
        #         data.update(run_savings_dict)
        #     file.seek(0)
        #     json.dump(data, file, indent=4)

        # with open(experiment_combined_data_path / "run_waiting_time_results.json", 'r+') as file:
        #     data = json.load(file)
        #     if f"{param_tested}" in data.keys():
        #         data[f"{param_tested}"].extend(df_waiting_time["Waiting_Time_Adjusted"].to_list())
        #     else:
        #         data.update(run_waiting_time_dict)
        #     file.seek(0)
        #     json.dump(data, file, indent=4)

        # with open(experiment_combined_data_path / "run_incentives_results.json", 'r+') as file:
        #     data = json.load(file)
        #     if f"{param_tested}" in data.keys():
        #         data[f"{param_tested}"].extend(df_incentives_paid["Incentives_Paid"].to_list())
        #     else:
        #         data.update(run_incentive_dict)
        #     file.seek(0)
        #     json.dump(data, file, indent=4)

        # statistics data
        experiment_meta_data_keys = ['n', 'mean', 'standard_dev', 'median']


        ###################################################################################################################################
        ## Total orders
        ###################################################################################################################################

        print("Checkpoint 1")

        with open(experiment_combined_data_path / "total_orders.json", 'r') as file:
            data = json.load(file)

        if f"{param_tested}" in data.keys():
            data[f"{param_tested}"].extend([len(df_waiting_time["Waiting_Time_Adjusted"])])
        else:
            data.update({f"{param_tested}": [len(df_waiting_time["Waiting_Time_Adjusted"])]})

        with open(experiment_combined_data_path / "total_orders.json", 'w') as file:
            json.dump(data, file, indent=4)

        df_total_orders_meta_data = pd.DataFrame(np.nan, columns=data.keys(), index=experiment_meta_data_keys)
        for column in df_total_orders_meta_data.columns:
            if len(data[column]) > 1:
                df_total_orders_meta_data[column]['n'] = len(data[column])
                df_total_orders_meta_data[column]['mean'] = mean(data[column])
                df_total_orders_meta_data[column]['standard_dev'] = stdev(data[column])
                df_total_orders_meta_data[column]['median'] = median(data[column])
        df_total_orders_meta_data = df_total_orders_meta_data.reindex(sorted(df_total_orders_meta_data.columns), axis=1)
        df_total_orders_meta_data.to_csv(
            experiment_combined_data_path / "meta_data_total_orders.csv", index=True)

        ###################################################################################################################################
        ## Incentive Means
        ###################################################################################################################################
        print("Checkpoint 2")

        with open(experiment_combined_data_path / "experiment_incentive_means.json", 'r') as file:
            data = json.load(file)

        if f"{param_tested}" in data.keys():
            data[f"{param_tested}"].extend([df_incentives_paid["Incentives_Paid"].mean()])
        else:
            data.update({f"{param_tested}": [df_incentives_paid["Incentives_Paid"].mean()]})

        with open(experiment_combined_data_path / "experiment_incentive_means.json", 'w') as file:
            json.dump(data, file, indent=4)

        ###################################################################################################################################
        ## Incentive totals
        ###################################################################################################################################
        print("Checkpoint 3")

        with open(experiment_combined_data_path / "experiment_incentive_totals.json", 'r+') as file:
            data = json.load(file)
        if f"{param_tested}" in data.keys():
            data[f"{param_tested}"].extend([df_incentives_paid["Incentives_Paid"].sum()])
        else:
            data.update({f"{param_tested}": [df_incentives_paid["Incentives_Paid"].sum()]})
        with open(experiment_combined_data_path / "experiment_incentive_totals.json", 'w') as file:
            json.dump(data, file, indent=4)

        df_incentive_totals_meta_data = pd.DataFrame(np.nan, columns=data.keys(), index=experiment_meta_data_keys)
        for column in df_incentive_totals_meta_data.columns:
            if len(data[column]) > 1:
                df_incentive_totals_meta_data[column]['n'] = len(data[column])
                df_incentive_totals_meta_data[column]['mean'] = mean(data[column])
                df_incentive_totals_meta_data[column]['standard_dev'] = stdev(data[column])
                df_incentive_totals_meta_data[column]['median'] = median(data[column])
        df_incentive_totals_meta_data = df_incentive_totals_meta_data.reindex(
            sorted(df_incentive_totals_meta_data.columns), axis=1)
        df_incentive_totals_meta_data.to_csv(
            experiment_combined_data_path / "meta_data_incentive_totals.csv", index=True)

        ###################################################################################################################################
        ## Incentive count
        ###################################################################################################################################
        print("Checkpoint 4")

        with open(experiment_combined_data_path / "experiment_incentive_count.json", 'r+') as file:
            data = json.load(file)
            if f"{param_tested}" in data.keys():
                data[f"{param_tested}"].extend([len(df_incentives_paid["Incentives_Paid"])])
            else:
                data.update({f"{param_tested}": [len(df_incentives_paid["Incentives_Paid"])]})
            file.seek(0)
            json.dump(data, file, indent=4)

        ###################################################################################################################################
        ## Waiting times
        ###################################################################################################################################

        print("Checkpoint 4")
        with open(experiment_combined_data_path / "experiment_waiting_time_means.json", 'r') as file:
            data = json.load(file)
        if f"{param_tested}" in data.keys():
            data[f"{param_tested}"].extend([df_waiting_time["Waiting_Time_Adjusted"].mean()])
        else:
            data.update({f"{param_tested}": [df_waiting_time["Waiting_Time_Adjusted"].mean()]})
        with open(experiment_combined_data_path / "experiment_waiting_time_means.json", 'w') as file:
            json.dump(data, file, indent=4)

        df_waiting_time_meta_data = pd.DataFrame(np.nan, columns=data.keys(), index=experiment_meta_data_keys)
        for column in df_waiting_time_meta_data.columns:
            if len(data[column]) > 1:
                df_waiting_time_meta_data[column]['n'] = len(data[column])
                df_waiting_time_meta_data[column]['mean'] = mean(data[column])
                df_waiting_time_meta_data[column]['standard_dev'] = stdev(data[column])
                df_waiting_time_meta_data[column]['median'] = median(data[column])
        df_waiting_time_meta_data = df_waiting_time_meta_data.reindex(sorted(df_waiting_time_meta_data.columns), axis=1)
        df_waiting_time_meta_data.to_csv(
            experiment_combined_data_path / "meta_data_waiting_time.csv", index=True)

        df_waiting_time_means = pd.DataFrame.from_dict(data, orient='index')
        df_waiting_time_means = df_waiting_time_means.transpose()
        df_waiting_time_means.to_csv(experiment_combined_data_path / "experiment_waiting_time_means.csv", index=False)

        ###################################################################################################################################
        ## Delivery cost
        ###################################################################################################################################

        print("Checkpoint 5")

        with open(experiment_combined_data_path / "experiment_delivery_cost_sum.json", 'r+') as file:
            data = json.load(file)
        if f"{param_tested}" in data.keys():
            data[f"{param_tested}"].extend([df_delivery_costs['Cumulative_Delivery_Cost'].iloc[-1]])
        else:
            data.update({f"{param_tested}": [df_delivery_costs['Cumulative_Delivery_Cost'].iloc[-1]]})
        with open(experiment_combined_data_path / "experiment_delivery_cost_sum.json", 'w') as file:
            json.dump(data, file, indent=4)

        df_delivery_cost_meta_data = pd.DataFrame(np.nan, columns=data.keys(), index=experiment_meta_data_keys)
        for column in df_delivery_cost_meta_data.columns:
            if len(data[column]) > 1:
                df_delivery_cost_meta_data[column]['n'] = len(data[column])
                df_delivery_cost_meta_data[column]['mean'] = mean(data[column])
                df_delivery_cost_meta_data[column]['standard_dev'] = stdev(data[column])
                df_delivery_cost_meta_data[column]['median'] = median(data[column])
        df_delivery_cost_meta_data = df_delivery_cost_meta_data.reindex(sorted(df_delivery_cost_meta_data.columns),
                                                                        axis=1)
        df_delivery_cost_meta_data.to_csv(
            experiment_combined_data_path / "meta_data_delivery_cost.csv", index=True)

        ###################################################################################################################################
        ## Savings
        ###################################################################################################################################

        # print("Checkpoint 6")

        with open(experiment_combined_data_path / "experiment_savings_sum.json", 'r') as file:
            data = json.load(file)
        if f"{param_tested}" in data.keys():
            data[f"{param_tested}"].extend([df_savings["Savings_Value"].sum()])
        else:
            data.update({f"{param_tested}": [df_savings["Savings_Value"].sum()]})
        with open(experiment_combined_data_path / "experiment_savings_sum.json", 'w') as file:
            json.dump(data, file, indent=4)

        savings_sum_meta_data = dict.fromkeys(data.keys())

        for key in savings_sum_meta_data:
            if len(data[key]) > 1:
                savings_sum_meta_data[key] = {'n': len(data[key]), 'mean': mean(data[key]), 'stdev': stdev(data[key])}

        print(savings_sum_meta_data)



        df_savings_sum = pd.DataFrame.from_dict(data, orient='index')
        df_savings_sum = df_savings_sum.transpose()
        df_savings_sum.to_csv(experiment_combined_data_path / "experiment_savings_sum.csv", index=False)

        ###################################################################################################################################
        ## Savings percentage
        ###################################################################################################################################

        print("Checkpoint 7")

        with open(experiment_combined_data_path / "experiment_savings_percentage.json", 'r') as file:
            data = json.load(file)
        if f"{param_tested}" in data.keys():
            data[f"{param_tested}"].extend(
                [(df_savings["Savings_Value"].sum() / df_original_delivery_costs['Delivery_Cost'].sum()) * 100])
        else:
            data.update({f"{param_tested}": [
                (df_savings["Savings_Value"].sum() / df_original_delivery_costs['Delivery_Cost'].sum()) * 100]})
        with open(experiment_combined_data_path / "experiment_savings_percentage.json", 'w') as file:
            json.dump(data, file, indent=4)

        df_percentage_savings_meta_data = pd.DataFrame(np.nan, columns=data.keys(), index=experiment_meta_data_keys)
        for column in df_percentage_savings_meta_data.columns:
            if len(data[column]) > 1:
                df_percentage_savings_meta_data[column]['n'] = len(data[column])
                df_percentage_savings_meta_data[column]['mean'] = mean(data[column])
                df_percentage_savings_meta_data[column]['standard_dev'] = stdev(data[column])
                df_percentage_savings_meta_data[column]['median'] = median(data[column])

        df_percentage_savings_meta_data = df_percentage_savings_meta_data.reindex(
            sorted(df_percentage_savings_meta_data.columns), axis=1)
        df_percentage_savings_meta_data.to_csv(
            experiment_combined_data_path / "meta_data_experiment_savings_percentage.csv", index=True)
        print(df_percentage_savings_meta_data)

        print("Checkpoint 8")

        df_perc_savings = pd.DataFrame.from_dict(data, orient='index')
        df_perc_savings = df_perc_savings.transpose()
        df_perc_savings.to_csv(experiment_combined_data_path / "experiment_savings_percentage.csv", index=False)

        kpi_json_files = {"savings_percentage": "experiment_savings_percentage.json",
                          "waiting_time": "experiment_waiting_time_means.json"}

        print("Checkpoint 9")
        if len(data[column]) > 1:
            for kpi in kpi_json_files:
                anova_test(kpi_json_files[kpi], experiment_combined_data_path, kpi)
                mannwhitneyu_func(kpi_json_files[kpi], experiment_combined_data_path, kpi)
                paired_t_test(kpi_json_files[kpi], experiment_combined_data_path, kpi)
                shapiro_wilk_normality(kpi_json_files[kpi], experiment_combined_data_path, kpi)
                confidence_intervals(kpi_json_files[kpi], experiment_combined_data_path, kpi)

    # %% Summarise results

    # %% Plot results

    # plot_waiting_time_histogram(df_waiting_time, path_results)
    plot_ordering_time_histogram(df_waiting_time, path_results)
    # plot_delivery_costs(df_delivery_costs, path_results)
    # plot_cum_delivery_costs(df_delivery_costs, path_results)

    # if not df_incentives_paid.empty:
    #     plot_incentive_time_histogram(df_incentives_paid, path_results)
    #
    #     with open(experiment_combined_data_path / "run_incentive_time_results.json", 'r') as file:
    #         data = json.load(file)
    #         plot_experiment_incentive_time_average_histogram(data, experiment_combined_data_path, param_pre_string)

    # plot_OD_VOT_histogram(df_od_vot, path_results)
    # plot_savings_histogram(df_savings, path_results)
    # plot_incentives_paid(df_incentives_paid, path_results)
    # plot_cum_incentives_paid(df_incentives_paid, path_results)
    # plot_cum_total_costs(df_delivery_costs, df_incentives_paid, path_results)

    # combined results plot

    with open(experiment_combined_data_path / "experiment_delivery_cost_sum.json", 'r') as file:
        data = json.load(file)
        plot_experiment_delivery_cost_boxplot(data, experiment_combined_data_path, param_tested_name)

    with open(experiment_combined_data_path / "experiment_savings_sum.json", 'r') as file:
        data = json.load(file)
        plot_experiment_savings_boxplot(data, experiment_combined_data_path, param_tested_name)

    with open(experiment_combined_data_path / "experiment_savings_percentage.json", 'r') as file:
        data = json.load(file)
        plot_experiment_percentage_savings_boxplot(data, experiment_combined_data_path, param_tested_name)

    with open(experiment_combined_data_path / "experiment_waiting_time_means.json", 'r') as file:
        data = json.load(file)
        plot_experiment_waiting_time_boxplot(data, experiment_combined_data_path, param_tested_name)

    with open(experiment_combined_data_path / "experiment_incentive_totals.json", 'r') as file:
        data = json.load(file)
        plot_experiment_incentives_total_boxplot(data, experiment_combined_data_path, param_tested_name)

    with open(experiment_combined_data_path / "experiment_incentive_count.json", 'r') as file:
        data = json.load(file)
        plot_experiment_incentives_count_boxplot(data, experiment_combined_data_path, param_tested_name)

    with open(experiment_combined_data_path / "experiment_incentive_means.json", 'r') as file:
        data = json.load(file)
        plot_experiment_incentives_boxplot(data, experiment_combined_data_path, param_tested_name)

    with open(experiment_combined_data_path / "run_order_time_results.json", 'r') as file:
        data = json.load(file)
        plot_experiment_order_time_average_histogram(data, experiment_combined_data_path, param_pre_string)

    # plt.show()


# %% main

def main():
    """main()"""

    data_path_test = "vrp_algorithms/test_data/R101_25.json"

    OD_VOT_data_test = '{"ymax": 5.799459197011004, "ymin": 3.7348358362285627, "xmax": 71097.41725401909, ' \
                       '"xmin": 69481.88504756276, "capacity": 100, "ymedian": 4.836125667268682,"plainDataTable": [[' \
                       '69481.88504756276, 5.651503574799046], [69493.72737082708, 4.060184710092623], ' \
                       '[69502.99385930639, 4.833723312350428], [69509.04381716147, 5.482579829793415], ' \
                       '[69521.87147101379, 4.803633945084733], [69526.21237114162, 4.836664623149822], ' \
                       '[69536.6342581903, 4.02965748614713], [69550.65041315371, 4.016670670270266], ' \
                       '[69551.38084529217, 4.588856769137907], [69557.98106022972, 5.50178006774147], ' \
                       '[69560.4211159322, 5.569166538177478], [69566.6278279489, 4.702734787063591], ' \
                       '[69568.7432468683, 4.799470428233157], [69570.852366014, 5.505066916500445], ' \
                       '[69571.78936744288, 4.136434935300386], [69579.99452992396, 3.91504386820233], ' \
                       '[69584.05408504343, 5.571436031568572], [69585.79937334785, 4.7685088907966495], ' \
                       '[69587.48623346843, 5.560052347544088], [69597.55668366357, 3.851171630046092], ' \
                       '[69603.21145498416, 4.8601132273819125], [69609.68461286147, 5.567170544420181], ' \
                       '[69631.61097862724, 3.9629258137871797], [70560.15525271907, 5.5667019256243195], ' \
                       '[70569.09051681198, 4.1018282189367214], [70569.96835424198, 5.545456576231179], ' \
                       '[70578.37827923041, 4.1194728323895005], [70582.68893370127, 5.45957604292115], ' \
                       '[70592.93124167151, 4.770454746353452], [70616.87015961329, 5.799459197011004], ' \
                       '[70621.85121491888, 5.437329316520579], [70659.20697166678, 5.69919957583799], ' \
                       '[70659.67418142392, 4.858102343654834], [70662.31952269874, 5.530465300375879], ' \
                       '[70662.79520753236, 3.997185270310561], [70664.32229795787, 5.719422240285776], ' \
                       '[70673.66949221665, 3.875138312438067], [70701.51158449937, 5.550665076113704], ' \
                       '[70708.31715515393, 5.532446894279709], [70708.39385733638, 3.9916368836856018], ' \
                       '[70708.49616057683, 3.9234458396062495], [70721.13086833664, 5.500199621000864], ' \
                       '[70722.58252984233, 4.731230098690215], [70724.34804095681, 3.7348358362285627], ' \
                       '[70734.42679966611, 5.574571370019821], [70743.07378316151, 5.554756227863024], ' \
                       '[70744.75988205579, 5.719975490214166], [70745.99017837062, 5.518936161466789], ' \
                       '[70751.31962168263, 4.00351272445492], [70757.0444233563, 5.714433405101315], ' \
                       '[70763.74684975136, 5.474155177406769], [70767.3667673643, 3.997155144516697], ' \
                       '[70783.54777102235, 4.876483651983138], [70790.24639414085, 4.713132752722257], ' \
                       '[70808.50395450366, 3.953722123658875], [70813.46050147312, 5.450372068073649], ' \
                       '[70817.02105534893, 4.647882323828275], [70822.36776629434, 5.580657089493866], ' \
                       '[70829.86522061392, 4.9837302596600015], [70846.72228622745, 5.55814470696664], ' \
                       '[70848.2777796867, 4.03690312433696], [70848.96044005732, 4.0949889787343015], ' \
                       '[70863.05207909577, 5.686715725920274], [70863.42239400484, 5.6060894660530565], ' \
                       '[70881.8969347586, 4.835586711387543], [70888.43478632526, 3.8632549907661873], ' \
                       '[70888.52912572585, 4.788881575950323], [70891.99147936626, 4.817632517851928], ' \
                       '[70900.34404970317, 4.746531428847342], [70901.22270628164, 5.047277283714505], ' \
                       '[70902.38880579223, 5.381124519222404], [70911.77989629697, 5.52594665312254], ' \
                       '[70918.5517156899, 5.728010546732394], [70919.07852860767, 3.9933079272820793], ' \
                       '[70920.25025982344, 5.616074164683395], [70933.11683812173, 5.057052825398644],' \
                       '[70937.1765064896, 4.219518757692683], [70945.83533540255, 5.6490661707315075], ' \
                       '[70952.48118747324, 3.978628779885139], [70966.01627004081, 3.8896353708208045], ' \
                       '[70975.29710723173, 5.492893167945047], [70981.72090528258, 5.561821080661686], ' \
                       '[70990.0975377719, 5.609560366517113], [70991.65409461754, 4.719289703071148], ' \
                       '[70995.28001851238, 4.019516607437862], [71003.40259576561, 4.001884552201309],' \
                       '[71011.41558155675, 4.7663720836466785], [71018.4843980525, 4.808341729210366],' \
                       '[71028.92889699891, 3.883981713686571], [71033.27458821252, 3.984859534039675],' \
                       '[71042.21703181507, 5.5408872630187895], [71043.27903143545, 5.629606699100226],' \
                       '[71055.22774730778, 4.88499791716782], [71063.7994390842, 5.599418272333073],' \
                       '[71064.6148437258, 4.813280335485407], [71069.92653489897, 5.664259079001395],' \
                       '[71077.88184761055, 3.947398719087944], [71077.93826600666, 3.9467118466507367],' \
                       '[71082.58822220283, 4.795961169113754], [71097.41725401909, 3.94581937823182]], "xmedian": ' \
                       '70760.39563655383, "xmean": 70548.25630528998, "ymean": 4.875195125102574, "version": 3519} '

    run_deliveries_data_test = '{"xmax":19260.0,"ymin":16.72,"xmin":540.0,"ymax":70.7,"capacity":10000,' \
                               '"plainDataTable":[[540.0,16.72],[1980.0,47.84],[3420.0,68.84],[4860.0,51.74],[6300.0,' \
                               '69.34],[7740.0,57.4],[9180.0,63.839999999999996],[10620.0,66.56],[12060.0,70.7],' \
                               '[13500.0,62.599999999999994],[14940.0,49.339999999999996],[16380.0,50.3],[17820.0,' \
                               '59.22],[19260.0,56.85999999999999]],"ymean":56.52142857142858,"ymedian":58.31,' \
                               '"xmedian":9900.0,"xmean":9900.0,"version":15} '

    original_route_data_test = '{"xmax": 19260.0, "ymin": 29.439999999999998, "xmin": 540.0, "ymax": 70.7, ' \
                               '"capacity": 100000, "plainDataTable": [[540.0, 29.439999999999998], [1980.0, 63.84], ' \
                               '[3420.0, 68.84], [4860.0, 67.22], [6300.0, 69.34], [7740.0, 68.02], [9180.0, ' \
                               '63.839999999999996], [10620.0, 66.56], [12060.0, 70.7], [13500.0, ' \
                               '62.599999999999994], [14940.0, 49.339999999999996], [16380.0, 50.3], [17820.0, ' \
                               '59.22], [19260.0, 56.85999999999999]], "ymean": 60.43714285714286, "ymedian": 63.84, ' \
                               '"xmedian": 9900.0, "xmean": 9900.0, "version": 15} '

    incentives_paid_data_test = '{"ymax":19.731510111959906,"ymin":10.013453073980195,"xmin":331.93229801878203,' \
                                '"xmax":18861.275641070668,"capacity":100,"plainDataTable":[[331.93229801878203,' \
                                '14.407333137025503],[414.2385468203655,11.252833191076284],[497.5134215969183,' \
                                '12.462307038105138],[1694.2338356244024,11.437431456646344],[1792.7458752349517,' \
                                '16.3449856979166],[1956.3339799561297,17.836325843482612],[2923.8851851621507,' \
                                '10.024948765560055],[3050.306027510304,12.491468375796359],[3063.319200818182,' \
                                '12.712033608982246],[3254.829652220737,13.309808690041102],[3393.500692931511,' \
                                '11.580144098575573],[4363.652455817007,10.222185095958558],[4364.13683941769,' \
                                '17.836325843482612],[4549.005005375919,12.462307038105138],[4582.828263442435,' \
                                '13.592181132479531],[4635.216621326971,10.222185095958558],[5780.3852296402465,' \
                                '12.491468375796359],[5784.83388579554,14.407333137025503],[5937.778689497238,' \
                                '10.160763150409004],[6004.360882142183,10.024948765560055],[6012.890806430829,' \
                                '12.1535002526457],[7222.413716242576,14.407333137025503],[7223.06840883155,' \
                                '11.580144098575573],[7225.139244385013,12.822543331135648],[7374.70167116465,' \
                                '11.252833191076284],[7433.984463795617,10.160763150409004],[7582.561525923297,' \
                                '17.836325843482612],[7691.790196499514,12.462307038105138],[7714.487934935005,' \
                                '17.68539648686015],[8964.446087807464,12.712033608982246],[9035.571547521558,' \
                                '12.1535002526457],[10084.346599584183,10.222185095958558],[10517.661944128131,' \
                                '11.437431456646344],[11545.130451303981,13.309808690041102],[11563.681787223948,' \
                                '16.563590086308196],[11663.187500559083,13.592181132479531],[11723.351916812868,' \
                                '12.712033608982246],[11781.06577780825,10.160763150409004],[11794.677314116889,' \
                                '12.639437099654373],[12026.110418530941,11.437431456646344],[13421.780496397845,' \
                                '10.024948765560055],[13482.200481557995,10.013453073980195],[14403.52958988309,' \
                                '12.822543331135648],[14404.217534668604,13.309808690041102],[16028.92363689442,' \
                                '19.731510111959906],[16117.883980898256,12.1535002526457],[16172.209528912601,' \
                                '13.8684236756148],[17307.99184461961,11.252833191076284],[17352.4081010834,' \
                                '16.563590086308196],[17635.994093346613,12.616126536861799],[18861.275641070668,' \
                                '12.491468375796359]],"xmean":8426.347467280162,"xmedian":7433.984463795617,' \
                                '"ymean":12.89076599602024,"ymedian":12.491468375796359,"version":52} '

    run_savings_data_test = '{"ymax":0.0,"xmax":29340.0,"xmin":180.0,"ymin":0.0,"capacity":100000,"xmean":14760.0,"xmedian":14760.0,"ymean":0.0,"ymedian":0.0,"plainDataTable":[[180.0,0.0],[540.0,0.0],[1620.0,0.0],[1980.0,0.0],[3060.0,0.0],[3420.0,0.0],[4500.0,0.0],[4860.0,0.0],[5940.0,0.0],[6300.0,0.0],[7380.0,0.0],[7740.0,0.0],[8820.0,0.0],[9180.0,0.0],[10260.0,0.0],[10620.0,0.0],[11700.0,0.0],[12060.0,0.0],[13140.0,0.0],[13500.0,0.0],[14580.0,0.0],[14940.0,0.0],[16020.0,0.0],[16380.0,0.0],[17460.0,0.0],[17820.0,0.0],[18900.0,0.0],[19260.0,0.0],[20340.0,0.0],[20700.0,0.0],[21780.0,0.0],[22140.0,0.0],[23220.0,0.0],[23580.0,0.0],[24660.0,0.0],[25020.0,0.0],[26100.0,0.0],[26460.0,0.0],[27540.0,0.0],[27900.0,0.0],[28980.0,0.0],[29340.0,0.0]],"version":43}'

    # '{"ymin":0.0,"xmax":35099.4,"ymax":5.8102598376454395,"xmin":539.4,"capacity":100000,' \
    # '"plainDataTable":[[539.4,5.8102598376454395],[1979.4,6.0],[3419.4,3.0],[4859.4,0.0],' \
    # '[6299.4,0.0],[7739.4,7.0],[9179.4,0.0],[10619.4,0.0],[12059.4,0.0],[13499.4,0.0],' \
    # '[14939.4,0.0],[16379.4,9.0],[17819.4,1.0],[19259.4,2.0],[20699.4,3.0],[22139.4,4.0],' \
    # '[23579.4,5.0],[25019.4,6.0],[26459.4,7.0],[27899.4,8.0],[29339.4,0.0],[30779.4,0.0],' \
    # '[32219.4,0.0],[33659.4,0.0],[35099.4,0.0]],"ymean":0.23241039350581758,' \
    # '"xmedian":17819.4,"ymedian":0.0,"xmean":17819.4,"version":26} '

    # ########################################################################################################################
    # # Uncomment to test for no incentives or savings
    # incentives_paid_data_test = '{"xmin": "Infinity", "ymax": "-Infinity", "ymin": "Infinity", ' \
    #                             '"xmax": "-Infinity", "capacity": 100, "ymean": 0.0, "ymedian": 0.0, ' \
    #                             '"plainDataTable": [], "xmean": 0.0, ' \
    #                             '"xmedian": 0.0, "version": 1}'
    #
    # run_savings_data_test = '{"xmin": "Infinity", "ymax": "-Infinity", "ymin": "Infinity", "xmax": "-Infinity", ' \
    #                         '"capacity": 10000, "ymean": 0.0, "ymedian": 0.0, "plainDataTable": [], "xmean": 0.0, ' \
    #                         '"xmedian": 0.0, "version": 1}'
    # #########################################################################################################################

    waiting_time_data_test = '{"ymax":1084.6317584830922,"ymin":6.30109057477739,"xmin":42.90595617467103,' \
                             '"xmax":18982.319347559114,"capacity":10000,"plainDataTable":[[42.90595617467103,' \
                             '17.36891753370348],[283.58848885764445,52.4992177117864],[410.411083944617,' \
                             '6.673061097481764],[341.2394941604695,79.1492359658535],[81.18800822772249,' \
                             '340.0073885652672],[48.397429208356,373.4607216595101],[85.07039346214093,' \
                             '337.4763192140416],[71.01867993975347,352.3613660697624],[387.14412593194214,' \
                             '37.28566749432275],[476.402119476906,24.27162821749954],[719.3313522805907,' \
                             '780.9090178044402],[497.1120050533889,1003.8950316983087],[768.888371817274,' \
                             '732.9168073314236],[772.6082884056192,729.8596448179547],[741.287928719654,' \
                             '761.805790919014],[793.5619566589028,710.1260438839236],[567.395182900149,' \
                             '936.9418888411773],[795.8510544823963,709.1252213457154],[713.5316456728008,' \
                             '792.1808974239332],[714.3198749366948,791.9869490641975],[597.9049216839385,' \
                             '909.0509735154537],[1663.7189929455553,33.5744759747231],[1781.2078162131033,' \
                             '15.30054532294048],[1760.6152358838058,99.8116390653563],[1505.2233866274396,' \
                             '356.0016307187225],[1535.7442481886271,326.758229410181],[1899.6353498258577,' \
                             '59.68770652179683],[2053.000934699469,873.9606322377035],[2824.4351974183596,' \
                             '115.80480258164016],[2058.8542357820797,882.0115506330139],[2144.4909450168548,' \
                             '796.969122302397],[2154.9016297157928,787.1917709367922],[2107.316672518567,' \
                             '835.4100614673512],[2085.75128947322,857.6611563563938],[2179.909307197659,' \
                             '764.1658927068311],[2209.957522413003,734.8176774914868],[3025.756296579397,' \
                             '27.808416758485237],[3061.0175687885458,6.30109057477739],[3215.3918994234064,' \
                             '43.40530481857468],[3116.7677003148997,183.63781718712016],[3178.893825616839,' \
                             '122.77180883524716],[2950.0203416198674,352.23957373637677],[3389.2319550934676,' \
                             '7.174613171904184],[3748.2108699680625,618.667902083273],[3366.0092011565835,' \
                             '1001.1167146526309],[3535.4817305386136,844.7213567442091],[3481.1625990791954,' \
                             '899.7479061927752],[3502.673559157706,878.9477646249425],[3513.3796674813993,' \
                             '868.8907274997491],[3471.84125999672,911.1291349844282],[3646.2122342661305,' \
                             '737.4467225233338],[3667.940799780387,716.4585270941084],[3740.2581659898296,' \
                             '644.7744942179988],[4296.441240505153,89.23062378946179],[3580.4517632129237,' \
                             '805.8934344150239],[4275.7317507727885,111.44678018849208],[4527.786663158577,' \
                             '24.378668314829156],[4480.967483903662,105.30520679680649],[4621.059021497365,' \
                             '17.38391606393452],[4580.515490533927,159.63358066457295],[4633.300674504164,' \
                             '107.63123940681089],[4433.899035541155,307.6819495683194],[4373.617401857211,' \
                             '368.61265445076333],[4551.5051727134,191.35821692790796],[4696.96829817118,' \
                             '47.0617581367942],[5103.562531104451,680.0813843633732],[4963.700621351832,' \
                             '825.2886729943566],[5149.302611131317,671.0373235029228],[5114.379918789251,' \
                             '706.8487459713115],[5004.925027648842,817.2624277926298],[5064.127797911033,' \
                             '758.8421857984449],[4949.1593328687695,874.4597220392079],[5097.960172794525,' \
                             '726.3992521984837],[5931.906238311757,9.104225707555088],[5979.54290233907,' \
                             '27.89436157813452],[5993.100687416581,22.695994348107888],[6065.280638860605,' \
                             '115.11936113939464],[6576.319261581611,649.6550225838],[6420.348193541168,' \
                             '806.2209312520563],[6509.517591952049,718.6946444628047],[6494.3843209274255,' \
                             '766.0425540217366],[6590.977911614666,670.0980345329963],[6469.0877328024235,' \
                             '792.6372845437381],[6299.557442116381,963.0892122511368],[6211.962685334828,' \
                             '1051.2782499368477],[7186.7329884263445,77.15701804383116],[6181.555379536486,' \
                             '1083.045445444368],[6546.110136049841,719.2888313280127],[6570.765777537772,' \
                             '695.4665231734143],[7307.638620952216,69.90864843416784],[7420.1019064261,' \
                             '17.114331891591064],[7365.207577685139,220.343024629683],[7375.388217982524,' \
                             '244.76085321597566],[7313.8773487641865,306.90505576764645],[7589.029100779826,' \
                             '32.40237495050678],[7461.719586222787,160.51003190454503],[7681.7712698667365,' \
                             '13.179252730265034],[7645.732432066756,71.91377293778623],[7948.7758526743255,' \
                             '751.3732185241752],[7998.931672014726,701.9840658504409],[8688.767427664574,' \
                             '12.981643533927127],[7784.343478696832,918.3909331609539],[7806.296274726568,' \
                             '897.1381371312182],[7640.756287512129,1063.3666861539732],[8677.155084543267,' \
                             '27.66788912283664],[7652.583524151956,1052.9798195991789],[7850.07767082265,' \
                             '856.1856729284855],[8841.149942815722,127.2956035368843],[9003.81144912103,' \
                             '34.6659737343889],[8784.068699263937,276.1313007360641],[8894.920598338287,' \
                             '165.9794016617143],[8968.320401936251,93.27959806375111],[9023.782802589907,' \
                             '38.55756749512693],[8955.844967577044,107.32873584132358],[8743.597638226365,' \
                             '320.2868837026799],[8731.553579473743,332.9800136538033],[8869.42523186982,' \
                             '195.75743245622652],[8986.394713819702,79.4736623500412],[8990.857655004229,' \
                             '75.74698843413717],[8998.601957295921,68.77755985081967],[9197.66696526728,' \
                             '889.9059505512305],[10060.689886050934,79.66912493620839],[9260.476451574354,' \
                             '880.5453134876643],[9168.615036999508,973.2424528174961],[9337.125239726847,' \
                             '805.381321288658],[9423.415624293935,719.7766485652664],[9453.172121438192,' \
                             '690.6829054958853],[9144.94160015963,999.6019885827645],[9429.574122534368,' \
                             '715.6802847187028],[9183.998815374558,961.9046630770135],[9066.885288599935,' \
                             '1079.7181898516374],[10236.47198038116,263.9548945680017],[10326.2757344297,' \
                             '174.8511405194622],[10367.16887243994,134.84673263554578],[10438.454400652641,' \
                             '64.24976623115981],[10259.345838052443,244.05832883135918],[10367.36081821231,' \
                             '136.81001533815834],[10194.47646537186,310.4772108910838],[10433.729834490641,' \
                             '72.0571751056359],[10399.707230822476,106.82014885883291],[10498.007158812425,' \
                             '22.714418611582005],[10731.149407273839,817.9485960513866],[10657.919079447485,' \
                             '907.8674778732893],[10495.79511646607,1084.6317584830922],[10597.530189931816,' \
                             '983.9300183506784],[10523.086758724812,1059.5401162243488],[10595.832281303015,' \
                             '987.5927360431451],[11656.793549575374,9.838378241742248],[11585.738355058053,' \
                             '141.6130202999575],[11776.364811910693,7.932740419630136],[11619.242037835871,' \
                             '179.10652316205778],[11732.197152455903,208.00593482692057],[11597.307931934587,' \
                             '343.61505431493606],[11870.816669590622,71.08705682896289],[11821.872305224722,' \
                             '120.73142119486329],[11835.67643444298,107.66766206163811],[11812.025564915779,' \
                             '132.15186492217254],[11673.875238427225,271.14212604496606],[11971.03910952124,' \
                             '58.130942305577264],[12250.64417933801,769.705804788613],[12050.341202111364,' \
                             '970.7450492838834],[12297.365772785006,724.6259961122614],[12958.306358707574,' \
                             '64.66615035975519],[12931.736514177472,91.9359948898582],[12195.623226071051,' \
                             '828.7896530813105],[12245.58904153877,779.472908812093],[12134.265402814706,' \
                             '891.6965475361558],[12980.895552943097,45.86453980476472],[13248.842624338044,' \
                             '131.30644686045707],[13039.707151538594,341.2247623723815],[13324.279466512515,' \
                             '57.55796490048124],[13116.113308521564,266.5222652884313],[13138.731122543979,' \
                             '244.97793961715251],[13393.366832506239,31.49004566662734],[13431.830546423096,' \
                             '53.30173805062077],[13739.123730188987,667.4788517239431],[13517.457492774582,' \
                             '890.727593915266],[13749.444219384162,710.7048518143383],[13594.397867748,' \
                             '866.5911380847392],[13409.799944917397,1052.0223942486773],[13656.019556542358,' \
                             '806.4518538222164],[13575.2890947745,887.9571892984495],[13456.738636397822,' \
                             '1007.2076476751281],[13399.987301914083,1064.6080533573677],[13630.450971901035,' \
                             '834.97771670375],[13631.816062309206,834.4716372827206],[14659.004396067692,' \
                             '161.41724095366408],[14470.660623956277,350.741753235141],[14715.52141751948,' \
                             '106.62132975697023],[14610.430709933962,212.41203734248847],[15078.968158929987,' \
                             '821.1809122685136],[15009.702774805273,891.3679334145836],[15032.055094230289,' \
                             '869.7156139895687],[14904.371423787614,998.110102942921],[15048.028083411868,' \
                             '855.4341834887291],[14988.67848272081,915.4837841797871],[16023.96975641587,' \
                             '7.703964111202367],[16077.100264071674,43.68959216044277],[16149.475285554387,' \
                             '25.633435077359536],[16102.316367220388,158.0891502816321],[16093.03241955862,' \
                             '168.29473496475657],[16206.544569079995,55.48258544338205],[17303.10935878098,' \
                             '7.7280840603598335],[16313.022727670894,1027.3772723291077],[16533.23635468779,' \
                             '808.0905202613758],[16412.326748901804,929.710944558039],[16514.95421905645,' \
                             '827.9168077367249],[16447.80644774666,895.7136502450121],[16272.511719977634,' \
                             '1071.6417113473744],[16373.818311233852,971.020831934853],[16594.40308605845,' \
                             '751.1723243788765],[16297.83036508906,1048.339326252426],[16587.327372658896,' \
                             '759.4913898810883],[17345.781724355093,8.731146825131873],[17563.74248784929,' \
                             '75.74584189718007],[17673.333346718624,26.815724479874916],[17457.113077169062,' \
                             '243.81883674190976],[17599.129421387843,102.56915918979576],[17536.05331775083,' \
                             '166.27859616014393],[18099.420326669788,680.9851908322307],[18734.653088018567,' \
                             '46.67406650480552],[17878.68445331142,903.3427012119537],[17986.838580698066,' \
                             '796.1154487744716],[17927.717751784483,855.9470961987317],[18842.45374273839,' \
                             '22.08058415985579],[18889.91401669762,250.32635338740874],[18828.701175137336,' \
                             '312.27956503272435],[18856.1123522526,285.51745911595935],[18789.637094576985,' \
                             '352.89271679157537],[18825.209544465273,317.969338101786],[18949.13460533051,' \
                             '194.8424196335509],[18860.19022131232,284.5616773601141],[18982.319347559114,' \
                             '163.46588444665394],[18954.624124331243,191.86110767452556]],"xmean":9078.256925942997,' \
                             '"xmedian":8994.729806150075,"ymean":468.12554316410143,"ymedian":342.4199083436588,' \
                             '"version":235} '

    fixed_incentive_test = 10.0
    variable_rate_test = 2.0
    deliveries_per_day_test = 2.0
    od_percentage_test = 1.2
    min_vot_test = 5.0
    customer_order_rate_test = 3.0
    OD_arrival_rate_test = 1.0
    cost_per_distance_test = 2.0
    loss_aversion_parameter_test = 7
    run_duration_test = 24772

    capture_run_results(data_path_test, fixed_incentive_test, variable_rate_test, deliveries_per_day_test,
                        od_percentage_test, min_vot_test,
                        customer_order_rate_test, OD_arrival_rate_test, cost_per_distance_test,
                        loss_aversion_parameter_test,
                        OD_VOT_data_test, run_deliveries_data_test,
                        incentives_paid_data_test, run_savings_data_test, original_route_data_test,
                        waiting_time_data_test, run_duration_test)


if __name__ == '__main__':
    main()
