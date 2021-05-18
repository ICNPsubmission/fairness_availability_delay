def create_variables(solver, no_of_demands,k):
    allocation_variables = [[]] * (no_of_demands*k)
    for i in range(0,no_of_demands*k):
        allocation_variables[i]=solver.NumVar(0.0,solver.infinity(),str(i))
    return allocation_variables

def create_objective(solver,allocation_variables,no_of_demands,k, demands, path_latency_dict):
    objective= solver.Objective()
    for i in range(0,no_of_demands*k):
        objective.SetCoefficient(allocation_variables[i],max((path_latency_dict[i+1]-demands[i/k][3]),0)/demands[i/k][2])
        #objective.SetCoefficient(allocation_variables[i],(-(max(( demands[i / k][3]-path_latency_dict[i + 1] ), 0)))/ demands[i / k][2])
    objective.SetMinimization()
    return objective

def create_constraints(solver, no_of_demands, no_of_edges, allocation_variables, path_edge_matrix, G, demands, k, bandwidth_allocation_per_flowgroup_mmf, alpha):

    constraints= [0]*(2*(no_of_demands+no_of_edges))
    i=0
    for demand in demands:
        constraints[i] = solver.Constraint(alpha*bandwidth_allocation_per_flowgroup_mmf[i+1], solver.infinity())
        for j in range(0, k):
            constraints[i].SetCoefficient(allocation_variables[i * k + j], 1)

        constraints[i+no_of_demands] = solver.Constraint(-solver.infinity(), demand[2])
        for j in range(0, k):
            constraints[i+no_of_demands].SetCoefficient(allocation_variables[i * k + j], 1)

        i=i+1

    i=i+no_of_demands
    m=0
    for (u, v) in G.edges():
        constraints[i+m]=solver.Constraint(0,G.edges[u,v]['capacity'])
        for n in range(0,no_of_demands*k):
            constraints[i+m].SetCoefficient(allocation_variables[n],path_edge_matrix[n,m])
        m=m+1
        constraints[i+m]=solver.Constraint(0,G.edges[u,v]['capacity'])
        for n in range(0,no_of_demands*k):
            constraints[i+m].SetCoefficient(allocation_variables[n],path_edge_matrix[n,m])
        m=m+1

    return(constraints)

