from __future__ import print_function
from __future__ import division
import json
from math import degrees, atan2, sqrt
from scipy.spatial import distance_matrix
import numpy as np
import datetime
from pathlib import Path
from builtins import range
import os

import matplotlib as mpl
import matplotlib.font_manager as font_manager


from logging import log, DEBUG
from utilities.utils import routes2sol, objf

S_EPS = 1e-10
C_EPS = 1e-10

mpl.rcParams['font.family'] = 'serif'
cmfont = font_manager.FontProperties(fname=mpl.get_data_path() + '/fonts/ttf/cmunrm.ttf')
mpl.rcParams['font.serif'] = cmfont.get_name()
mpl.rcParams['mathtext.fontset'] = 'cm'
mpl.rcParams['font.size'] = 11
mpl.rcParams['axes.unicode_minus'] = False

import matplotlib.pyplot as plt


class Position:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ") "

    def x_coor(self):
        return self.x

    def y_coor(self):
        return self.y


class Customer:
    id = 0
    pos = Position(-1, -1)
    demand = 0
    due_time = 0
    ready_time = 0
    service_time = 0

    def set_id(self, id_var):
        self.id = id_var

    def __init__(self, name):
        self.name = name

    def set_position(self, x, y):
        self.pos = Position(x, y)

    def set_demand(self, d):
        self.demand = d

    def set_due_time(self, d_time):
        self.due_time = d_time

    def set_ready_time(self, r_time):
        self.ready_time = r_time

    def set_service_time(self, s_time):
        self.service_time = s_time

    def set_angle_with_depot(self, a):
        self.angleWithDepot = a

    def __str__(self):
        return "Customer " + str(self.id - 1) + "  (" + str(self.pos.x) + ", " + \
               str(self.pos.y) + ") demand: " + str(self.demand)
        # return  "(" + str(self.pos.x) + ", " + \
        #        str(self.pos.y) + " )"


def create_distance_matrix(customer_list):
    """Takes in as argument a list of Customers, returns a distance matrix"""
    x_temp, y_temp = zip(*[(float(i.pos.x), float(i.pos.y)) for i in customer_list])
    matrix_double = np.column_stack([x_temp, y_temp])
    matrix = distance_matrix(matrix_double, matrix_double)

    matrix = np.rint(matrix)
    return matrix


def print_tuple(t):
    print("["),
    for i in t:
        print(i),
    print("]")


def copy(li):
    return [i for i in li]


def get_distance(cus1, cus2):
    # Euclidean
    dist = sqrt(((cus1.pos.x - cus2.pos.x) ** 2) + ((cus1.pos.y - cus2.pos.y) ** 2))
    return dist


def get_route_as_objects(route_index, route_nodes_object):
    """This function translates a route in the form of their local order, to a list of the actual objects """
    """e.g. [0,1,3,2,0] is translated to [DEPOT, Customer(79), Customer(6), Customer(50), DEPOT"""

    route_node = {}
    final = []
    counter = 0
    for node in route_index:
        route_node[counter] = node
        counter += 1
        final.append(route_nodes_object[node])
        # print('Route node object: ', route_nodes_object[node])
        # Customers.index #Still needs to be added
    return final


def route_index_to_id(route_index, route_nodes_object):
    """This function translates a route in the form of their local order, to a list of the actual objects """
    """e.g. [0,1,3,2,0] is translated to [DEPOT, Customer(79), Customer(6), Customer(50), DEPOT"""

    route_node = {}
    final = []
    counter = 0
    for node in route_index:
        route_node[counter] = node
        counter += 1
        final.append(route_nodes_object[node].id - 1)
        # print('Route node object: ', route_nodes_object[node])
        # Customers.index #Still needs to be added
    return final


def get_route_as_object_index(final_route_objects, customer_list, depot):
    """This function translates a route in the form of their objects to their indices """
    """e.g. [DEPOT, Customer(5), Customer(0), DEPOT] is translated to [-1, 5 , 0,-1]"""

    final = []
    # print("customer_list", customer_list)
    # print("final_route_objects", final_route_objects)
    for node in final_route_objects:
        if node == depot:
            final.append(-1)
        else:
            index = node.id - 1
            final.append(index)

    return final


def plot_routes(final_routes_var, customer_object_list, route_distance_par=0.0):
    run_end_time = datetime.datetime.now()  # enter the begin time
    path_parent_folder = Path(os.path.dirname(os.getcwd()))
    path_results = path_parent_folder / (
            "exports" + "/" + "Routing_Results" + "/" + "Savings_CVRP" + "_" + run_end_time.strftime(
        "%Y%m%d_%H%M%S.%f"))
    if not path_results.exists():
        os.makedirs(path_results)

    markers = ["-o", "-x", "-^", "-s", "-+", "-distance_matrix_input", "-<", "-*", '-1']
    # markers = ["o", "x", "^", "s", "+", "distance_matrix_input", "<", "*", '1']

    print(customer_object_list)
    for single_route in final_routes_var:
        route_number = final_routes_var.index(single_route)
        print(single_route)

        x_values, y_values = zip(
            *[(float(customer_object_list[i].pos.x), float(customer_object_list[i].pos.y)) for i in
              single_route])

        plt.plot(x_values, y_values, markers[route_number], label=route_number + 1)

        # for showing all customers without clustering
        # plt.plot(x_values, y_values, "o", color='black')
        # plt.plot(final_routes_var[0][0].pos.x, final_routes_var[0][0].pos.y, 'o', color='black', label="Customers",
        #          markersize=8)

        # plt.xlim([17.5, 62.5])  # temp - remove after validation
        # plt.ylim([-2.5, 90])  # temp - remove after validation
        plt.text(x=35, y=81, s=f"Distance: {route_distance_par}")  # temp - remove after validation

    plt.plot(customer_object_list[0].pos.x, customer_object_list[0].pos.y, 's', color='black', label="Depot",
             markersize=9)

    plt.xlabel("x")
    plt.ylabel("y")
    plt.legend(loc='upper left', bbox_to_anchor=(1.01, 1.02))
    plt.savefig(path_results / "savings.pdf", bbox_inches='tight')
    plt.show()


# %%    Receive: This part should receive agent data (customer, depot and vehicle) from AnyLogic Return: It should
# return lists of Customer Class (with depot as Customer(0)) as well as the vehicle capacity (currently only a single
# capacity).
def clarke_wright_savings_function(D):
    N = len(D)
    n = N - 1
    savings = [None] * int((n * n - n) / 2)
    idx = 0
    for i in range(1, N):
        for j in range(i + 1, N):
            s = D[i, 0] + D[0, j] - D[i, j]
            savings[idx] = (s, -D[i, j], i, j)
            idx += 1
    savings.sort(reverse=True)
    return savings


def parallel_savings_init(distance_matrix_input, demand_list, vehicle_capacity, max_allowable_distance=None,
                          savings_callback=clarke_wright_savings_function):
    """
    Implementation of the basic savings algorithm / construction heuristic for
    capaciated vehicle routing problems with symmetric distances (see, e.g.
    Clarke-Wright (1964)). This is the parallel route version, aka. best
    feasible merge version, that builds all of the routes in the solution in
    parallel making always the best possible merge (according to varied savings
    criteria, see below).

    * distance_matrix_input the full 2D distance matrix.
    * demand_list is a list of demands. demand_list[0] should be 0.0 as it is the depot.
    * vehicle_capacity is the capacity constraint limit for the identical vehicles.
    * max_allowable_distance is the optional constraint for the maximum route length/duration/cost.


    See clarke_wright_savings.py, gaskell_savings.py, yellow_savings.py etc.
    to find specific savings variants. They all use this implementation to do
    the basic savings procedure and they differ only by the savings
    calculation. There is also the sequental_savings.py, which builds the
    routes one by one.

    Clarke, G. and Wright, J. (1964). Scheduling of vehicles from a central
     depot to a number of delivery points. Operations Research, 12, 568-81.
    """

    # print("Distance matrix:\n", distance_matrix_input)
    # print("Demands:", demand_list)
    # print("Homogeneous capacity: ", vehicle_capacity)

    N = len(distance_matrix_input)
    ignore_negative_savings = not False

    ## 1. make route for each customer
    routes = [[i] for i in range(1, N)]
    route_demands = demand_list[1:] if vehicle_capacity else [0] * N
    if max_allowable_distance: route_costs = [distance_matrix_input[0, i] + distance_matrix_input[i, 0] for i in range(1, N)]

    try:
        ## 2. compute initial savings
        savings = savings_callback(distance_matrix_input)

        # zero based node indexing!
        endnode_to_route = [0] + list(range(0, N - 1))

        ## 3. merge
        # Get potential merges best savings first (second element is secondary
        #  sorting criterion, and it it ignored)
        for best_saving, _, i, j in savings:
            if __debug__:
                log(DEBUG - 1, "Popped savings s_{%d,%d}=%.2f" % (i, j, best_saving))

            if ignore_negative_savings:
                cw_saving = distance_matrix_input[i, 0] + distance_matrix_input[0, j] - distance_matrix_input[i, j]
                if cw_saving < 0.0:
                    break

            left_route = endnode_to_route[i]
            right_route = endnode_to_route[j]

            # the node is already an internal part of a longer segment
            if ((left_route is None) or
                    (right_route is None) or
                    (left_route == right_route)):
                continue

            if __debug__:
                log(DEBUG - 1, "Route #%d : %s" %
                    (left_route, str(routes[left_route])))
                log(DEBUG - 1, "Route #%d : %s" %
                    (right_route, str(routes[right_route])))

            # check capacity constraint validity
            if vehicle_capacity:
                merged_demand = route_demands[left_route] + route_demands[right_route]
                if merged_demand - C_EPS > vehicle_capacity:
                    if __debug__:
                        log(DEBUG - 1, "Reject merge due to " +
                            "capacity constraint violation")
                    continue
            # if there are route cost constraint, check its validity
            if max_allowable_distance:
                merged_cost = route_costs[left_route] - distance_matrix_input[0, i] + \
                              route_costs[right_route] - distance_matrix_input[0, j] + \
                              distance_matrix_input[i, j]
                if merged_cost - S_EPS > max_allowable_distance:
                    if __debug__:
                        log(DEBUG - 1, "Reject merge due to " +
                            "maximum route length constraint violation")
                    continue

            # update bookkeeping only on the recieving (left) route
            if vehicle_capacity: route_demands[left_route] = merged_demand
            if max_allowable_distance: route_costs[left_route] = merged_cost

            # merging is done based on the joined endpoints, reverse the
            #  merged routes as necessary
            if routes[left_route][0] == i:
                routes[left_route].reverse()
            if routes[right_route][-1] == j:
                routes[right_route].reverse()

            # the nodes that become midroute points cannot be merged
            if len(routes[left_route]) > 1:
                endnode_to_route[routes[left_route][-1]] = None
            if len(routes[right_route]) > 1:
                endnode_to_route[routes[right_route][0]] = None

            # all future references to right_route are to merged route
            endnode_to_route[routes[right_route][-1]] = left_route

            # merge with list concatenation
            routes[left_route].extend(routes[right_route])
            routes[right_route] = None

            if __debug__:
                dbg_sol = routes2sol(routes)
                log(DEBUG - 1, "Merged, resulting solution is %s (%.2f)" %
                    (str(dbg_sol), objf(dbg_sol, distance_matrix_input)))

    except KeyboardInterrupt:  # or SIGINT
        interrupted_sol = routes2sol(routes)
        raise KeyboardInterrupt(interrupted_sol)

    return routes2sol(routes)


def run_vehicle_routing_savings(customerData, vehicleCapacityData, depotData):
    print("Customer data:", customerData)
    # print("Vehicle capacity:", vehicleCapacityData)
    # print("Depot data:", depotData)

    #################
    # INITIALISATION #
    ##################

    no_of_customers = len(customerData)
    vehicle_cap = vehicleCapacityData  # This assumes that all vehicles have the same capacity.

    # create Customer object to represent the depot
    depot = Customer(0)
    depot.set_position(depotData["x"], depotData["y"])
    depot.set_demand(0)
    depot.set_due_time(0)
    depot.set_ready_time(0)
    depot.set_service_time(0)

    Customers = [depot]
    for i in range(0, no_of_customers):
        c = Customer(i + 1)
        c.set_id(int(customerData[i]["id"]))
        c.set_position(customerData[i]["x"], customerData[i]["y"])
        c.set_demand(customerData[i]["demand"])
        Customers.append(c)
    customers_original_order = Customers[:]  # to keep track of the original customer index for later use

    data = {'distance_matrix': create_distance_matrix(Customers), 'demands': [round(i.demand) for i in Customers],
            'num_vehicles': 10}

    data['vehicle_capacities'] = [round(vehicle_cap)] * data['num_vehicles']
    data['depot'] = 0

    list_of_route_dicts_1 = []
    list_of_route_dicts_for_plot = []

    routes2sol = parallel_savings_init(data['distance_matrix'], data['demands'], round(vehicle_cap))

    if routes2sol:
        size = len(routes2sol)
        idx_list = [idx + 1 for idx, val in
                    enumerate(routes2sol) if val == 0]

        routes_list = [routes2sol[i: j] for i, j in
                       zip([0] + idx_list, idx_list +
                           ([size] if idx_list[-1] != size else []))]

        routes_list.pop(0)

        # print("After route split:", routes_list)

        route_number = 0
        route_loads = []

        for r in routes_list:
            r.insert(0, 0)
            # print("Route:", r)

            vehicle_route_distance = 0

            vehicle_route_demand = data['demands'][r[0]]
            for index in range(0, len(r) - 1):
                # print("Index: ", index)
                # print("Current customer:", r[index])


                if r[index + 1]:
                    # print("Next customer: ", r[index + 1])

                    arc_distance = data['distance_matrix'][r[index]][r[index + 1]]
                    # print("Distance: ", arc_distance)
                    vehicle_route_distance += arc_distance
                    vehicle_route_demand += data['demands'][r[index+1]]

            route_loads.append(vehicle_route_demand)

            # print("Current vehicle route distance:", vehicle_route_distance)

            # returns optimised route as original Customer index (for integration with AnyLogic
            # route_index = get_route_as_object_index(current_route_customers, customers_original_order, depot)
            current_route_customers = route_index_to_id(r, Customers[:])

            temp_route = {'route_number': route_number, 'customer_indices': current_route_customers,
                          'route_distance': vehicle_route_distance}

            temp_route_for_plot = {'route_number': route_number, 'customer_indices': r,
                                   'route_distance': vehicle_route_distance}

            list_of_route_dicts_1.append(temp_route)
            list_of_route_dicts_for_plot.append(temp_route_for_plot)


            route_number += 1
    else:
        empty_route = {'route_number': 0, 'customer_indices': [-1, -1], 'route_distance': 0.0}
        list_of_route_dicts_1.append(empty_route)

    final_routes = [d['customer_indices'] for d in list_of_route_dicts_for_plot]

    total_vrp_distance = round(sum(item["route_distance"] for item in list_of_route_dicts_1), 2)

    list_of_route_dicts_json = json.dumps(list_of_route_dicts_1)  # json.dumps is used to make the dictionary
    #
    # # ########
    # # PLOT   #
    # # ########

    # plot_routes(final_routes, Customers, total_vrp_distance)

    print("Final routes: ", list_of_route_dicts_json)
    print(route_loads)

    return list_of_route_dicts_json


# # # %% This part should be replaced by reading data in from AnyLogic. Currently it reads from a json file
##################
# READING IN DATA #
#################
#


def main():
    """main()"""
    with open("test_data/R101_25.json") as inputFile:
        data = json.load(inputFile)

    customer_data_test = data["customers"]  # this will be replaced with the customer data rec
    depot_data_test = data["depot"]
    vehicle_capacity_data_test = data["vehicle_capacity"]

    run_vehicle_routing_savings(customer_data_test, vehicle_capacity_data_test, depot_data_test)

    # print(customer_data_test)
    # print(depot_data_test)
    # print(vehicle_capacity_data_test)

    # parallel_savings_init =


if __name__ == '__main__':
    main()
