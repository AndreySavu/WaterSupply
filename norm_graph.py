
class Vertex(object):
    def __init__(self, latitude, longitude, value=None):
        self.__latitude = latitude
        self.__longitude = longitude
        self.__value = value

    def get_latitude(self):
        return self.__latitude
    
    def get_longitude(self):
        return self.__longitude
    
    def get_value(self):
        return self.__value
    
    def set_latitude(self, lat):
        self.__latitude = lat
    
    def set_longitude(self, long):
        self.__longitude = long

    def set_value(self, value):
        self.__value = value

    
class Edge(object):

    def __init__(self,  source, destination, label=None, value=1):
        self.__source = source
        self.__destination = destination
        self.__label = label
        self.__value = value

    def set_source(self, source):
        self.__source = source

    def get_source(self):
        return self.__source

    def set_destination(self, destination):
        self.__destination = destination

    def get_destination(self):
        return self.__destination

    def set_label(self, label):
        self.__label = label

    def get_label(self):
        return self.__label

    def set_value(self, value):
        self.__value = value

    def get_value(self):
        return self.__value

class Graph(object):

    def __init__(self):
        self.vertexes = {}
        self.edges = {}

    def vertex_exist(self, vert):
        for name in self.vertexes:
            if self.vertexes[name].get_latitude() == vert.get_latitude() and self.vertexes[name].get_longitude() == vert.get_longitude():
                return 1
        return 0
    
    def add_vertex(self, name, latitude, longitude, value):
        new_vertex = Vertex(latitude, longitude, value)
        if not self.vertex_exist(new_vertex):
            self.vertexes[name] = new_vertex

    def get_vertex(self, name):
        return (name, self.vertexes[name].get_latitude(), self.vertexes[name].get_longitude(), self.vertexes[name].get_value())
    
    def remove_vertex(self, n):
        edges_to_delete = []
        for item in self.edges:
            print(self.edges[item].get_source())
            if self.edges[item].get_source() == self.get_vertex(n) or\
                self.edges[item].get_destination() == self.get_vertex(n):
                edges_to_delete.append(item)
                print('edge deleted')
        for item in edges_to_delete:
            del self.edges[item]
        del self.vertexes[n]

    def update_vertex(self, name, latitude, longitude, value):
        self.vertexes.update({name : Vertex(latitude, longitude, value)})

    def get_all_vertexes(self):
        out = []
        for name in self.vertexes:
            out.append((name, self.vertexes[name].get_latitude(), self.vertexes[name].get_longitude(), self.vertexes[name].get_value()))
        return out

    def edge_exists(self, edg):
        for name in self.edges:
            if (self.edges[name].get_source() == edg.get_source() and self.edges[name].get_destination() == edg.get_destination()) or \
            (self.edges[name].get_source() == edg.get_destination() and self.edges[name].get_destination() == edg.get_source()):
                return 1
        return 0

    def add_edge(self, name, source, destination, label = None, value = None):
        new_edge = Edge(source, destination, label, value)
        if not self.edge_exists(new_edge):
            self.edges[name] = new_edge

    def get_edge(self, name):
        return (name, self.edges[name].get_source(),
                      self.edges[name].get_destination(), 
                      self.edges[name].get_label(), 
                      self.edges[name].get_value())
    
    def remove_edge(self, name):
        del self.edges[name]

    def get_all_edges(self):
        out = []
        for name in self.edges:
            out.append((name, self.edges[name].get_source(), 
                        self.edges[name].get_destination(), 
                        self.edges[name].get_label(),
                        self.edges[name].get_value()))
        return out
    
gr = Graph()
gr.add_vertex('lol1',33,44, ('','','',''))

gr.update_vertex('lol1', 35, 30, ('1','2','3','4'))

print(gr.get_all_vertexes())
