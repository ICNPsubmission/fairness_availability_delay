from __future__ import print_function

from networkx import convert_node_labels_to_integers
from ortools.linear_solver import pywraplp
import utils_and_generate_random_graph
import optimal_mmf
import latency_aware_bandwidth_allocation
import generate_custom_graph
import read_gml_networks


G=None
demands=None
path_edge_matrix=None
path_latency_dict=None
no_of_demands=None
result_path = r'(path to results folder)'


def main(no_of_nodes,no_of_edges,k,alpha, begin, random_graph, custom_graph, gml_graph, custom_graph_type, gml_graph_file, paths_type, availabilty_slo, reuse_graph_and_demands):
    blocked_demands_LP_values_dict={}
    iteration = 0
    global G
    global demands
    global path_edge_matrix
    global path_latency_dict
    global no_of_demands
    network_availability=None
    availability_topology_avg=None

    if begin == True:
        if reuse_graph_and_demands == False:
            if random_graph == True:
                G=utils_and_generate_random_graph.generate_graph(no_of_nodes, no_of_edges)
                no_of_demands = no_of_nodes
                demands=utils_and_generate_random_graph.generate_demands(no_of_demands, no_of_nodes, k, G)

            elif custom_graph == True:
                G=generate_custom_graph.generate_graph(custom_graph_type)
                no_of_nodes = len(G)
                no_of_demands = no_of_nodes*2
                demands = utils_and_generate_random_graph.generate_demands(no_of_demands, no_of_nodes, k, G)

            elif gml_graph == True:
                G=read_gml_networks.generate_graph(gml_graph_file)
                G=convert_node_labels_to_integers(G)
                no_of_nodes=len(G)
                no_of_demands=no_of_nodes*2
                demands = utils_and_generate_random_graph.generate_demands(no_of_demands, no_of_nodes, k, G)

        no_of_edges=G.number_of_edges()
        path_edge_matrix, path_latency_dict, network_availability, availability_topology_avg = utils_and_generate_random_graph.generate_path_edge_matrix(G, demands, no_of_demands,
                                                                                                                                                         no_of_edges, k, paths_type, availabilty_slo)
        print(demands)



    no_of_edges = G.number_of_edges()
    current_demands=list(demands)
    prev_solution_value = None
    while current_demands:
        blocking=False

        # Instantiate a Glop solver
        solver = pywraplp.Solver('SolveMaxMin', pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
        allocation_variables = optimal_mmf.create_variables(solver, no_of_demands, k)
        objective = optimal_mmf.create_objective(solver, allocation_variables[0])
        constraints=optimal_mmf.create_constraints(solver, no_of_demands, no_of_edges, allocation_variables, path_edge_matrix, G, current_demands, blocked_demands_LP_values_dict, demands, k)
        status = solver.Solve()
        if status == solver.OPTIMAL:

            for demand in current_demands:
                i=demands.index(demand)
                #print(constraints[i].dual_value())
                if constraints[i].dual_value()>0: # blocking demand
                    blocking=True
                    blocked_demands_LP_values_dict[demand]=allocation_variables[0].solution_value()
            iteration=iteration+1
            current_demands = [item for item in current_demands if item not in blocked_demands_LP_values_dict]

            #print(current_demands)
            if blocking == False and prev_solution_value == allocation_variables[0].solution_value():
                break
            prev_solution_value=allocation_variables[0].solution_value()
            #print(allocation_variables[0].solution_value())
        else:
            break

    #print("blocked_demands_LP_values_dict" + str(blocked_demands_LP_values_dict))
    #print("current demands" + str(current_demands))

    bandwidth_allocation_per_flowgroup_mmf={}
    bandwidth_allocation_per_path_mmf={}

    sum=0
    latency_violation_mmf=0
    for i in range(1, no_of_demands * k + 1):
        bandwidth_allocation_per_path_mmf[i]=allocation_variables[i].solution_value()
        sum=sum+bandwidth_allocation_per_path_mmf[i]
        if(i%k==0):
            bandwidth_allocation_per_flowgroup_mmf[i/k]=sum
            sum=0
        #print(i)
        latency_violation_mmf = latency_violation_mmf + allocation_variables[i].solution_value() * max((
                    path_latency_dict[i] - demands[(i-1) / k][3]),0) / demands[(i-1) / k][2]

    #print("latency violation mmf (beta)=" + str(latency_violation_mmf))
    #print("demands"+ str(demands))
    #print("path latency =>" + str(path_latency_dict))
    print("bandwidth allocated per path for max-min fair algorithm"+ str(bandwidth_allocation_per_path_mmf))
    print("bandwidth allocated per flowgroup for max-min fair algorithm"+ str(bandwidth_allocation_per_flowgroup_mmf))


    #link_utilization mmf
    link_utilization={}
    capacity={}
    count_directed_edges=0
    for (u, v) in G.edges():
        capacity_edge=G.edges[u, v]['capacity']
        #forward_edge
        for directed_edge in [0,1]:
            link_utilization_sum=0
            path_index=1
            for i in path_edge_matrix[:,count_directed_edges]:
                if i == 1:
                    link_utilization_sum=link_utilization_sum+allocation_variables[path_index].solution_value()
                path_index=path_index+1
            link_utilization[count_directed_edges]=link_utilization_sum
            capacity[count_directed_edges]=capacity_edge
            count_directed_edges = count_directed_edges + 1

    sum_network_utilization_mmf=0
    for edge in link_utilization:
        sum_network_utilization_mmf=sum_network_utilization_mmf+(link_utilization[edge]/capacity[edge])

    avg_network_utilization_mmf=sum_network_utilization_mmf/(G.number_of_edges()*2)



    # Instantiate a Glop solver
    solver = pywraplp.Solver('Solve_latency_aware_bandwidth_allocation', pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
    allocation_variables_latency_aware = latency_aware_bandwidth_allocation.create_variables(solver, no_of_demands, k)
    objective_latency_aware = latency_aware_bandwidth_allocation.create_objective(solver,allocation_variables_latency_aware,no_of_demands,k, demands, path_latency_dict)
    constraints_latency_aware = latency_aware_bandwidth_allocation.create_constraints(solver, no_of_demands, no_of_edges, allocation_variables_latency_aware, path_edge_matrix, G, demands, k, bandwidth_allocation_per_flowgroup_mmf, alpha)
    status = solver.Solve()
    latency_violation_improved = 0
    if status == solver.OPTIMAL:

        bandwidth_allocation_per_path_latency_aware={}
        for i in range(0, no_of_demands * k):
            bandwidth_allocation_per_path_latency_aware[i+1]=allocation_variables_latency_aware[i].solution_value()
            #if (i % k == 0):
            #    print('-----')
            #print(allocation_variables_latency_aware[i].solution_value())

            latency_violation_improved=latency_violation_improved + allocation_variables_latency_aware[i].solution_value()*max((path_latency_dict[i + 1] - demands[i / k][3]),0) / demands[i / k][2]
        #print("latency violation (beta)="+str(latency_violation_improved))
        print("bandwidth allocated per path for latency aware algorithm",str(bandwidth_allocation_per_path_latency_aware))

    #link_utilization latency aware
    link_utilization={}
    capacity={}
    count_directed_edges=0
    for (u, v) in G.edges():
        capacity_edge=G.edges[u, v]['capacity']
        #forward_edge
        for directed_edge in [0,1]:
            link_utilization_sum=0
            path_index=0
            for i in path_edge_matrix[:,count_directed_edges]:
                if i == 1:
                    link_utilization_sum=link_utilization_sum+allocation_variables_latency_aware[path_index].solution_value()
                path_index=path_index+1
            link_utilization[count_directed_edges]=link_utilization_sum
            capacity[count_directed_edges]=capacity_edge
            count_directed_edges = count_directed_edges + 1

    sum_network_utilization_latency_aware=0
    for edge in link_utilization:
        sum_network_utilization_latency_aware=sum_network_utilization_latency_aware+(link_utilization[edge]/capacity[edge])

    avg_network_utilization_latency_aware=sum_network_utilization_latency_aware/(G.number_of_edges()*2)

    return latency_violation_mmf, latency_violation_improved,avg_network_utilization_mmf, avg_network_utilization_latency_aware, network_availability, availability_topology_avg, path_edge_matrix, path_latency_dict, demands, bandwidth_allocation_per_path_mmf, bandwidth_allocation_per_path_latency_aware

