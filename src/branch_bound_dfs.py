import time
import random
import concurrent.futures
import threading
import matplotlib.pyplot as plt
import os, datetime
class UnionFind:
    def __init__(self, size):
        self.parent = list(range(size)) #keeps track of parent of each vertex in the disjoint-set
        self.rank = [0]*size #rank = depth of each vertex's tree

    #finds the parent of the vertex
    #path compression
    def find(self, x): 
        if self.parent[x] != x: #it is not it's own parent? (not root?)
            self.parent[x] = self.find(self.parent[x]) #reassign node's parent to root node --> path compression
        return self.parent[x]

    def union(self, x, y): #combines the sets; x, y are the vertices that are being combined
        root_x, root_y = self.find(x), self.find(y)
        
        if root_x != root_y: #they are not part of the same group
            #attach smaller rank tree under root of higher rank tree
            if self.rank[root_x] < self.rank[root_y]:
                self.parent[root_x] = root_y
            elif self.rank[root_y] < self.rank[root_x]:
                self.parent[root_y] = root_x
            else: #ranks are equal, choose one as parent and increase it's rank
                self.parent[root_x] = root_y
                self.rank[root_y] +=1

class TSPSolver:
    def __init__(self, graph, intermediate_file):
        self.graph = graph
        self.heuristic_cache = {}
        self.upperbound = float('inf')
        self.shared_value_lock = threading.Lock()
        self.intermediate_file = intermediate_file

    
    def update_function(self, upper_initial):
        with self.shared_value_lock:
            if self.upperbound > upper_initial:
                self.upperbound = upper_initial 

    def branch_and_bound_dfs(self, graph, initial_start, start_time):
        start_node = random.randint(0,len(graph)-1)
        visited = [start_node]
        domain = self.order_domain_values(start_node, visited.copy()) 
        stack = list()
        count = 0
        stack.append([start_node, domain])
        best_assignment = initial_start
        upper_initial = self.functionf(initial_start)
        self.update_function(upper_initial)

        while stack:
            var, domain = stack[-1]
            if not domain:
                visited.remove(var)
                stack.pop()
            else:
                value = domain.pop()
                visited.append(value)

                get = self.functionf(visited)
                if get >= self.upperbound: # f(p) = h(n) + g(n)
                    visited.pop()
                    continue

                if len(visited) == len(graph):
                    temp = visited.copy()
                    temp.append(visited[0])
                    funcf = self.functionf(temp)
                    if funcf < self.upperbound: 
                        self.update_function(funcf)
                        best_assignment = temp.copy()
                        count += 1
                        self.intermediate_file.seek(0)
                        self.intermediate_file.write(f"{count} | {time.time() - start_time:.4f}| {self.upperbound:.4f} | {best_assignment} \n")
                    visited.pop()
                    
                else:
                    var_next = value
                    domain_next = self.order_domain_values(var_next, visited)
                    stack.append([var_next, domain_next])
        return best_assignment

    def functionf(self, visited):
        key = tuple(visited)
        if key in self.heuristic_cache:
            return self.heuristic_cache[key]
        g_n = 0 

        for num in range(len(visited)-1):
            g_n += graph[visited[num]][visited[num+1]]
        
        unvisited = list(set([i for i in range(len(graph))] ) - set(visited))
        unvisited.append(visited[-1])
        unvisited.append(visited[0])
    
        length = len(unvisited) 
        # initialize new_graph
        # with vertices list make new graph
        vertex_edge_list = [] #row (city1), column (city2), edge length (distance between cities)
        if len(visited) < len(graph)-1: #len = 2 means there is 1 unvisted left
            for row in range(length-1): 
                for col in range(row+1, length):
                    vertex_edge_list.append([row, col, graph[unvisited[row]][unvisited[col]]])
        
            mst_sum = self.kruskal_mst(vertex_edge_list)
            h_n = mst_sum
        
        elif len(visited) == len(graph)-1:
            h_n = graph[visited[-1]][unvisited[0]]
        else: 
            h_n = 0
        result = g_n + h_n
        self.heuristic_cache[key] = result
        return result


    def kruskal_mst(self, vertex_edge_list): # graph = unvisited only
        mst= [] #list of edges
        sorted_ve_list = sorted(vertex_edge_list, key = lambda x: x[2]) # sort by shortest edge distance

        UF = UnionFind(len(graph))
        for i in sorted_ve_list:
            root1 = UF.find(i[0])
            root2 = UF.find(i[1])

            if root1 != root2:
                mst.append(i)
                UF.union(root1, root2)
            
        mst_sum = sum(sublist[-1] for sublist in mst) #length of edges in mst
        return mst_sum

    def order_domain_values(self, node, visited):
        # ordering the child nodes
        # return child that hasn't been visited
        children = list(set(range(len(graph))) - set(visited))
        sorted_children = sorted(children, key=lambda x: graph[node][x])

        return sorted_children

    def nearest_neighbor(self, graph):
        current_city = 0  # Starting from city 0
        tour = [current_city]
        total_cost = 0.0
        unvisited = [i for i in range(1,len(graph))]

        while unvisited:
            nearest_city = min(unvisited, key=lambda city: graph[current_city][city])
            tour.append(nearest_city)
            total_cost += graph[current_city][nearest_city]
            current_city = nearest_city
            unvisited.remove(nearest_city)

        
        # Return to the starting city to complete the tour
        tour.append(tour[0])
        total_cost += graph[current_city][tour[0]]

        return tour

    def start_tour(self, initial_start):
        start_point = list()
        if len(graph) < 21:
            start_time = time.time()
            result_tour = self.branch_and_bound_dfs(graph, initial_start, start_time)
            cost = self.functionf(result_tour)
            print("Minimum Cost:", result_tour, cost)
            total_time = time.time() - start_time
            print("--- %s seconds ---" % (total_time))

            return total_time, result_tour 
        else:
            thread_num = 2
            start_point.append(initial_start)
            nearest_sample = self.nearest_neighbor(graph)
            start_point.append(nearest_sample)

            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(self.branch_and_bound_dfs, graph, start_point[i], time.time()) for i in range(thread_num)]

                # Wait for all tasks to finish
                concurrent.futures.wait(futures)

                for future in futures:
                    result = future.result()
                    cost = self.functionf(result)
                    print("Minimum Cost:", result, cost)



if __name__ == "__main__":
    # Get the current working directory
    current_directory = os.getcwd()
    print("Current Working Directory:", current_directory)

    # Set the working directory to the directory containing the script
    script_directory = os.path.dirname(os.path.realpath(__file__))
    os.chdir(script_directory)

    data_file_path = "../data/"
    data_file_name = "10_0.0_10.0.out"
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y%m%d_%H%M%S")
    result_file_path = f"../output/bnbdfs/{formatted_datetime}/"
    if not os.path.exists(result_file_path):
        os.makedirs(result_file_path)

    data = open(data_file_path + data_file_name, "r")
    lines = data.readlines()
    data.close()

    graph = []
    for line in lines[1:]:
        result = [float(x.strip()) for x in line.split(' ')]
        graph.append(result)

    keep = list()
    keep2 = list()
    f3 = open(f"{result_file_path}total_result_for_{len(graph)}.txt", "a+")
    f3.truncate(0) 

    f3.write(f"count | total_time | initial_cost |  initial_tour \n") 
    for i in range(10):
        random_sample = random.sample(range(0, len(graph)), len(graph))
        random_sample.append(random_sample[0])
        inter = open(f"{result_file_path}intermediate_result_{len(graph)}_{i}.txt", "a+")
        inter.truncate(0)
        tsp_solver = TSPSolver(graph, inter)
         
        total_time, new_tour = tsp_solver.start_tour(random_sample)
        initial_cost = tsp_solver.functionf(random_sample)
        new_cost = tsp_solver.functionf(new_tour)
        keep.append(total_time)
        keep2.append(initial_cost - new_cost)
        f3.seek(0)
        f3.write(f"{i} | {total_time:.4f} |{initial_cost:.4f} | {random_sample} \n") 
        inter.close()
     
    f3.write("=============================================== \n") 
    f3.write(f"final result cost: {new_cost:.4f} | optimal tour {new_tour} \n") 
    f3.close() 

    # plt.hist(keep, bins=20, color='skyblue', edgecolor='black')
    # plt.xlabel('Time Values')
    # plt.ylabel('Count')
    # plt.title('Count of Runtime for 10 Nodes(Var = 10)')
    # plt.grid(axis='y')
    # plt.show()