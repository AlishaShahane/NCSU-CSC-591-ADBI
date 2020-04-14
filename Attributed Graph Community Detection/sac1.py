# Name: Alisha Shahane
# StudentId: 200311941
# UnityId: asshahan

# Algorithm:
# 1: Every vertex forms its own community.
# 2: Assign communities to vertices such that the gain in modularity is highest.
#    Repeat till there no changes in communitites.
# 3: Combine vertices in a community and repeat 2.


# ---------- Imports ----------
import sys
import pandas as pd
from igraph import *
from scipy import spatial

'''
Function Description: Compute the cosine similarity of all the vertices
'''
def getCosineSimilarity(g):
    mat = [[0 for _ in range(g.vcount())] for _ in range(g.vcount())]

    for i in range(graph.vcount()):
        first = g.vs[i].attributes().values()
        
        for j in range(i, graph.vcount()):
            second = g.vs[j].attributes().values()
            dist = 1.0 / (1.0 + spatial.distance.cosine(first, second))
            mat[i][j] = mat[j][i] = dist

    return mat

'''
Function Description: Compute the modularity which would be a result of adding a vertex to a certain community
'''
def getModularity(graph, sim_mat, communities, vertex, alpha):

    sum_weigths = 0
    for node in set(communities):
        if graph.are_connected(vertex, node):
            eid = graph.get_eid(vertex, node)
            sum_weigths += graph.es["weight"][eid]    
    
    expected_edges = (sum(graph.degree(list(set(communities)))) * graph.degree(vertex)) / (2.0 * graph.ecount())
    Q = sum_weigths - expected_edges
    Q = Q / (2.0 * graph.ecount())
    
    # For attributed graphs
    sum_similarity = 0.0 
    for c in set(communities):
        sum_similarity += sim_mat[c][vertex]

    l = len(set(communities))
    sum_similarity = sum_similarity / l / l
    
    return ((alpha * Q) + ((1 - alpha) * sum_similarity))

'''
Function Description: This function assigns the correct community to all vertices based on modularity
'''
def getChangedCommunity(graph, sim_mat, communities, alpha):
    # We need to check modularity by putting the vertex in all the communities and chose the one with highest modularity
    num_changes = 0

    for v in range(graph.vcount()):

        # Find the original community
        org_com, new_com = [], []
        for c in communities:
            if v in c:
                org_com = c
                break

        max_gain = -1

        # Get the gain by adding the vertex to all other communities
        # Choose the maximum gain and add the vertex to that community.
        for c in communities:
            mod = getModularity(graph, sim_mat, c, v, alpha)

            if mod > 0:
                if mod > max_gain:
                    max_gain = mod
                    new_com = c

        if set(new_com) != set(org_com):
            if max_gain > 0:
                org_com.remove(v)
                new_com.append(v)
                num_changes += 1

                if len(org_com) == 0: communities.remove([])

    return num_changes


'''
Function Description: This function implements the initial pahse of the algorithm
'''
def stepTwo(graph, sim_mat, communities, alpha):
    # Assign vertex to a community which gives the highest positive gain
    changed_comm = getChangedCommunity(graph, sim_mat, communities, alpha)
    iter = 0
    
    # We need to repeat step 2 
    # We will repeat it till changed comminities are more than zero and for a maximum of 15 iterations
    while iter < 15 and changed_comm > 0:
        changed_comm = getChangedCommunity(graph, sim_mat, communities, alpha)
        iter += 1

'''
Function Description: This function combines vertices in a single node and repeats earlier steps
'''
def stepThree(graph, sim_mat, communities, alpha, vertex_community, edges):
    # Community and vertex mapping
    num_coms = 0
    for com in communities:
        for v in com:
            vertex_community[v] = num_coms
        num_coms += 1
    
    # All vertices in a community contracted to a single vertex
    graph.contract_vertices(vertex_community, combine_attrs = "mean")
    graph.simplify(multiple = True, loops = True)
    
    # Assign every vertex its own community
    reduced_communities = [[i] for i in range(num_coms)]
    graph.es['weight'] = [0 for j in range(graph.ecount())]

    # Edge weight is equivalent to number of edges between the nodes within two communities.
    for edge in edges:
        left_com = vertex_community[edge[0]]
        right_com = vertex_community[edge[1]]
        
        if left_com != right_com:
            eid = graph.get_eid(left_com, right_com)
            graph.es['weight'][eid] += 1
        
    # Get the new cosine similarity
    new_sim_mat = getCosineSimilarity(graph)
    
    # Repeat step two
    stepTwo(graph, new_sim_mat, reduced_communities, alpha)


# ---------- Main ----------
# Check input choice of algorithm
if len(sys.argv) != 2:
    print("Aplha value not specified (0.0 or 0.5 or 1)")
    exit(0)

# Create grpah
attr_list = pd.read_csv("./data/fb_caltech_small_attrlist.csv")
graph = Graph.Read_Edgelist("./data/fb_caltech_small_edgelist.txt", directed = False)

graph.es['weight'] = [1] * graph.ecount()

# Assign attributes to each vertex
for i in list(attr_list.columns):
    graph.vs[i] = attr_list[i]

# Get cosine similarity
sim_mat = getCosineSimilarity(graph)

# Set aplha value
alpha, filename = 0,  "0"
if float(sys.argv[1]) == 0.5: 
    alpha = 0.5
    filename = "5"
elif float(sys.argv[1]) == 0.1: 
    aplha = 0.1
    filename = "1"

# Step 1 of SAC algorithm
# Number of communities is equal to number of vertices
communities = [[v] for v in range((graph.vcount()))]
print("Step 1 done.")

# Each vertex is its own community
vertex_community = [0 for v in range(graph.vcount())]

# Step 2 of SAC algorithm
stepTwo(graph, sim_mat, communities, alpha)
print("Step 2 done.")

# Step 3 of SAC algorithm
edges = []
for e in graph.es:
    edges.append([e.source, e.target])
stepThree(graph, sim_mat, communities, alpha, vertex_community, edges)
print("Step 3 done. Writing result in file. ")

with open('./communities_' + filename + '.txt', 'w') as file:
    for com in communities:
        for idx, vertex in enumerate(com):
            if idx != 0:
                file.write(',')
            file.write(str(vertex))
        file.write("\n")

file.close()


