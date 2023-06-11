import NormGraph as NG
from math import pi

def calc_lambda(type = 0, d = 1, v = 1):
    return 0

def v(q = 1, d = 1):
    return (4 * q / 3600) / (pi * d * d)

def h(l = 1, d = 1, v = 1, lambd = 1):
    return 0

class Dijkstra:

    def __init__(self, vertices, graph):
        self.vertices = vertices  # ("A", "B", "C" ...)
        self.graph = graph  # {"A": {"B": 1}, "B": {"A": 3, "C": 5} ...}

    def find_route(self, start, end):
        unvisited = {n: float("inf") for n in self.vertices}
        unvisited[start] = 0  # set start vertex to 0
        visited = {}  # list of all visited nodes
        parents = {}  # predecessors
        while unvisited:
            min_vertex = min(unvisited, key=unvisited.get)  # get smallest distance
            for neighbour, _ in self.graph.get(min_vertex, {}).items():
                if neighbour in visited:
                    continue
                new_distance = unvisited[min_vertex] + self.graph[min_vertex].get(neighbour, float("inf"))
                if new_distance < unvisited[neighbour]:
                    unvisited[neighbour] = new_distance
                    parents[neighbour] = min_vertex
            visited[min_vertex] = unvisited[min_vertex]
            unvisited.pop(min_vertex)
            if min_vertex == end:
                break
        return parents, visited

    @staticmethod
    def generate_path(parents, start, end):
        path = [end]
        while True:
            try:
                key = parents[path[0]]
            except KeyError:
                return []
            path.insert(0, key)
            if key == start:
                break
        return path
    
def commute_task_path(graph, vertex_to_isolate, end_vertex):
    """
    input_vertices = ("A", "B", "C", "D", "E", "F", "G")
    input_graph = {
        "A": {"B": 5, "D": 3, "E": 12, "F": 5},
        "B": {"A": 5, "D": 1, "G": 2},
        "C": {"E": 1, "F": 16, "G": 2},
        "D": {"A": 3, "B": 1, "E": 1, "G": 1},
        "E": {"A": 12, "C": 1, "D": 1, "F": 2},
        "F": {"A": 5, "C": 16, "E": 2},
        "G": {"B": 2, "C": 2, "D": 1}
    }
    """
    input_vertices_list = []
    input_graph = {}
    for vertex in graph.get_all_vertexes():
        input_vertices_list.append(vertex[0])
        buff_dict = {}
        for edge in graph.get_outgoing_edges(vertex[0]):
            if edge[1] == vertex[0]:
                buff_dict[edge[2]] = edge[3][3]
            if edge[2] == vertex[0]:
                buff_dict[edge[1]] = edge[3][3]
        input_graph[vertex[0]] = buff_dict
    input_vertices = tuple(input_vertices_list)
    start_vertex = vertex_to_isolate
    dijkstra = Dijkstra(input_vertices, input_graph)
    p, v = dijkstra.find_route(start_vertex, end_vertex)
    se = dijkstra.generate_path(p, start_vertex, end_vertex)
    #print('se = ', se)

    path_edges = []
    for i in range(len(se) - 1):
        path_edges.append(graph.get_edge_by_vertexes(se[i], se[i + 1]))
    #print('path_edges = ', path_edges)
    return path_edges, se

def commute_task(graph_start, vertex_to_isolate):
    graph = NG.Graph()
    for vertex in graph_start.get_all_vertexes():
        graph.add_vertex(vertex[0], vertex[1], vertex[2], vertex[3])
    for edge in graph_start.get_all_edges():
        graph.add_edge(edge[0], edge[1], edge[2], edge[3])
    while True:
        path, se = commute_task_path(graph, vertex_to_isolate, "Source1")
        #print(path)
        if len(path) == 0:
            break
        check = 0
        for edge in path:
            #print(edge[0], ', value = ', edge[3][12])
            if edge[3][12] == 1:
                graph.remove_edge(edge[0])
                check = 1
                break
        if check == 0:
            print('Коммутационная задача невыполнима (нет необходимой запорной арматуры)')
            return -1
    print('Все эджи = ', graph.get_all_edges())

    disabled = []
    for vertex in graph.get_all_vertexes():
        pth, buff = commute_task_path(graph, vertex_to_isolate, vertex[0])
        if buff == []:
            continue
        for vert in buff:
            if vert not in disabled:
                disabled.append(vert)
    print('disabled = ', disabled)
    return disabled

