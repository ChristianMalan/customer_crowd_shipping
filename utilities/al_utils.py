# %%
import pandas as pd
import json


# %%
def split_data_customer(JsonString):
    customer_data = json.dumps(JsonString["customers"])
    # print(customer_data)
    return customer_data


def split_data_depot(JsonString):
    depot_data = json.dumps(JsonString["depot"])
    # print(depot_data)
    return depot_data


# def split_data_vehicle(JsonString):
#     num_vehicles = json.dumps(JsonString["max_vehicle_number"])
#     vehicle_capacity = json.dumps(JsonString["vehicle_capacity"])
#
#     # print(num_vehicles, vehicle_capacity)
#
#     return num_vehicles, vehicle_capacity

def split_data_num_vehicle(JsonString):
    num_vehicles = json.dumps(JsonString["max_vehicle_number"])

    # print(num_vehicles, vehicle_capacity)

    return num_vehicles


def split_data_vehicle_capacity(JsonString):
    vehicle_capacity = json.dumps(JsonString["vehicle_capacity"])

    # print(vehicle_capacity)

    return vehicle_capacity
