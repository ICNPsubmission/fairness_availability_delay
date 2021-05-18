import matplotlib.pyplot as plt
from networkx import nx
import random
import numpy
import math
from itertools import islice
import edge_disjoint_paths
import itertools
import sys

def generate_graph(no_of_nodes, no_of_edges):
    G = nx.gnm_random_graph(no_of_nodes, no_of_edges)
    for (u, v) in G.edges():
        G.edges[u, v]['latency'] = random.randint(40, 70) # ms
        G.edges[u,v]['capacity']= random.randint(50, 100) # Gbps
        G.edges[u,v]['availability']=random.randint(90,100)/100.0 #fraction

    nx.draw(G, with_labels= True, node_color='y')
    plt.show()

    return G

# demand =( source, destination, bandwidth upper bound, latency SLO)
def generate_demands(no_of_demands, no_of_nodes, k, G):
    demands = []
    while len(demands) <= no_of_demands:
        source = random.randrange(0, no_of_nodes)
        destination = random.randrange(0, no_of_nodes)
        if source != destination: #and ((source, destination) not in demands): # fix it
            shortest_path_length_1 = nx.shortest_path_length(G, source=source, target=destination, weight='latency')

            #tc1
            bandwidth_upper_bound_1_tc1=math.ceil(0.8*k*random.randint(50, 100))
            latency_SLO_1_tc1=math.ceil(1.5 * shortest_path_length_1)
            availability_SLO_1_tc1=0.9999

            #tc2
            bandwidth_upper_bound_1_tc2=math.ceil(0.8*k*random.randint(50, 100))
            latency_SLO_1_tc2=math.ceil(2.0 * shortest_path_length_1)
            availability_SLO_1_tc2=0.9995

            #tc3
            bandwidth_upper_bound_1_tc3=math.ceil(0.8*k*random.randint(50, 100))
            latency_SLO_1_tc3=math.ceil(2.5 * shortest_path_length_1)
            availability_SLO_1_tc3=0.999

            #tc4
            bandwidth_upper_bound_1_tc4=math.ceil(0.8*k*random.randint(50, 100))
            latency_SLO_1_tc4=math.ceil(3.0 * shortest_path_length_1)
            availability_SLO_1_tc4=0.99

            demands.append(
                (source, destination, bandwidth_upper_bound_1_tc1, latency_SLO_1_tc1, availability_SLO_1_tc1))
            demands.append(
                (source, destination, bandwidth_upper_bound_1_tc2, latency_SLO_1_tc2, availability_SLO_1_tc2))
            demands.append(
                (source, destination, bandwidth_upper_bound_1_tc3, latency_SLO_1_tc3, availability_SLO_1_tc3))
            demands.append(
                (source, destination, bandwidth_upper_bound_1_tc4, latency_SLO_1_tc4, availability_SLO_1_tc4))

            shortest_path_length_2 = nx.shortest_path_length(G, source=destination, target=source, weight='latency')

            # tc1
            bandwidth_upper_bound_2_tc1 = math.ceil(0.8 * k * random.randint(50, 100))
            latency_SLO_2_tc1 = math.ceil(1.5 * shortest_path_length_2)
            availability_SLO_2_tc1 = 0.9999

            # tc2
            bandwidth_upper_bound_2_tc2 = math.ceil(0.8 * k * random.randint(50, 100))
            latency_SLO_2_tc2 = math.ceil(2.0 * shortest_path_length_2)
            availability_SLO_2_tc2 = 0.9995

            # tc3
            bandwidth_upper_bound_2_tc3 = math.ceil(0.8 * k * random.randint(50, 100))
            latency_SLO_2_tc3 = math.ceil(2.5 * shortest_path_length_2)
            availability_SLO_2_tc3 = 0.999

            # tc4
            bandwidth_upper_bound_2_tc4 = math.ceil(0.8 * k * random.randint(50, 100))
            latency_SLO_2_tc4 = math.ceil(3.0 * shortest_path_length_2)
            availability_SLO_2_tc4 = 0.99



            demands.append(
                (destination, source, bandwidth_upper_bound_2_tc1, latency_SLO_2_tc1, availability_SLO_2_tc1))
            demands.append(
                (destination, source, bandwidth_upper_bound_2_tc2, latency_SLO_2_tc2, availability_SLO_2_tc2))
            demands.append(
                (destination, source, bandwidth_upper_bound_2_tc3, latency_SLO_2_tc3, availability_SLO_2_tc3))
            demands.append(
                (destination, source, bandwidth_upper_bound_2_tc4, latency_SLO_2_tc4, availability_SLO_2_tc4))
    print demands
    return demands[0:no_of_demands]



def generate_path_edge_matrix(G,demands,no_of_demands,no_of_edges,k, paths_type, availability_slo):
    path_edge_matrix = numpy.zeros((no_of_demands*k, 2*no_of_edges))
    path_latency_dict ={}
    path_count = 0
    sum=0
    availability_topology_avg=[0]*len(availability_slo)
    availability_topology_sum=[0]*len(availability_slo)
    for demand in demands:
        path_list, path_list_reliability, path_set_characteristics=path_generator(G, demand[0], demand[1], k, paths_type, demand[4])
        sum=sum+path_list_reliability

        for path in path_list:
            pairwise_path = nx.utils.pairwise(path)
            edge_count = 0
            for edge in G.edges:
                if edge in pairwise_path:
                    path_edge_matrix[path_count][edge_count] = 1
                else:
                    path_edge_matrix[path_count][edge_count] = 0
                edge_count = edge_count + 1
                if edge[::-1] in pairwise_path:
                    path_edge_matrix[path_count][edge_count] = 1
                else:
                    path_edge_matrix[path_count][edge_count] = 0
                edge_count = edge_count + 1



            path_count = path_count + 1

            path_latency = G.subgraph(path).size(weight='latency')
            path_latency_dict[path_count] = path_latency



        for i in range(0,len(availability_slo)):
            for path_set in path_set_characteristics:
                if path_set_characteristics[path_set] >= availability_slo[i]:
                    availability_topology_sum[i]=availability_topology_sum[i]+1

    for j in range(0,len(availability_topology_sum)):
        availability_topology_avg[j]=availability_topology_sum[j]/len(demands)


    network_availability=float(sum)/len(demands)
    return path_edge_matrix, path_latency_dict, network_availability, availability_topology_avg


def path_generator(G,source, destination, k,type,path_set_reliability_threshold):
    path_set_final = None
    path_set_final_latency_sum = sys.maxint
    path_set_final_reliability = 0
    path_set_characteristics = {}

    if type == "shortest_path":
        path_set_final = list(islice(nx.shortest_simple_paths(G, source, destination, weight='latency'), k))
    elif type == "shortest_edge_disjoint_paths":
        path_set_final =  edge_disjoint_paths.compute_edge_disjoint_paths(G,source,destination,k)
    elif type == "combination":
        shortest_paths_list=list(islice(nx.shortest_simple_paths(G, source, destination, weight='latency'), 2*k))
        #print shortest_paths_list
        shortest_edge_disjoint_paths_list = edge_disjoint_paths.compute_edge_disjoint_paths(G,source,destination,2*k)
        #print shortest_edge_disjoint_paths_list,"\n"`
        #for path in path_list:
        shortest_paths_tuples=[tuple(path) for path in shortest_paths_list]
        shortest_edge_disjoint_paths_tuples=[tuple(path) for path in shortest_edge_disjoint_paths_list]
        final_list=set(shortest_paths_tuples+shortest_edge_disjoint_paths_tuples)
        #print final_list

        for path_set in itertools.combinations(final_list, k):
            path_set_reliability=path_set_reliability_calculator(G, path_set)
            latency_sum = 0
            for path in path_set:
                for i in range(len(path) - 1):
                    latency_sum = latency_sum + G.get_edge_data(path[i], path[i + 1])['latency']
            path_set_characteristics[path_set] = path_set_reliability_calculator(G, path_set)
            if path_set_reliability>path_set_reliability_threshold:
                if latency_sum < path_set_final_latency_sum:
                    path_set_final=path_set
                    path_set_final_latency_sum=latency_sum
                    path_set_final_reliability=path_set_reliability
        if path_set_final==None:
            path_set_final=max(path_set_characteristics, key=path_set_characteristics.get)
            path_set_final_reliability=path_set_characteristics[path_set_final]

        #print path_set_final,path_set_final_reliability,path_set_final_latency_sum
                    #print path_set_final,path_set_final_latency_sum

    return path_set_final, path_set_final_reliability, path_set_characteristics

def path_set_reliability_calculator(G,path_set):
    #print path_set

    path_set_reliability=0
    for j in range(1,len(path_set)+1):
        for path_subset in itertools.combinations(path_set, j):
            edge_dict = {}
            for path in path_subset:
                for i in range(len(path)-1):
                    edge_dict[(path[i],path[i+1])]=G.get_edge_data(path[i],path[i+1])['availability']
            path_subset_reliability = numpy.prod(edge_dict.values())
            #print path_subset,(((-1)**(j+1))*path_subset_reliability)
            path_set_reliability=path_set_reliability+(((-1)**(j+1))*path_subset_reliability)
            #print path_set_reliability

    return path_set_reliability