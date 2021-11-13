import json
import pandas as pd
import numpy as np
from scipy.spatial import distance
import math


def calculate_distances(od_candidate_x, od_candidate_y, depot_data, current_od):
    original_distance = distance.euclidean((depot_data['x'], depot_data['y']),
                                           (current_od['x_home'], current_od['y_home']))
    deviated_distance = distance.euclidean((depot_data['x'], depot_data['y']),
                                           (od_candidate_x, od_candidate_y)) + distance.euclidean(
        (od_candidate_x, od_candidate_y), (current_od['x_home'], current_od['y_home']))

    # print("Original Distance = ", original_distance)
    # print("New Possible Distance = ", deviated_distance)
    # print("Deviation = ", deviation)

    return original_distance, deviated_distance


def calculate_absolute_deviation_distance(od_candidate_x, od_candidate_y, depot_data, current_od):
    # all these values are still in "pixel" units
    original_distance = distance.euclidean((depot_data['x'], depot_data['y']),
                                           (current_od['x_home'], current_od['y_home']))
    deviated_distance = distance.euclidean((depot_data['x'], depot_data['y']),
                                           (od_candidate_x, od_candidate_y)) + distance.euclidean(
        (od_candidate_x, od_candidate_y), (current_od['x_home'], current_od['y_home']))
    deviation = deviated_distance - original_distance

    # change to adjust to scale (10 pixels = 1km)

    deviation /= 10

    # print("Original Distance = ", original_distance / 10, "km")
    # print("New Possible Distance = ", deviated_distance / 10, "km")
    # print("Deviation = ", deviation * 10, " pixels")
    # print("Deviation = ", deviation, " km")

    # output in km
    return deviation


def calculate_deviation_time(deviation_distance, current_od):
    # change from distance deviation to time deviation based on the ODs speed
    deviation_time = deviation_distance * (1 / current_od['speed'])  # km * (h/km)

    # print("Distance = ", deviation_distance)
    # print("Speed = ", current_od['speed'])
    # print("Deviation time = ", deviation_time)

    return deviation_time


def calculate_value_of_deviation(deviation_time, current_od):
    return deviation_time * current_od['value_of_time']


def calculate_value_of_deviation_2(deviation_time, current_od):
    value_of_time = (current_od['max_time_deviation'] / 2) / (current_od['max_time_deviation'] - deviation_time)
    return value_of_time


def calculate_incentive(deviation, fixed_incentive_arg, variable_incentive_arg, maximum_incentive_arg):
    total_incentive = fixed_incentive_arg + (deviation * variable_incentive_arg)
    if total_incentive > maximum_incentive_arg:
        return maximum_incentive_arg
    else:
        return total_incentive


def calculate_perceived_gain(incentive, deviation_value):
    if deviation_value < 0:
        return 0
    else:
        return incentive - deviation_value


def calculate_utility(incentive, deviation_value):
    # current_od['value_of_time']
    return math.sqrt(incentive) * math.sqrt(500 - deviation_value)


def evaluate_od_candidates(candidates_data, current_od_data, depot_data, fixed_incentive, variable_incentive, maximum_incentive):
    pd.set_option("display.max_rows", None, "display.max_columns", None)

    # print("In evaluate OD python function")
    # print("Candidate data; ", candidates_data)
    # print("Current OD Data: ", current_od_data)
    # print("Depot Data: ", depot_data)

    # define and fill dataframe with od_candidates
    df_candidates = pd.DataFrame(np.zeros((len(candidates_data), 4)), columns=['_index', 'x', 'y', 'cost_to_serve'])
    for (columnName, columnData) in df_candidates.iteritems():
        df_candidates[columnName] = [candidate[columnName] for candidate in candidates_data if columnName in candidate]

    ##########################################################################################
    # Calculations section
    ################################################################################

    # this is in km units
    df_candidates['Absolute_Deviation'] = df_candidates.apply(
        lambda row: calculate_absolute_deviation_distance(row['x'], row['y'], depot_data, current_od_data), axis=1)

    # this is in hour unit
    df_candidates['Deviation_time'] = df_candidates.apply(
        lambda row: calculate_deviation_time(row['Absolute_Deviation'], current_od_data), axis=1)

    # this is in $ unit
    df_candidates['Value_of_deviation_time'] = df_candidates.apply(
        lambda row: calculate_value_of_deviation(row['Deviation_time'], current_od_data), axis=1)

    df_candidates['Value_of_deviation_time_2'] = df_candidates.apply(
        lambda row: calculate_value_of_deviation_2(row['Deviation_time'], current_od_data), axis=1)

    # this is in $ unit
    df_candidates['Incentive_Offered'] = df_candidates.apply(
        lambda row: calculate_incentive(row['Absolute_Deviation'], fixed_incentive, variable_incentive,
                                        maximum_incentive), axis=1)

    df_candidates['Perceived_Gain'] = df_candidates.apply(
        lambda row: calculate_perceived_gain(row['Incentive_Offered'], row['Value_of_deviation_time']), axis=1)

    df_candidates['Perceived_Gain_2'] = df_candidates.apply(
        lambda row: calculate_perceived_gain(row['Incentive_Offered'], row['Value_of_deviation_time_2']), axis=1)
    # print(df_candidates)

    # %% try to incorporate another utlility function

    df_candidates['Utility'] = df_candidates.apply(
        lambda row: calculate_utility(row['Value_of_deviation_time'], row['Incentive_Offered']), axis=1)

    # print(df_candidates)

    ###########################################################################################
    #  Sort by perceived gain
    ###########################################################################################

    df_candidates = df_candidates.sort_values(by=['Perceived_Gain'], ascending=False)
    # print(df_candidates)

    ###########################################################################################
    #  Here we assume that the customer will chose the delivery with
    #  the largest possible gain
    #   Furthermore, we assume they only select them if perceived gain
    #   is positive
    ###########################################################################################

    trip_evaluation_dict = {"OD_index": current_od_data['_index'],
                            "Selected_Customer_Index": int(df_candidates.iloc[0]['_index']),
                            "Incentive_Offered": df_candidates.iloc[0]['Incentive_Offered'],
                            "Perceived_Gain": df_candidates.iloc[0]['Perceived_Gain']}
    trip_evaluation_dict_json = json.dumps(trip_evaluation_dict)
    # print(trip_evaluation_dict_json)

    return trip_evaluation_dict_json


# def add(a, b, c):
#     return a + b + c


# def main():
#     # create a dictionary with
#     # three fields each
#     data = {
#         'A': [1, 2, 3],
#         'B': [4, 5, 6],
#         'C': [7, 8, 9]}
#
#     # Convert the dictionary into DataFrame
#     df = pd.DataFrame(data)
#     print("Original DataFrame:\n", df)
#
#     df['add'] = df.apply(lambda row: add(row['A'],
#                                          row['B'], row['C']), axis=1)


def main():
    """main()"""
    candidates_test = [
        {'$SWITCH_TABLE$vrp_first_attempt$Customer$statechart_state': [1, 2, 3, 4, 5, 6, 7, 8], 'due_time': 44.0,
         'service_time': 10.0, '_index': 4, '_text6': 19, '_text7': 20, '_text4': 2, '_text5': 18, '_text2': 16,
         'ready_time': 34.0, '_text3': 17, 'cost_to_serve': 10.0, '_house': 13, '_text1': 15, 'demand': 26.0,
         '_roundRectangle1': 1, '_order_circle': 21, 'x': 15.0, 'y': 30.0, 'id': 5, '_group1': 3, '_text': 14},
        {'$SWITCH_TABLE$vrp_first_attempt$Customer$statechart_state': [1, 2, 3, 4, 5, 6, 7, 8], 'due_time': 107.0,
         'service_time': 10.0, '_index': 8, '_text6': 19, '_text7': 20, '_text4': 2, '_text5': 18, '_text2': 16,
         'ready_time': 97.0, '_text3': 17, 'cost_to_serve': 64.0, '_house': 13, '_text1': 15, 'demand': 16.0,
         '_roundRectangle1': 1, '_order_circle': 21, 'x': 55.0, 'y': 60.0, 'id': 9, '_group1': 3, '_text': 14}]

    od_test = {'y_home': 14.78621164329888, '_index': 9, 'value_of_time': 5.503391576577617, '_text7': 19, '_text4': 13,
               '_text5': 16, '_text2': 7, 'income_level': 2.0, 'arrival_rate': 20.0, 'speed': 10, '_text3': 10,
               '_text1': 4, 'max_time_deviation': 0.3,
               '_roundRectangle': 3, '_group4': 17, '_group6': 20, 'trip_accepted': False, '_group1': 8, '_group3': 14,
               'time_per_distance': 1.0, '_group2': 11, 'customer_to_serve': None, '_shapeBody': 1, '_person': 2,
               '_roundRectangle6': 18, '_roundRectangle4': 15, '_roundRectangle3': 12, '_roundRectangle2': 9,
               '_roundRectangle1': 6, 'x_home': 55.17889686537972, 'incumbent_best': None,
               '$SWITCH_TABLE$vrp_first_attempt$Occasional_Driver$statechart_state': [1, 2, 3, 4, 5], '_group': 5}

    depot_test = {'due_time': 230.0, 'service_time': 0.0, '_warehouse': 8, '_text4': 11, '_text5': 9, 'x': 35.0,
                  'y': 35.0, 'ready_time': 0.0, 'id': 0, '_group1': 12, 'demand': 0.0, '_roundRectangle1': 10}

    fixed_incentive_test = 2.0
    variable_incentive_test = 0.1
    maximum_incentive_test = 3.0

    evaluate_od_candidates(candidates_test, od_test, depot_test, fixed_incentive_test, variable_incentive_test, maximum_incentive_test)


if __name__ == '__main__':
    main()
