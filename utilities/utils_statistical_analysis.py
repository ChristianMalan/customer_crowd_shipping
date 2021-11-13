import scipy.stats as stats
from pathlib import Path
import os
from scipy.stats import mannwhitneyu
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from bioinfokit.analys import stat

import pandas as pd
import numpy as np
import json
import researchpy


def shapiro_wilk_normality(json_file_path, dir_path_string, kpi):
    with open(dir_path_string / json_file_path, 'r+') as file:
        data = json.load(file)

    try:
        df = pd.DataFrame.from_dict(data, orient="columns")
        df = df.reindex(sorted(df.columns), axis=1)

        df_shapiro_results = pd.DataFrame(np.nan, index=['test_stat', 'p_value', 'outcome'], columns=df.columns)

        for i in df.columns:
            shapiro_test = stats.shapiro(df[i])
            # print(shapiro_test.statistic)
            df_shapiro_results.loc['test_stat', i] = shapiro_test.statistic
            df_shapiro_results.loc['p_value', i] = shapiro_test.pvalue
            if df_shapiro_results[i]['p_value'] < 0.05:
                df_shapiro_results.loc['outcome', i] = 'Non-Normal'
            else:
                df_shapiro_results.loc['outcome', i] = 'Normal'

        # print(df_shapiro_results)
        df_shapiro_results.to_csv(dir_path_string / f"Shapiro_Wilk_Normality_{kpi}_output.csv", index=False)
    except:
        print("Something went wrong")


def tukey_stat_test(json_file_path, dir_path_string, kpi):
    with open(dir_path_string / json_file_path, 'r+') as file:
        data = json.load(file)

    pairwise_tukeyhsd()


def paired_t_test(json_file_path, dir_path_string, kpi):
    with open(dir_path_string / json_file_path, 'r+') as file:
        data = json.load(file)

    try:
        df = pd.DataFrame.from_dict(data, orient="columns")
        df = df.reindex(sorted(df.columns), axis=1)

        df_p_values = pd.DataFrame(np.nan, index=df.columns, columns=df.columns)
        df_t_values = pd.DataFrame(np.nan, index=df.columns, columns=df.columns)

        for i in df.columns:
            for j in df.columns:
                t_value, p_value = stats.ttest_rel(df[i], df[j])
                df_p_values[i][j] = p_value
                df_t_values[i][j] = t_value

        # print(df_p_values)
        # print(df_t_values)

        df_p_values.to_csv(dir_path_string / f"t_test_{kpi}_p_values.csv", index=True)
        df_t_values.to_csv(dir_path_string / f"t_test_{kpi}_t_values.csv", index=True)
    except:
        print("Number of samples not equal")


def anova_test(json_file_path, dir_path_string, kpi):
    print("Anova start")

    with open(dir_path_string / json_file_path, 'r+') as file:
        data = json.load(file)

    try:

        df_data = pd.DataFrame.from_dict(data, orient="columns")
        df_data = df_data.reindex(sorted(df_data.columns), axis=1)

        fvalue, pvalue = stats.f_oneway(*df_data.values)
        df_ANOVA_values = pd.DataFrame({'f_value': [fvalue], 'p_value': [pvalue]})
        print(df_ANOVA_values)

        # df_p_values = pd.DataFrame(np.nan, index=df.columns, columns=df.columns)
        # df_f_values = pd.DataFrame(np.nan, index=df.columns, columns=df.columns)
        #
        # for i in df.columns:
        #     for j in df.columns:
        #         fvalue, pvalue = stats.f_oneway(df[i], df[j])
        #         df_p_values[i][j] = pvalue
        #         df_f_values[i][j] = fvalue
        #
        # print(df_p_values)
        # print(df_f_values)
        #
        df_ANOVA_values.to_csv(dir_path_string / f"ANOVA_{kpi}_values.csv", index=True)
    # df_f_values.to_csv(dir_path_string / f"ANOVA_{kpi}_f_values.csv", index=True)

    except:
        print("Error my bra")


def mannwhitneyu_func(json_file_path, dir_path_string, kpi):
    with open(dir_path_string / json_file_path, 'r+') as file:
        data = json.load(file)

    try:
        df = pd.DataFrame.from_dict(data, orient="columns")
        df = df.reindex(sorted(df.columns), axis=1)

        df_p_values = pd.DataFrame(np.nan, index=df.columns, columns=df.columns)
        df_stat_values = pd.DataFrame(np.nan, index=df.columns, columns=df.columns)

        for i in df.columns:
            print(i)
            for j in df.columns:
                stat, pvalue = mannwhitneyu(df[i], df[j])
                df_p_values[i][j] = pvalue
                df_stat_values[i][j] = stat

        df_p_values.to_csv(dir_path_string / f"mannwhitneyu_{kpi}_p_values.csv", index=True)
        df_stat_values.to_csv(dir_path_string / f"mannwhitneyu_{kpi}_stats_values.csv", index=True)
    except:
        print("Number of samples not equal")


def confidence_intervals(json_file_path, dir_path_string, kpi):
    with open(dir_path_string / json_file_path, 'r+') as file:
        data = json.load(file)

    try:
        print("In CI")
        df = pd.DataFrame.from_dict(data, orient="columns")
        df = df.reindex(sorted(df.columns), axis=1)
        results = researchpy.summary_cont(df)
        print(results)
        results.to_csv(dir_path_string / f"CI_{kpi}_summary.csv", index=True)
    except:
        print("CI failed")


def confidence_intervals_t_dist(json_file_path, dir_path_string, kpi):
    with open(dir_path_string / json_file_path, 'r+') as file:
        data = json.load(file)

    try:
        print("In CI")
        df = pd.DataFrame.from_dict(data, orient="columns")
        df = df.reindex(sorted(df.columns), axis=1)
        results = researchpy.summary_cont(df)
        print(results)
        results.to_csv(dir_path_string / f"CI_t_distribution_{kpi}_summary.csv", index=True)
    except:
        print("CI failed")


def main():
    path_parent_folder = Path(os.path.dirname(os.getcwd()))
    test_path = path_parent_folder / "exports"
    path_string_test = "experiment_waiting_time_means.json"
    print(test_path / path_string_test)

    # anova_test(path_string_test, test_path)
    # mannwhitneyu_func(path_string_test, test_path)
    # shapiro_wilk_normality(path_string_test, test_path, "test_kpi")

    # Scenario_1_savings = [[0.9207, 1.3777, 1.3936, 1.1572, 0.6302], [0.8082, 0.7561, 0.924, 0.7702, 0.6585],
    #                       [1.1791, 1.6195, 1.6891, 1.4035, 0.8408], [1.179, 1.620, 1.689, 1.404, 0.841]]
    #
    # df_Scenario_1 = pd.DataFrame(Scenario_1_savings, columns=['mean', 'std_dev', 'lower_bound', 'upper_bound'], index=1)
    #
    # print(df_Scenario_1)


if __name__ == '__main__':
    main()
