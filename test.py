import main
import pandas as pd
import os
import csv
import numpy as np

if __name__ == "__main__":

    alpha_values = [x * 0.01 for x in range(100, 0, -1)]



    nodes = None
    edges = None
    no_of_paths_per_fg = 4
    begin = True  # always set it to True
    random_graph = False
    custom_graph = False
    custom_graph_type = "(name of the custom graph defined in generate_custom_graph.py)" # Google, Amazon and Microsoft
    # WAN graphs will be referred here
    gml_graph = True
    topology_dataset_path = r'/Users/varya001/PycharmProjects/inter_data_center_routing_july_20/graphs/'
    result_path = r'/Users/varya001/PycharmProjects/inter_data_center_routing_july_20/results'
    reuse_graph_and_demands=False

    availability_slo = [0.9999, 0.9995, 0.999, 0.99]
    latency_slo = [1.5, 2, 2.5, 3]

    experiment_no=0
    for paths_type in ['combination']:
        if experiment_no>0:
           reuse_graph_and_demands=True
        experiment_no=experiment_no+1
        if custom_graph == True:
            alpha_vs_latency_violation = pd.DataFrame(
                columns=['alpha', 'delta_beta', 'latency_violation_mmf', 'latency_violation_improved',
                         'avg_network_utilization_mmf', 'avg_network_utilization_latency_aware', 'network_availability'])
            i = 0
            for alpha in alpha_values:
                latency_violation_mmf, latency_violation_improved, avg_network_utilization_mmf, avg_network_utilization_latency_aware, network_availability, availability_topology_avg, path_edge_matrix, path_latency_dict, demands, bandwidth_allocation_per_path_mmf, bandwidth_allocation_per_path_latency_aware = main.main(
                    nodes, edges, no_of_paths_per_fg, alpha, begin, random_graph, custom_graph, gml_graph,
                    custom_graph_type, None, paths_type, availability_slo, reuse_graph_and_demands)
                print alpha, latency_violation_mmf - latency_violation_improved, latency_violation_mmf, latency_violation_improved, avg_network_utilization_mmf, avg_network_utilization_latency_aware, network_availability, availability_topology_avg
                alpha_vs_latency_violation.loc[i] = [alpha, latency_violation_mmf - latency_violation_improved,
                                                     latency_violation_mmf, latency_violation_improved,
                                                     avg_network_utilization_mmf, avg_network_utilization_latency_aware,
                                                     network_availability]
                i = i + 1
                if availability_topology_avg != None:
                    df = pd.DataFrame(availability_topology_avg)
                    df.to_csv(result_path + "/" + custom_graph_type + '_' + paths_type + '_' + '_availability_topology_avg.csv',
                              index=False)
                begin = False
                np.savetxt(result_path + "/" + custom_graph_type + '_' + paths_type + '_' + '_path_edge_matrix.csv', path_edge_matrix,
                           delimiter=",")  # numpy array  rows - paths (grouped per demand), columns - edges  (grouped bidirectional)
                with open(result_path + "/" + custom_graph_type + '_' + paths_type + '_' + '_path_latency_dict.csv', 'w') as csv_file:
                    writer = csv.writer(csv_file)
                    for key, value in path_latency_dict.items():
                        writer.writerow([key, value])
                # dict keys - paths (grouped per demand), value -latency
                with open(result_path + "/" + custom_graph_type + '_demands.csv', 'w') as f:
                    writer = csv.writer(f, lineterminator='\n')
                    for demand in demands:
                        writer.writerow(demand)

                with open(result_path + "/" + custom_graph_type + '_' + paths_type + '_' + '_bandwidth_allocation_per_path_mmf.csv',
                          'w') as csv_file:
                    writer = csv.writer(csv_file)
                    for key, value in bandwidth_allocation_per_path_mmf.items():
                        writer.writerow([key, value])

                if alpha == 1.0:
                    with open(result_path + "/" + custom_graph_type + '_' + paths_type + '_' + '_bandwidth_allocation_per_path_latency_aware_' + str(
                            int(alpha * 100)) + '.csv', 'w') as csv_file:
                        writer = csv.writer(csv_file)
                        for key, value in bandwidth_allocation_per_path_latency_aware.items():
                            writer.writerow([key, value])

            alpha_vs_latency_violation.to_csv(result_path + "/" + custom_graph_type + '_' + paths_type + '_' + '_alpha_vs_latency_violation.csv',
                                              index=False)


        elif gml_graph == True:
            for gml_graph_file in os.listdir(topology_dataset_path):


                    print gml_graph_file
                    alpha_vs_latency_violation = pd.DataFrame(
                        columns=['alpha', 'delta_beta', 'latency_violation_mmf', 'latency_violation_improved',
                                 'avg_network_utilization_mmf', 'avg_network_utilization_latency_aware',
                                 'network_availability'])
                    i = 0
                    for alpha in alpha_values:
                        latency_violation_mmf, latency_violation_improved, avg_network_utilization_mmf, avg_network_utilization_latency_aware, network_availability, availability_topology_avg, path_edge_matrix, path_latency_dict, demands, bandwidth_allocation_per_path_mmf, bandwidth_allocation_per_path_latency_aware = main.main(
                            nodes, edges, no_of_paths_per_fg,
                            alpha, begin, random_graph, custom_graph,
                            gml_graph, None, gml_graph_file,
                            paths_type, availability_slo, reuse_graph_and_demands)
                        print alpha, latency_violation_mmf - latency_violation_improved, latency_violation_mmf, latency_violation_improved, avg_network_utilization_mmf, avg_network_utilization_latency_aware, network_availability, availability_topology_avg
                        alpha_vs_latency_violation.loc[i] = [alpha, latency_violation_mmf - latency_violation_improved,
                                                             latency_violation_mmf, latency_violation_improved,
                                                             avg_network_utilization_mmf,
                                                             avg_network_utilization_latency_aware, network_availability]
                        i = i + 1
                        if availability_topology_avg != None:
                            df = pd.DataFrame(availability_topology_avg)
                            df.to_csv(
                                result_path + "/" + os.path.splitext(gml_graph_file)[0] + '_' + paths_type + '_' + '_availability_topology_avg.csv',
                                index=False)
                        begin = False
                        np.savetxt(result_path + "/" + os.path.splitext(gml_graph_file)[0] + '_' + paths_type + '_' + '_path_edge_matrix.csv',
                                   path_edge_matrix,
                                   delimiter=",")
                        with open(result_path + "/" + os.path.splitext(gml_graph_file)[0] + '_' + paths_type + '_' + '_path_latency_dict.csv',
                                  'w') as csv_file:
                            writer = csv.writer(csv_file)
                            for key, value in path_latency_dict.items():
                                writer.writerow([key, value])
                        with open(result_path + "/" + os.path.splitext(gml_graph_file)[0] + '_' + paths_type + '_' + '_demands.csv', 'w') as f:
                            writer = csv.writer(f, lineterminator='\n')
                            for demand in demands:
                                writer.writerow(demand)

                        with open(result_path + "/" + os.path.splitext(gml_graph_file)[
                            0] + '_' + paths_type + '_' + '_bandwidth_allocation_per_path_mmf.csv',
                                  'w') as csv_file:
                            writer = csv.writer(csv_file)
                            for key, value in bandwidth_allocation_per_path_mmf.items():
                                writer.writerow([key, value])

                        if alpha == 0.9 or alpha == 1.0:
                            with open(
                                    result_path + "/" + os.path.splitext(gml_graph_file)[
                                        0] + '_' + paths_type + '_' + '_bandwidth_allocation_per_path_latency_aware_' + str(
                                        int(alpha * 100)) + '.csv',
                                    'w') as csv_file:
                                writer = csv.writer(csv_file)
                                for key, value in bandwidth_allocation_per_path_latency_aware.items():
                                    writer.writerow([key, value])
                    alpha_vs_latency_violation.to_csv(
                        result_path + "/" + os.path.splitext(gml_graph_file)[0] + '_' + paths_type + '_' + '_alpha_vs_latency_violation.csv',
                        index=False)
                    begin = True
