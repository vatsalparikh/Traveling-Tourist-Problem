import csv
import copy
import itertools
import os
import datetime

''' A function used to print matrix to check if the attraction file is readed in right way'''
def print_map(matrix):
    size = len(matrix)
    for i in range(0, size):
        for j in range(0, size):
            print matrix[i][j],
            if matrix[i][j] < 10:
                print '',
        print '\n'



def get_edgeweight_matrix(file):  # Reading the distance file, to assign weight to edges
    d_data = csv.reader(file, dialect='excel')
    size = 0
    for line_ in d_data:
        if int(line_[1]) > size:
            size = int(line_[1])
    size += 1
    map_ = [[0 for i in range(size)]for i in range(size)]
    file.seek(0)
    d_data = csv.reader(file, dialect='excel')
    for line_ in d_data:
        map_[int(line_[0])][int(line_[1])] = copy.copy(float(line_[2]))
    for i in range(0, size):
        for j in range(0, i):
            map_[i][j] = copy.copy(map_[j][i])
    # get max edge
    max_edge = 0
    for i in range(0, size):
        for j in range(0, size):
            if map_[i][j] > max_edge:
                max_edge = map_[i][j]
    # Normalization value[i][j] = w[i][j]/ max w[i][j]
    for i in range(0, size):
        for j in range(0, size):
            map_[i][j] = map_[i][j] / max_edge
    # print_map(map_)
    file.seek(0)
    return map_


def get_vertexweight_list(file, x, y, z):  # Reading the attractions file, to assign weight to vertices
    v_value = []
    a_data = csv.reader(file, dialect='excel')
    max_popularity = 0
    max_time = 0
    max_money = 0
    # get max popularity, time and money
    for line_ in a_data:
        if float(line_[2]) > max_popularity:
            max_popularity = float(line_[2])
        if float(line_[3]) > max_time:
            max_time = float(line_[3])
        if float(line_[4]) > max_money:
            max_money = float(line_[4])
    file.seek(0)
    v_value.append(0)
    # # Normalization w[i] = (p[i] + m[i] + t[i]) / 3
    for line_ in a_data:
        v_value.append(x * (1 - float(line_[2]) / max_popularity) + y * (float(line_[3]) / max_time) + z * (float(line_[4]) / max_money))
    # print v_value
    file.seek(0)
    return v_value


def get_map(matrix, valuelist):
    #  W(U -> V) = e(U, V) + V (V)
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            matrix[i][j] = matrix[i][j] + valuelist[j]
    return matrix


class TSP(object):
    def __init__(self):
        self.graph = None
        self.size = 0
        self.vertex = ()
        # use pre_vertex to print rout. When one step is {{SET}, i} then the value is the prevertex to i
        self.pre_vertex = {}
        self.rout = []
        # when TTP reach the budget, which is the size of current vertex set (uesd to find the end set)
        self.end_size = 0
        # when TTP reach the budget, which is the last vertex (uesd to find the last vertex in the rout)
        self.end_point = 0
        # the last set, combine with the last vertex can backtrack the route.
        self.end_set = []
        self.attraction_cost = None    # attraction_cost[time][money], when each of it over budget in a particular size, stop.
        self.budget = []  # [time][money]
        self.attraction_dict = {}  # used to print attraction name
        # self.lastsecond_point = None

    def get_attraction_info(self, file):
        a_data = csv.reader(file, dialect='excel')
        size = 0
        for line_ in a_data:
            if int(line_[0]) > size:
                size = int(line_[0])
        size += 1
        file.seek(0)
        self.attraction_cost = [[0 for i in range(2)] for i in range(size)]
        # generate attraction cost for each vertex
        for line_ in a_data:
            self.attraction_cost[int(line_[0])][0] = float(line_[3])
            self.attraction_cost[int(line_[0])][1] = float(line_[4])
            self.attraction_dict[int(line_[0])] = line_[1]
        file.seek(0)

    def get_graph(self, matrix):
        self.graph = copy.deepcopy(matrix)
        self.size = len(matrix)
        self.end_size = len(matrix) - 1
        vertex_list = []
        for i in range(1, len(matrix)):
            vertex_list.append(i)
        self.vertex = tuple(list(vertex_list))

    def get_budget(self, budget):
        self.budget = copy.copy(budget)

    def solve(self):
        dist = {}
        if_break = 0  # may not useful
        # the base case: When the set just one value, dist{{set}, i} = w(0, i)
        for i in range(1, self.size):
            set = (i,)
            dist[set, i] = copy.copy(self.graph[0][i])
            self.pre_vertex[set, i] = 0
        for set_size in range (2, self.size):
            # for each size, find all combination of vertices
            setlist = list(itertools.combinations(self.vertex, set_size))
            min_budget_current_size = [1000000000000, 1000000000000]  # if all budget[time, money] in size k > budget, then stop
            for set in setlist:
                budget_current_set = [0, 0]  # minimum budget for a current set[time][money]
                for j in set:
                    budget_current_set[0] = budget_current_set[0] + self.attraction_cost[j][0]
                    budget_current_set[1] = budget_current_set[1] + self.attraction_cost[j][1]
                    #dist[set, j] = 2
                    # for each j in set, remove j to get subset
                    tempsetlist = list(tuple(set))          # change tuple structure to list
                    tempsetlist.remove(j)
                    subset = tuple(list(tempsetlist))
                    mindist = 1000000000000
                    # dist({SET}, j) = min {dist(subset), i + w(i, j)}
                    for k in subset:
                        if ((dist[subset, k] + self.graph[k][j]) < mindist):
                            mindist = dist[subset, k] + self.graph[k][j]
                            self.pre_vertex[set, j] = k  # reserve prevertex to backtrack the route
                    dist[set, j] = mindist
                # get the min budget of current size of set
                if min_budget_current_size[0] > budget_current_set[0]:
                    min_budget_current_size[0] = budget_current_set[0]
                if min_budget_current_size[1] > budget_current_set[1]:
                    min_budget_current_size[1] = budget_current_set[1]
            # if each cost over the budget input, stop
            if min_budget_current_size[0] > budget[0] or min_budget_current_size[1] > budget[1]:
                self.end_size = set_size - 1
                if_break = 1
                break

        # find out end set and end point
        setlist = list(itertools.combinations(self.vertex, self.end_size))
        mindist_set= {}  # mindist for each set (no matter which is the end point)
        max_cost = 0      # choose the set with max cost but within budget
        for set in setlist:
            mindist_set[set] = 1000000
            budget_current_set = [0, 0]
            for j in set:
                if mindist_set[set] > dist[set, j]:
                    mindist_set[set] = dist[set, j]
                budget_current_set[0] = budget_current_set[0] + self.attraction_cost[j][0]
                budget_current_set[1] = budget_current_set[1] + self.attraction_cost[j][1]

            if (budget_current_set[0] <= self.budget[0]) and (budget_current_set[1] <= self.budget[1]):
                if mindist_set[set] > max_cost:
                    self.end_set = copy.copy(set)
        # now we have a set, need to find out end point
        mindist = 10000000
        for j in self.end_set:
            if mindist > dist[self.end_set, j] + self.graph[j][0]:
                mindist = dist[self.end_set, j] + self.graph[j][0]
                self.end_point = j


    def print_rout(self):
        # backtrack to print the route
        #set = (0,1,2,3,4,5,6,7,8,9,)

        set = self.end_set
        i = self.end_point
        self.rout.insert(0, self.end_point)
        while (len(set) >= 1):
            # print self.pre_vertex[set, i]
            a = self.pre_vertex[set, i]
            self.rout.insert(0, a)
            tempsetlist = list(tuple(set))
            tempsetlist.remove(i)
            set = tuple(list(tempsetlist))
            i = a
        self.rout.append(0)
        print 'path shown as vertex:'
        print self.rout
        budget = [0, 0]
        for j in self.end_set:
            budget[0] = budget[0] + self.attraction_cost[j][0]
            budget[1] = budget[1] + self.attraction_cost[j][1]
        print 'total cost', budget
        print 'path shown as attractions name:'
        for i in range(0, len(self.rout)):
            print self.attraction_dict[self.rout[i]],
            if i < len(self.rout)-1:
                print '->',
        out_file = open("Path.txt", "w")
        for i in range (len(self.rout)):
            # out_file.write(str(self.rout[i]) + "->" + str(self.attraction_dict[self.rout[i]]) + "\n")
            if i < len(self.rout) - 2:
                out_file.write(str(self.rout[i]) + ",")
            elif i == len(self.rout) - 2:
                out_file.write(str(self.rout[i]))

        out_file.close()
        return self.rout

if __name__ == "__main__":

    # read CSV file. a is info about attraction. b is distance between attractions
    a = open("Attractions_NYC.csv", 'rU')
    d = open("Distance_NYC.csv", 'rU')


    # if default, budget will be infinite and P = T = M = 1/3
    budget = [1000000, 1000000]
    P = 0.33
    T = 0.33
    M = 0.33


    str1 = "./Downloads/savedfile"
    str3 = ".txt"

    last_file_num = 0
    while(1):
        if last_file_num == 0:
            str2 = ""
        else:
            str2 = "(" + str(last_file_num) + ")"
        path = str1 + str2 + str3
        last_file_num += 1
        str4 = "(" + str(last_file_num) + ")"
        next_path = str1 + str4 + str3
        if (os.path.exists(path) == True) and (os.path.exists(next_path) == False):
            c = open(path, 'rU')
            c_data = c.read()
            c_data_list = c_data.split(",")
            print c_data_list
            P = float(c_data_list[0])
            T = float(c_data_list[1])
            M = float(c_data_list[2])
            budget[0] = float(c_data_list[3])
            budget[1] = float(c_data_list[4])
            break

    # print "The weight of popularity is", P, 
    # "The weight of time is", T, "The weight of money is", M, "budget is ", budget

    '''
    time = raw_input('Please input time constraint. If has no constraint in time, input none\n')
    money = raw_input('Please input money constraint, If has no constraint in money, input none\n')
    if time != "none":
        budget[0] = int(time)
    if money != "none":
        budget[1] = int(money)
    '''
    # generate cost matrix
    edgeweight_matrix = get_edgeweight_matrix(d)


    vertexweight_list = get_vertexweight_list(a, P, T, M)
    cost_matrix = get_map(edgeweight_matrix, vertexweight_list)

    tsp = TSP()
    tsp.get_graph(cost_matrix)
    tsp.get_attraction_info(a)
    tsp.get_budget(budget)



    starttime = datetime.datetime.now()
    tsp.solve()
    tsp.print_rout()
    endtime = datetime.datetime.now()
    # print '\ntime used is', (endtime - starttime).microseconds, 'microseconds'




