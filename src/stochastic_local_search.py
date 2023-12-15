import concurrent.futures
import random
import time
import os, datetime

class TSPSolver:
    def __init__(self, graph, intermediate_file):
        self.graph = graph
        self.random_sample = self.nearest_neighbor()
        self.f2 = intermediate_file

    # tour = {(0,1):True, (1,2):True, (2,3):True, (3,4):True, (4,0):False}
    def check_tour(self, tour):
        dic = {}
        for i in range(len(self.graph)):
            dic[i] = 0
        for pair in tour.keys():
            if tour[pair]:
                dic[pair[0]] +=1
                dic[pair[1]] +=1

        for check in dic.values():
            if check < 2:
                return False
        return self.check_cycle(tour.copy())

    def check_cycle(self, b_route):
        new_list = list()
        for key in list(b_route.keys()):
            if b_route[key] == False:
                b_route.pop(key)
        first_key = list(b_route.keys())[0]
        new_list.append(first_key[0])
        new_list.append(first_key[1])
        b_route.pop(first_key)
        
        while b_route:
            if len(new_list) == len(graph)+1:
                return True
            if new_list[-1] in new_list[:-1]: 
                return False
            for key in b_route.keys():
                if b_route[key] == "checked" : continue
                
                if new_list[-1] in key:
                    b_route[key] = "checked"
                    new_key = list(key)
                    new_key.remove(new_list[-1])
                    new_list.append(new_key[0])
        return False   

    def helper(self, city, tour, unchoose, current_best, current_gain):
        best_improvement = current_gain
        city.append(current_best)
        unchoose.remove(current_best)

        tour[tuple(set((city[0], city[1])))] = False #tour.remove((city[0], city[1]))
        tour[tuple(set((city[1], current_best)))] = True #tour.append((city[1], current_best))
        
        i = 2
        save_tour4 = None
        while city[-1] != city[0] and i + 1 < len(graph):
            improve = len(city)
            for pair in tour.copy().keys():

                if city[i] in pair:
                    if city[i-1] in pair:
                        continue
                    if pair[0] == city[i]:
                        next_city = pair[1]
                    else:
                        next_city = pair[0]
                    
                    if next_city not in unchoose:
                        continue
                    # next_city = pair - (city[i])
                    tour[pair] = False #tour.remove(pair)
                    save = False
                    if tuple(set((next_city, city[0]))) in tour:
                        if tour[tuple(set((next_city, city[0])))]:
                            save = True
                    tour[tuple(set((next_city, city[0])))] = True #tour.append((next_city, city[0]))

                    gain = self.graph[city[i]][next_city] - graph[next_city][city[0]] 
                    if not self.check_tour(tour) :#or gain < 0:
                        tour[tuple(set((next_city, city[0])))] = save #tour.append((next_city, city[0]))
                        tour[pair] = True #tour.append(pair)
                    else:
                        save_tour4 = tour
                        tour[tuple(set((next_city, city[0])))] = save #tour.append((next_city, city[0]))
                        unchoose.remove(next_city)
                        city.append(next_city)
                        break

            if improve - len(city) >= 0:
                tour[tuple(set((city[0], city[1])))] = True #tour.remove((city[0], city[1]))
                tour[tuple(set((city[1], current_best)))] = False #tour.append((city[1], current_best))
                if i >= 4:
                    return save_tour4 if save_tour4 else tour
                return tour
            current_gain = 0
            current_best = 0

            for next_city in unchoose:
                if tuple(set((city[i+1], next_city))) in tour:
                    continue
                gain = self.graph[city[i]][city[i+1]] - graph[city[i+1]][next_city]
                if gain > current_gain: # sort by gain
                    current_best = next_city
                    current_gain = gain 

            # no possible x or y 
            if current_best == 0:
                tour[tuple(set((city[-1], city[0])))] = True
                break
            
            city.append(current_best)
            best_improvement += current_gain

            if city[i+1] != current_best:
                tour[tuple(set((city[i+1], current_best)))] = True

            i += 2
        return tour

    def lin(self, current_state, graph, start=1, neighbor1=0, neighbor2=2):

        tour = {}
        for i in range(len(current_state)-1):
            tour[tuple(set((current_state[i], current_state[i+1])))] = True
            # tour.append((current_state[i], current_state[i+1]))
        cost_init = self.cost1(tour)
        best_improvement = 0
        city = []

        city.append(current_state[start]) # T_1 T:city
        if graph[current_state[start]][current_state[neighbor1]] > graph[current_state[start]][current_state[neighbor2]]:
            city.append(current_state[neighbor1]) #T_2
        else:
            city.append(current_state[neighbor2])
        

        unchoose = list(set(current_state) - set(city))
        
        current_gain = []
        current_best = []
        for next_city in unchoose:
            if tuple({city[1], next_city}) in tour.keys() :
                if tour[tuple({city[1], next_city})]:continue
            gain = graph[city[0]][city[1]] - graph[city[1]][next_city]
            if gain > 0: # sort by gain
                current_best.append(next_city)
                current_gain.append(gain)

        new_tour = None
        good_one = None
        while current_best:
            new_tour = self.helper(city.copy(), tour.copy(), unchoose.copy(), current_best[-1], current_gain[-1])
            if not self.check_tour(new_tour) or self.cost1(new_tour) > cost_init:
                current_gain.pop()
                current_best.pop()
            else:
                cost_init = self.cost1(new_tour)
                good_one = new_tour 
                current_gain.pop()
                current_best.pop()

        return good_one if good_one else tour
            
    def cost1(self, tour):
        cost = 0
        for pair in tour:
            if tour[pair] : 
                cost += self.graph[pair[0]][pair[1]]
        return cost

    def cost(self, tour):
        cost = 0
        for num in range(len(tour)-1):
            cost += self.graph[tour[num]][tour[num+1]]
        return cost

    def nearest_neighbor(self):
        current_city = random.randint(0,len(self.graph)-1)  # Starting from city 0
        tour = [current_city]
        total_cost = 0.0
        unvisited = list(set([i for i in range(len(self.graph))] ) - set([current_city]))

        while unvisited:
            nearest_city = min(unvisited, key=lambda city: self.graph[current_city][city])
            tour.append(nearest_city)
            total_cost += graph[current_city][nearest_city]
            current_city = nearest_city
            unvisited.remove(nearest_city)

        # Return to the starting city to complete the tour
        tour.append(tour[0])
        total_cost += self.graph[current_city][tour[0]]

        return tour

    def make_neighbor(self, random_sample):
        node_count = len(self.graph)
        thread_arg = list()
        for i in range(node_count-1):
            thread_arg.append((random_sample, self.graph, i, i+1, i-1))
        thread_arg.append((random_sample, self.graph, node_count-1, node_count-2, 0))


        future = list()
        result = list()
        best_cost = float('inf')
        best_route = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for i in range(node_count):
                future.append(executor.submit(self.lin, *thread_arg[i]))
                result.append(future[i].result())        

        for i in range(node_count):
            if self.cost1(result[i]) < best_cost:
                best_cost = self.cost1(result[i]) 
                best_route = result[i]
        return best_cost, best_route

    def solve(self):
        random_sample = self.nearest_neighbor()
        new_list = random_sample
        previous=1
        b_cost=0
        start_time = time.time()
        while f"{previous:.4f}" != f"{b_cost:.4f}":
            previous = b_cost
            b_cost, b_route = self.make_neighbor(new_list)

            self.f2.seek(0)
            self.f2.write(f"{b_cost:.4f} | {time.time() - start_time:.4f} \n")
            new_list = list()

            for key in list(b_route.keys()):
                if b_route[key] == False:
                    b_route.pop(key)

            
            first_key = list(b_route.keys())[0]
            new_list.append(first_key[0])
            new_list.append(first_key[1])
            b_route.pop(first_key)
            
            while b_route:
                if len(new_list) == len(graph)+1:break
                if new_list[-1] == new_list[0]:break
                for key in b_route.keys():
                    if b_route[key] == "checked" : continue
                    
                    if new_list[-1] in key:
                        b_route[key] = "checked"
                        new_key = list(key)
                        new_key.remove(new_list[-1])
                        new_list.append(new_key[0])

            print(f"intermediate tour: {new_list}")
        return b_cost, new_list

if __name__ == "__main__":
    # Set the working directory to the directory containing the script
    script_directory = os.path.dirname(os.path.realpath(__file__))
    os.chdir(script_directory)

    data_file_path = "../data/"
    data_file_name = "10_0.0_10.0.out"
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y%m%d_%H%M%S")
    result_file_path = f"../output/sls/{formatted_datetime}/"
    if not os.path.exists(result_file_path):
        os.makedirs(result_file_path)
    
    data = open(data_file_path + data_file_name, "r")
    lines = data.readlines()
    data.close()

    graph = []
    for line in lines[1:]:
        result = [float(x.strip()) for x in line.split(' ')]
        graph.append(result)
    
    f3 = open(f"{result_file_path}total_result_for_{len(graph)}.txt", "a+")
    f3.truncate(0) 
    f3.write(f"count | result cost | result tour \n") 
    best = float('inf')
    best_tour = None
    for i in range(10):
        inter = open(f"{result_file_path}intermediate_result_{len(graph)}_{i}.txt", "a+")
        inter.truncate(0)
        inter.write(f"current best cost | time passes \n")
        solver = TSPSolver(graph, inter)
        result_cost, result_tour = solver.solve()
        inter.close()
        f3.seek(0)
        f3.write(f"{i} | {result_cost:.4f} | {result_tour} \n") 
        if result_cost < best:
            best = result_cost
            best_tour = result_tour
        inter.close()
    
    f3.write("=============================================== \n") 
    f3.write(f"final result cost: {best:.4f} | optimal tour {best_tour} \n") 
    print(f"final result cost: {best:.4f} | optimal tour {best_tour} \n")
    f3.close()
    
        

                
        