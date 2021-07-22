import json
import operator
from math import degrees, atan2, sqrt
import random
import ortools
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2
import pandas as pd
from scipy.spatial import distance_matrix
import numpy as np
import datetime
from pathlib import Path

import os
from zmq.utils.constant_names import no_prefix

import matplotlib as mpl
import matplotlib.font_manager as font_manager

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
    matrix = pd.DataFrame(distance_matrix(matrix_double, matrix_double))

    # print(matrix)
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


def calculate_depot_angle(x, y, depot_x, depot_y):
    """"""
    angle = degrees(atan2(y - depot_y, x - depot_x))
    bearing = (90 - angle) % 360
    return bearing


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


def get_demand_route(route):
    route_demand = 0
    for c in route:
        route_demand += c.demand
    return route_demand


def get_distance_route(route):
    route_distance = 0
    for i in range(len(route) - 1):
        route_distance += get_distance(route[i], route[i + 1])
    return route_distance


def print_route(route):
    print_tuple(route)
    print('Route demand = ', get_demand_route(route))
    distance = get_distance_route(route)
    print('Route distance = ', distance, '\n')
    return distance


def print_solution(final_routes):
    distance = 0
    for r in final_routes:
        # print_route(r)
        distance += print_route(r)
    print("\nTotal distance = ", distance)


def travelling_salesman_problem(distanceMatrix):
    """This function requires that the depot is element 0 of the route"""
    # Create routing model
    route_list = []

    # print(distanceMatrix)

    size = len(distanceMatrix)

    if size > 0:
        # RoutingIndexManager arguments include the size of the TSP, the number of vehicles and the index of the depot
        manager = pywrapcp.RoutingIndexManager(size, 1, 0)
        #        print("manager: ", manager)
        routing = pywrapcp.RoutingModel(manager)

        #        print("routing: ", routing)

        def distance_callback(from_index, to_index):
            """Returns the distance between the two nodes."""
            # Convert from routing variable Index to distance matrix NodeIndex.
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return distanceMatrix[from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        # print('Transit callback index: ', transit_callback_index)

        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        # print('Routing arc distance:', routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index))

        # Setting first solution heuristic (cheapest addition).
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.SAVINGS
        # PATH_CHEAPEST_ARC, CHRISTOFIDES, SAVINGS
        # print('route node: ', route_node)

        # Forbid node connections (randomly).
        rand = random.Random()
        rand.seed(0)

        def print_solution_tsp(manager, routing, solution):
            """Prints solution on console."""
            print('Objective: {} miles'.format(solution.ObjectiveValue()))
            index = routing.Start(0)
            plan_output = 'Route for vehicle 0:\n'
            route_distance = 0
            while not routing.IsEnd(index):
                plan_output += ' {} ->'.format(manager.IndexToNode(index))
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
            plan_output += ' {}\n'.format(manager.IndexToNode(index))
            print(plan_output)
            plan_output += 'Route distance: {}miles\n'.format(route_distance)

        assignment = routing.SolveWithParameters(search_parameters)

        if assignment:
            # Solution distance.
            # print(assignment.ObjectiveValue())
            # Inspect solution.
            # Only one route here; otherwise iterate from 0 to routing.vehicles() - 1

            route_number = 0
            node = routing.Start(route_number)
            route = ''
            while not routing.IsEnd(node):
                route += str(node) + ' -> '
                route_list.append(node)
                node = assignment.Value(routing.NextVar(node))
            route += '0'
            route_list.append(0)

            # route_distance = assignment.ObjectiveValue()
            #########################################################
            # This part changes the objective from INT to float
            # If we are happy with int and want it faster,
            # comment this part out. Uncomment line above
            ##########################################################
            route_distance = 0
            for node in range(0, len(route_list) - 1):
                # print(route_list[node], route_list[node + 1])
                # print(distanceMatrix[route_list[node]][route_list[node + 1]])
                route_distance += round(distanceMatrix[route_list[node]][route_list[node + 1]], 4)

            # print("Manual route distance = ", route_distance)
            # print_solution_tsp(manager, routing, assignment)

        else:
            print('No solution found.')
            return -1

        tsp_return = {"route": route_list, "distance": route_distance}

    # return route_list
    return tsp_return


def plot_routes(final_routes_var, route_distance_par=0.0):
    run_end_time = datetime.datetime.now()  # enter the begin time
    path_parent_folder = Path(os.path.dirname(os.getcwd()))
    path_results = path_parent_folder / (
            "exports" + "/" + "Routing_Results" + "/" + "CVRP" + "_" + run_end_time.strftime("%Y%m%d_%H%M%S.%f"))
    if not path_results.exists():
        os.makedirs(path_results)

    markers = ["-o", "-x", "-^", "-s", "-+", "-D", "-<", "-*", '-1']
    # markers = ["o", "x", "^", "s", "+", "D", "<", "*", '1']

    for single_route in final_routes_var:
        route_number = final_routes_var.index(single_route)
        x_values, y_values = zip(*[(float(i.pos.x), float(i.pos.y)) for i in single_route])
        plt.plot(x_values, y_values, markers[route_number], label=route_number + 1)

        # for showing all customers without clustering
        # plt.plot(x_values, y_values, "o", color='black')
        # plt.plot(final_routes_var[0][0].pos.x, final_routes_var[0][0].pos.y, 'o', color='black', label="Customers",
        #          markersize=8)


        # plt.xlim([17.5, 62.5])  # temp - remove after validation
        # plt.ylim([-2.5, 90])  # temp - remove after validation
        # plt.text(x=35, y=81, s=f"Distance: {route_distance_par}")  # temp - remove after validation

    plt.plot(final_routes_var[0][0].pos.x, final_routes_var[0][0].pos.y, 's', color='black', label="Depot",
             markersize=9)


    plt.xlabel("x")
    plt.ylabel("y")
    plt.legend(loc='upper left', bbox_to_anchor=(1.01, 1.02))
    plt.savefig(path_results / "sweep.pdf", bbox_inches='tight')
    plt.show()


# %%    Receive: This part should receive agent data (customer, depot and vehicle) from AnyLogic Return: It should
# return lists of Customer Class (with depot as Customer(0)) as well as the vehicle capacity (currently only a single
# capacity).


def run_vehicle_routing_sweep(customerData, vehicleCapacityData, depotData):
    # print("Customer data:", customerData)
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
    depot.set_angle_with_depot(0)

    Customers = []
    for i in range(0, no_of_customers):
        c = Customer(i + 1)
        c.set_id(int(customerData[i]["id"]))
        c.set_position(customerData[i]["x"], customerData[i]["y"])
        c.set_demand(customerData[i]["demand"])

        angle = calculate_depot_angle(c.pos.x, c.pos.y, depot.pos.x, depot.pos.y)
        c.set_angle_with_depot(angle)
        # Print customers out for validation
        # print(i+1, c, c.angleWithDepot)
        Customers.append(c)

    customers_original_order = Customers[:]  # to keep track of the original customer index for later use

    # %%
    #########################
    # CLUSTER-FIRST (SWEEP) #
    #########################

    #       Receive: Customers as a list. Vehicle capacity as a single value
    #       Returns: The routes after clustering in order of the angle. (A list of lists of Customers objects).

    Customers.sort(key=lambda x: x.angleWithDepot, reverse=False)

    # print("Customers sorted by angle: ")
    # for c in Customers:
    #     print(c, c.angleWithDepot)

    clusters = []  # this represents the list of routes. It is a list of lists of Customers.
    final_routes = []
    final_routes_index = []
    temp_cluster = []  # this represents a route. It is a list of Customers
    cap = 0  # variable to keep track of how much has been loaded into vehicle
    temp_customers = copy(Customers)

    while len(temp_customers):  # While there are still customers to assign to a route
        curr_customer = temp_customers.pop(0)  # Isolate and remove the first customer (smallest angle) from list
        # Print current customer for verification
        # print("Current customer: ", curr_customer)
        if cap + curr_customer.demand <= vehicle_cap:  # If the capacity of the current vehicle will not be exceeded
            temp_cluster.append(curr_customer)  # Add the current customer to the route in question
            cap += curr_customer.demand  # Add current customer demand to the current vehicle

        else:  # Once the route is full
            temp_cluster.append(depot)
            temp_cluster.insert(0, depot)
            clusters.append(temp_cluster)  # Add the current route to the list of routes
            temp_cluster = []  # Clear the current route (to make new one)
            cap = 0  # "Empty the vehicle
            temp_cluster.append(curr_customer)  # Add the current customer to the route in question
            cap += curr_customer.demand  # Add current customer demand to the current vehicle

    # print get_distance(DEPOT,Customers[0])
    temp_cluster.insert(0, depot)
    temp_cluster.append(depot)

    clusters.append(temp_cluster)  # Add the last route to the list of routes

    # print_solution(clusters)
    # plot_routes(clusters)
    # plt.show()

    # %%
    ######################
    # Route-Second (TSP) #
    ######################
    list_of_route_dicts = []

    for c in clusters:  # Do this for all routes

        temp_dict = {"route_number": clusters.index(c)}

        c.pop()  # remove extra depot at end of list
        # c.insert(0, depot)  # Insert the depot as the starting point of the route
        # print('Initial route: ')
        # print_route(c)

        # plot_single_route(c)                  # Plot initial solution (before TSP optimisation)

        # Run TSP to find a more efficient route
        # Returns the local order of route. i.e. [0, 1, 3, 2, 0].
        current_route_distance_matrix = create_distance_matrix(c)
        current_tsp_output = travelling_salesman_problem(current_route_distance_matrix)

        current_route_order = current_tsp_output['route']
        current_route_distance = current_tsp_output['distance']

        # Translate from TSP() solution [local order], to a list of customer objects
        current_route_customers = get_route_as_objects(current_route_order, c)

        # returns optimised route as original Customer index (for integration with AnyLogic
        route_index = get_route_as_object_index(current_route_customers, customers_original_order, depot)
        # plot_single_route(current_route_customers)  # Plot final sub-solution (after TSP optimisation)
        # plt.show()

        # Add the optimised route (current_route_customers) to the list of routes to form the entire solution
        final_routes.append(current_route_customers)
        # Add the optimised route (as indices) to the list of routes to form the entire solution
        final_routes_index.append(route_index)

        temp_dict["customer_indices"] = route_index  # add the route order to the dict
        temp_dict["route_distance"] = current_route_distance  # add the route distance to the dict
        list_of_route_dicts.append(temp_dict)  # add the new route (dict) to the list of routes
        list_of_route_dicts_json = json.dumps(list_of_route_dicts)  # json.dumps is used to make the dictionary
        # use double quotes. This is required for AnyLogic

    total_vrp_distance = round(sum(item["route_distance"] for item in list_of_route_dicts), 2)
    # print_solution(final_routes)  # print the list of arrays version
    print(list_of_route_dicts)  # print the list of dictionaries

    ########
    # PLOT #
    ########

    # plot_routes(final_routes, total_vrp_distance)

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

    run_vehicle_routing_sweep(customer_data_test, vehicle_capacity_data_test, depot_data_test)


if __name__ == '__main__':
    main()
