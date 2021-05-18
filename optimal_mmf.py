

def create_variables(solver, no_of_demands,k):
    allocation_variables = [[]] * (no_of_demands*k+1)
    allocation_variables[0] = solver.NumVar(0.0, solver.infinity(), 't')
    for i in range(1,no_of_demands*k+1):
        allocation_variables[i]=solver.NumVar(0.0,solver.infinity(),str(i))
    return allocation_variables

def create_objective(solver,t):
    objective= solver.Objective()
    objective.SetCoefficient(t,1)
    objective.SetMaximization()
    return objective

def create_constraints(solver, no_of_demands, no_of_edges, allocation_variables, path_edge_matrix, G, current_demands, blocked_demands_LP_values_dict, demands, k):

    constraints= [0]*(2*(no_of_demands+no_of_edges))
    i=0
    for demand in demands:
        if demand in current_demands:
            constraints[i]=solver.Constraint(-solver.infinity(),0)
            constraints[i].SetCoefficient(allocation_variables[0],1)
            for j in range(0,k):
                constraints[i].SetCoefficient(allocation_variables[i*k+j+1],-1)

        elif demand in blocked_demands_LP_values_dict:
            constraints[i] = solver.Constraint(-solver.infinity(),-blocked_demands_LP_values_dict[demand])
            for j in range(0, k):
                constraints[i].SetCoefficient(allocation_variables[i * k + j + 1], -1)

        constraints[i+no_of_demands] = solver.Constraint(-solver.infinity(), demand[2])
        for j in range(0, k):
            constraints[i+no_of_demands].SetCoefficient(allocation_variables[i * k + j + 1], 1)

        i=i+1

    i=i+no_of_demands
    m=0
    for (u, v) in G.edges():
        constraints[i+m]=solver.Constraint(0,G.edges[u,v]['capacity'])
        for n in range(0,no_of_demands*k):
            constraints[i+m].SetCoefficient(allocation_variables[n+1],path_edge_matrix[n,m])
        m=m+1
        constraints[i+m]=solver.Constraint(0,G.edges[u,v]['capacity'])
        for n in range(0,no_of_demands*k):
            constraints[i+m].SetCoefficient(allocation_variables[n+1],path_edge_matrix[n,m])
        m=m+1

    return(constraints)

