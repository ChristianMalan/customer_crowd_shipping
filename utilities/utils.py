import os
import io
import fnmatch
import json
from json import load, dump
from . import BASE_DIR
import pandas as pd
import math


def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier


def round_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier


def make_dirs_for_file(path):
    """utilities.uitls.make_dirs_for_file(path)"""
    try:
        os.makedirs(os.path.dirname(path))
    except OSError:
        pass


def calculate_distance(customer1, customer2):
    """utilities.uitls.calculate_distance(customer1, customer2)"""
    return ((customer1['x'] - customer2['x']) ** 2 +
            (customer1['y'] - customer2['y']) ** 2) ** 0.5


def text2json(customize=False):
    """utilities.uitls.text2json(customize=False)"""
    text_data_dir = os.path.join(BASE_DIR, 'data', 'text_customize' if customize else 'text')
    json_data_dir = os.path.join(BASE_DIR, 'data', 'json_customize' if customize else 'json')
    for text_file in map(lambda text_filename: os.path.join(text_data_dir, text_filename),
                         fnmatch.filter(os.listdir(text_data_dir), '*.txt')):
        json_data = {}
        df_temp = pd.DataFrame(columns=["id", "x", "y", "demand", "ready_time", "due_time", "service_time"])

        with io.open(text_file, 'rt', newline='') as file_object:
            for line_count, line in enumerate(file_object, start=1):
                if line_count in [2, 3, 4, 6, 7, 8, 9]:  # skip empty lines
                    pass

                elif line_count == 1:
                    # <Instance name>
                    json_data['instance_name'] = line.strip()

                elif line_count == 5:
                    # <Maximum vehicle number>, <Vehicle capacity>
                    values = line.strip().split()
                    json_data['max_vehicle_number'] = int(values[0])
                    json_data['vehicle_capacity'] = float(values[1])

                elif line_count == 10:
                    # <Depot>
                    # Custom number = 0, depart
                    # <Custom number>, <X coordinate>, <Y coordinate>,
                    # ... <Demand>, <Ready time>, <Due date>, <Service time>
                    values = line.strip().split()
                    json_data['depot'] = {
                        'x': float(values[1]),
                        'y': float(values[2]),
                        'demand': float(values[3]),
                        'ready_time': float(values[4]),
                        'due_time': float(values[5]),
                        'service_time': float(values[6]),
                    }
                else:
                    # <Customers>
                    # <Custom number>, <X coordinate>, <Y coordinate>,
                    # ... <Demand>, <Ready time>, <Due date>, <Service time>
                    print("here")
                    values = line.strip().split()
                    # read from text file into a dataframe, capture customer data
                    print("here 1")
                    df_temp = df_temp.append({'id': int(values[0]), 'x': float(values[1]), 'y': float(values[2]),
                                              'demand': float(values[3]), 'ready_time': float(values[4]),
                                              'due_time': float(values[5]), 'service_time': float(values[6])},
                                             ignore_index=True)
                    print("here 2")

        customer_data_json_string = df_temp.to_json(orient="records")  # convert customer dataframe to json
        print("here 3")

        customer_data_parsed = json.loads(customer_data_json_string)  # parse json string
        print("here 4")

        json_data['customers'] = customer_data_parsed  # add customer array to json data

        # customers = json_data['depot'] + json_data['customers']
        #
        # print(customers)

        # json_data['distance_matrix'] = [[calculate_distance(json_data[customer1], \
        #                                                     json_data[customer2]) for customer1 in customers] for
        #                                 customer2 in customers]
        json_file_name = f"{json_data['instance_name']}.json"
        json_file = os.path.join(json_data_dir, json_file_name)
        print(f'Write to file: {json_file}')
        make_dirs_for_file(path=json_file)
        with io.open(json_file, 'wt', newline='') as file_object:
            dump(json_data, file_object, sort_keys=True, indent=4, separators=(',', ': '))


def routes2sol(routes):
    """Concatenates a list of routes to a solution. Routes may or may not have
    visits to the depot (node 0), but the procedure will make sure that
    the solution leaves from the depot, returns to the depot, and that the
    routes are separated by a visit to the depot."""
    if not routes:
        return None

    sol = [0]
    for r in routes:
        if r:
            if r[0] == 0:
                sol += r[1:]
            else:
                sol += r
            if sol[-1] != 0:
                sol += [0]
    return sol


def objf(sol, D):
    """A quick procedure for calclulating the quality of an solution (or a
    route). Assumes that the solution (or the route) contains all visits (incl.
    the first and the last) to the depot."""
    return sum((D[sol[i - 1], sol[i]] for i in range(1, len(sol))))
