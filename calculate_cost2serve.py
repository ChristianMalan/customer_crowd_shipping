# %%
import json
import matplotlib.pyplot as plt
from vrp_algorithms.Sweep import run_vehicle_routing_sweep
from vrp_algorithms.savings import run_vehicle_routing_savings
import time


def calculate_distance_to_serve(customer_data, vehicle_capacity_data, depot_data, routing_heuristic_index=0):
    tic = time.perf_counter()

    if routing_heuristic_index == 0:
        total_vrp_result = json.loads(run_vehicle_routing_sweep(customer_data, vehicle_capacity_data, depot_data))
    else:
        total_vrp_result = json.loads(run_vehicle_routing_savings(customer_data, vehicle_capacity_data, depot_data))

    # print(total_vrp_result)
    total_vrp_distance = round(sum(item["route_distance"] for item in total_vrp_result), 4)
    # print("Total cvrp distance: ", total_vrp_distance)

    distance_to_serve_list = []
    distance_to_serve_dict = []

    for i in range(0, len(customer_data)):

        temp_dict = {}

        c = customer_data.pop(i)  # we are calculating the distance_to_serve of c. remove him from cvrp customers

        temp_dict = {"index": c['id'] - 1}

        # print(customer_data)

        if len(customer_data) > 0:
            if routing_heuristic_index == 0:
                vrp_results = run_vehicle_routing_sweep(customer_data, vehicle_capacity_data,
                                                        depot_data)  # run vrp on all but c
            else:
                vrp_results = run_vehicle_routing_savings(customer_data, vehicle_capacity_data,
                                                          depot_data)

            vrp_results_parsed = json.loads(vrp_results)  # parse results
            current_vrp_distance = sum(
                item["route_distance"] for item in vrp_results_parsed)  # calculate total distance for current instance
            customer_data.insert(i, c)  # put c back into the list of customers

        else:
            current_vrp_distance = 0

        current_distance_to_serve = total_vrp_distance - current_vrp_distance  # distance to serve as difference between serving with or without c
        distance_to_serve_list.append(current_distance_to_serve)  # add to distance_to_serve list
        temp_dict["distance_to_serve"] = round(current_distance_to_serve, 4)  #
        distance_to_serve_dict.append(temp_dict)
        distance_to_serve_dict_json = json.dumps(distance_to_serve_dict)  # json.dumps is used to make the dictionary

        # print( f"Current cvrp distance: {current_vrp_distance}. Customer {c['id']-1} has a distance to serve of {
        # current_distance_to_serve}.")

    print(distance_to_serve_dict_json)
    toc = time.perf_counter()
    print(f"Calculated distance to serve in {toc - tic:0.4f} seconds")

    return distance_to_serve_dict_json


# %%
def main():
    """main()"""
    with open("vrp_algorithms/test_data/C5.json") as inputFile:
        data = json.load(inputFile)

    customer_data_test = data["customers"]  # this will be replaced with the customer data rec
    depot_data_test = data["depot"]
    vehicle_capacity_data_test = data["vehicle_capacity"]

    calculate_distance_to_serve(customer_data_test, vehicle_capacity_data_test, depot_data_test, 1)


if __name__ == '__main__':
    main()
