from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
from tkinter import filedialog
#import os
#import customtkinter
#import tkintermapview
import TKmv
#from graphpy.graph import Graph
import sqlite3
import norm_graph as NG
import math

class App:

    def create_db(name):
        cx = sqlite3.connect("schemas/"+ name +".db")
        cu = cx.cursor()
        cu.execute("CREATE TABLE sources (\
	                             name VARCHAR(50) PRIMARY KEY,\
	                             coord1 DOUBLE,\
	                             coord2 DOUBLE,\
                                 H DOUBLE,\
                                 G DOUBLE,\
                                 Gmax DOUBLE,\
	                             P DOUBLE);")
        cu.execute("CREATE TABLE towers (\
	                             name VARCHAR(50) PRIMARY KEY,\
	                             coord1 DOUBLE,\
	                             coord2 DOUBLE,\
                                 H DOUBLE,\
                                 G DOUBLE,\
                                 Hwater DOUBLE,\
                                 V DOUBLE,\
	                             P DOUBLE);")
        cu.execute("CREATE TABLE reservoirs (\
	                             name VARCHAR(50) PRIMARY KEY,\
	                             coord1 DOUBLE,\
	                             coord2 DOUBLE,\
                                 H DOUBLE,\
                                 G DOUBLE,\
                                 Hwater DOUBLE,\
                                 P DOUBLE);")
        cu.execute("CREATE TABLE connectors (\
	                             name VARCHAR(50) PRIMARY KEY,\
	                             coord1 DOUBLE,\
	                             coord2 DOUBLE,\
                                 H DOUBLE,\
                                 G DOUBLE,\
                                 P DOUBLE,\
                                 Pressure DOUBLE);")
        cu.execute("CREATE TABLE consumers (\
	                             name VARCHAR(50) PRIMARY KEY,\
	                             coord1 DOUBLE,\
	                             coord2 DOUBLE,\
                                 H DOUBLE,\
                                 G DOUBLE,\
                                 Pmin DOUBLE,\
                                 P DOUBLE);")
        cu.execute("CREATE TABLE pipes (\
                                 name VARCHAR(50) PRIMARY KEY,\
                                 name1 VARCHAR(50), name2 VARCHAR(50),\
                                 coord11 DOUBLE, coord12 DOUBLE,\
                                 coord21 DOUBLE, coord22 DOUBLE,\
                                 H1 DOUBLE, H2 DOUBLE,\
                                 D DOUBLE, Len DOUBLE, G DOUBLE, R DOUBLE,\
                                 Glost DOUBLE,\
                                 Speed DOUBLE,\
                                 Lambda DOUBLE,\
                                 Lost DOUBLE,\
                                 AcceptPres DOUBLE,\
                                 Material VARCHAR(20),\
                                 hasValve INTEGER,\
                                 opened INTEGER);")
        cx.commit()
        cx.close()

    def clear_graph():
        pass

    def add_marker_source(self, coords):
        adress = str(TKmv.convert_coordinates_to_address(coords[0], coords[1]).street) + " " + str(TKmv.convert_coordinates_to_address(coords[0], coords[1]).housenumber)
        if len(self.gr.get_all_vertexes()) == 0:
            dat = 'Source0'
        else:
            dat = "Source" + str(int(self.gr.get_all_vertexes()[-1][0][-1:])+1)
        new_marker = self.map_widget.set_marker(coords[0], coords[1],
                                                text = "ИСТ " + adress,
                                                icon = "icons/source.png",
                                                data = dat)                          
        self.gr.add_vertex("Source" + str(len(self.gr.get_all_vertexes())), coords[0], coords[1], ('', '', '', ''))
    
    def add_marker_tower(self, coords):
        adress = str(TKmv.convert_coordinates_to_address(coords[0], coords[1]).street) + " " + str(TKmv.convert_coordinates_to_address(coords[0], coords[1]).housenumber)
        if len(self.gr.get_all_vertexes()) == 0:
            dat = 'WaterTower0'
        else:
            dat = "WaterTower" + str(int(self.gr.get_all_vertexes()[-1][0][-1:])+1)
        new_marker = self.map_widget.set_marker(coords[0], coords[1],
                                                text = "ВНБ" + adress,
                                                icon = "icons/tower.png",
                                                data = dat)                          
        self.gr.add_vertex("WaterTower" + str(len(self.gr.get_all_vertexes())), coords[0], coords[1], ('', '', '', '', ''))
    
    def add_marker_reservoir(self, coords):
        adress = str(TKmv.convert_coordinates_to_address(coords[0], coords[1]).street) + " " + str(TKmv.convert_coordinates_to_address(coords[0], coords[1]).housenumber)
        if len(self.gr.get_all_vertexes()) == 0:
            dat = 'CounterReservoir0'
        else:
            dat = "CounterReservoir" + str(int(self.gr.get_all_vertexes()[-1][0][-1:])+1)
        new_marker = self.map_widget.set_marker(coords[0], coords[1],
                                                text = "КР " + adress,
                                                icon = "icons/reservoir.png",
                                                data = dat)                          
        self.gr.add_vertex("CounterReservoir" + str(len(self.gr.get_all_vertexes())), coords[0], coords[1], ('', '', '', ''))
    
    def add_marker_consumer(self, coords):
        adress = str(TKmv.convert_coordinates_to_address(coords[0], coords[1]).street) + " " + str(TKmv.convert_coordinates_to_address(coords[0], coords[1]).housenumber)
        if len(self.gr.get_all_vertexes()) == 0:
            dat = 'Consumer0'
        else:
            dat = "Consumer" + str(int(self.gr.get_all_vertexes()[-1][0][-1:])+1)
        new_marker = self.map_widget.set_marker(coords[0], coords[1],
                                                text = "ПТР " + adress,
                                                icon = "icons/consumer.png",
                                                data = dat)
        self.gr.add_vertex(dat, coords[0], coords[1], ('', '', '', ''))

    def add_marker_connector(self, coords):
        if len(self.gr.get_all_vertexes()) == 0:
            dat = 'Connector0'
        else:
            dat = "Connector" + str(int(self.gr.get_all_vertexes()[-1][0][-1:])+1)
        new_marker = self.map_widget.set_marker(coords[0], coords[1],
                                                text = "РЗВ " + str(round(coords[0],4)) + "; " + str(round(coords[1],4)),
                                                icon = "icons/connector.png",
                                                data = dat)
        self.gr.add_vertex(dat, coords[0], coords[1], ('', '', '', ''))

    def delete_marker(self, coords):
        buff = []
        for marker in self.map_widget.canvas_marker_list:
            if not (marker.get_canvas_pos(coords)[0] > marker.get_canvas_pos(marker.position)[0] + 20 or
                marker.get_canvas_pos(coords)[0] < marker.get_canvas_pos(marker.position)[0] - 20 or
                marker.get_canvas_pos(coords)[1] > marker.get_canvas_pos(marker.position)[1] + 20 or
                marker.get_canvas_pos(coords)[1] < marker.get_canvas_pos(marker.position)[1] - 20):   
                    
                for poly in self.map_widget.canvas_polygon_list:
                    if poly.data[0] == marker.data or poly.data[1] == marker.data:
                        buff.append(poly)
                self.gr.remove_vertex(marker.data)
                self.map_widget.delete(marker)
                for poly in buff:
                    self.map_widget.delete(poly)
                break

    def properties(self, object_name):
        width=self.root.winfo_width()*0.7
        
        for i in range(len(self.props_name)):
            self.props_name[i].place_forget()
            self.props_value[i].place_forget()
            self.props_value[i].delete(0,END)

        _name = object_name
        _object = self.gr.get_vertex(_name)
        match _name[:4]:
            case 'Sour': #источник водоснабжения
                _type = 'Источник'
                list_props_name = ['Высота объекта, м', 'Расход воды, м3/час', 
                                   'Максимальный расход, м3/час', 'Напор на выходе, м', ]
            case 'Towe': #водонапорная башня
                _type = 'Водонапорная башня'
                list_props_name = ['Высота объекта, м', 'Расход воды, м3/час',
                                   'Высота воды, м', 'Объем запаса воды, м3', 
                                   'Напор, м']
            case 'Rese': #контррезервуар
                _type = 'Контррезервуар'
                list_props_name = ['Высота объекта, м', 'Расход воды, м3/час',
                                   'Высота воды, м', 'Напор, м']
            case 'Conn':
                _type = 'Узер(разветвление)'
                list_props_name = ['Высота объекта, м', 'Расход воды, м3/час',
                                   'Напор, м', 'Давление воды, м']
            case 'Cons':
                _type = 'Потребитель'
                list_props_name = ['Высота объекта, м', 'Расчетный расход воды, м3/час', 
                                   'Минимальный напор, м', 'Напор, м']

        self.type.config(text = _type)
        self.name.config(text = _name)
        self.coordinates.config(text = 'Координаты: ' + str(_object[1]) + " -- " + str(_object[2]))
        self.type.place( x=width+15, y=30)
        self.name.place( x=width+15, y=50)
        self.coordinates.place( x=width+15, y=70)
        
        for i in range (len(_object[3])):          
            self.props_name[i].config(text= list_props_name[i]) 
            self.props_value[i].insert(0, _object[3][i])
            self.props_name[i].place( x=width+15, y=120+i*20)  
            self.props_value[i].place( x=width+60, y=120+i*20) 
    
    def properties_line(self, object_name):
            width=self.root.winfo_width()*0.7
            
            for i in range(len(self.props_name)):
                self.props_name[i].place_forget()
                self.props_value[i].place_forget()
                self.props_value[i].delete(0,END)

            _name = object_name
            _object = self.gr.get_edge(_name)
            
            _type = 'Участок'
            list_props_name = ['Высота начала, м', 'Высота конца, м',
                               'Внутренний диаметр, м', 'Длина участка, м',
                               'Расход воды, м3/час', 'Гидравлическое сопротивление, м/(т/ч)2',
                               'Потери напора на участке, м', 'Скорость движения воды, м/с',
                               'Коэффициент гидравл. трения(λ)', 'Утечка, м3/ч', 
                               'Условно допустимое давление, м']
            

            self.type.config(text = _type)
            self.name.config(text = _name)
            self.coordinates.config(text = 'Координаты: ' + str(_object[1]) + " -- " + str(_object[2]))
            self.type.place( x=width+15, y=30)
            self.name.place( x=width+15, y=50)
            self.coordinates.place( x=width+15, y=70)
            
            for i in range (len(_object[3])):          
                self.props_name[i].config(text= list_props_name[i]) 
                self.props_value[i].insert(0, _object[3][i])
                self.props_name[i].place( x=width+15, y=120+i*20)  
                self.props_value[i].place( x=width+60, y=120+i*20) 
            
            self.props_name[11].config(text= 'Материал трубы')#combo box
            self.props_name[12].config(text= 'Наличие запорной арматуры')#combo box
            self.props_name[13].config(text= 'Процент открытия') #entry


        
    def delete_line(self, coords):
        for poly in self.map_widget.canvas_polygon_list:
            a = poly.get_canvas_pos(poly.position_list[0], self.root.winfo_width()*0.7, self.root.winfo_height())
            b = poly.get_canvas_pos(poly.position_list[1], self.root.winfo_width()*0.7, self.root.winfo_height())
            c = poly.get_canvas_pos(coords, self.root.winfo_width()*0.7, self.root.winfo_height())
            print("ABC: ", a,'\n', b,'\n',c)
            print("E: ", abs(math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2) - 
                    (math.sqrt((a[0] - c[0])**2 + (a[1] - c[1])**2) + math.sqrt((b[0] - c[0])**2 + (b[1] - c[1])**2))))
            if abs(math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2) - 
                   (math.sqrt((a[0] - c[0])**2 + (a[1] - c[1])**2) + math.sqrt((b[0] - c[0])**2 + (b[1] - c[1])**2))) < 0.4:
                   self.gr.remove_edge(poly.data[0] + poly.data[1])
                   self.map_widget.delete(poly)

    def add_line(self, coords):
        getfirstpoint = False
        getsecondpoint = False
        if self.firstpoint is None:
            for marker in self.map_widget.canvas_marker_list:
                if not (marker.get_canvas_pos(coords)[0] > marker.get_canvas_pos(marker.position)[0] + 30 or
                    marker.get_canvas_pos(coords)[0] < marker.get_canvas_pos(marker.position)[0] - 30 or
                    marker.get_canvas_pos(coords)[1] > marker.get_canvas_pos(marker.position)[1] + 30 or
                    marker.get_canvas_pos(coords)[1] < marker.get_canvas_pos(marker.position)[1] - 30):
                        self.firstpoint = marker
                        getfirstpoint = True
                        break
            if not getfirstpoint:
                print("Первая точка не найдена")
        else:
            for marker in self.map_widget.canvas_marker_list:
                if (not (marker.get_canvas_pos(coords)[0] > marker.get_canvas_pos(marker.position)[0] + 30 or
                    marker.get_canvas_pos(coords)[0] < marker.get_canvas_pos(marker.position)[0] - 30 or
                    marker.get_canvas_pos(coords)[1] > marker.get_canvas_pos(marker.position)[1] + 30 or
                    marker.get_canvas_pos(coords)[1] < marker.get_canvas_pos(marker.position)[1] - 30)) and self.firstpoint.data != marker.data:
                    self.secondpoint = marker
                    getsecondpoint = True
                    buff = [self.firstpoint.position, self.secondpoint.position]
                    
                    current_amount = len(self.gr.get_all_edges())
                    self.gr.add_edge(self.firstpoint.data + self.secondpoint.data,
                                        self.gr.get_vertex(self.firstpoint.data),
                                        self.gr.get_vertex(self.secondpoint.data))
                    
                    if current_amount != len(self.gr.get_all_edges()):
                        self.map_widget.set_polygon(buff, data=(self.firstpoint.data, self.secondpoint.data))

                    self.firstpoint = None
                    self.secondpoint = None
                    break
            if not getsecondpoint:
                print("Вторая точка не найдена")

            print("Edges (", len(self.gr.get_all_edges()), ":")
            print(self.gr.get_all_edges())

    def open_new_map(self, pos=(55.010159, 82.925716), zoom = 10):
        self.map_widget = TKmv.TkinterMapView(self.root, width=self.root.winfo_width()*0.7, height=self.root.winfo_height(), corner_radius=0)
        self.map_widget.set_position(pos[0], pos[1])
        self.map_widget.set_zoom(zoom)
        self.map_widget.grid(row=0, column=0)
        #print(TKmv.decimal_to_osm(pos[0], pos[1], zoom))

        self.map_widget.add_right_click_menu_command(label="Добавить источник", 
                                command=self.add_marker_source, 
                                pass_coords=True,
                                )
        self.map_widget.add_right_click_menu_command(label="Добавить водонапорную башню", 
                                command=self.add_marker_tower, 
                                pass_coords=True,
                                )
        self.map_widget.add_right_click_menu_command(label="Добавить контеррезервуар", 
                                command=self.add_marker_reservoir, 
                                pass_coords=True,
                                )        
        self.map_widget.add_right_click_menu_command(label="Добавить потребителя", 
                                command=self.add_marker_consumer, 
                                pass_coords=True,
                                )
        self.map_widget.add_right_click_menu_command(label="Добавить узел", 
                                command=self.add_marker_connector, 
                                pass_coords=True,
                                )
        self.map_widget.add_right_click_menu_command_markers(label="Добавить соединение", 
                                command=self.add_line,
                                pass_coords=True 
                                )
        self.map_widget.add_right_click_menu_command_markers(label="Свойства", 
                                command=self.properties,
                                pass_coords=False 
                                )
        self.map_widget.add_right_click_menu_command_markers(label="Удалить объект", 
                                command=self.delete_marker,
                                pass_coords=True 
                                )
        self.map_widget.add_right_click_menu_command_lines(label="Удалить трубу", 
                                command=self.delete_line,
                                pass_coords=True 
                                )

        
        self.map_widget.save_state_to_file
    
    def load(self):
        cx = sqlite3.connect("schemas/water.db")
        cu = cx.cursor()
        cu.execute("SELECT * FROM map;")
        out = cu.fetchall()
        self.open_new_map((out[0][1], out[0][2]), out[0][3])
        
        cu.execute("SELECT * FROM sources;")
        out = cu.fetchall()
        for row in out:
            new_marker = self.map_widget.set_marker(row[1], row[2],
                                                    text=row[3],
                                                    icon="source.png",
                                                    data = row[0])
            self.gr.add_vertex(row[0], row[1], row[2], row[3])

        cu.execute("SELECT * FROM consumers;")
        out = cu.fetchall()
        for row in out:
            new_marker = self.map_widget.set_marker(row[1], row[2],
                                                    text=row[3],
                                                    icon="consumer.png",
                                                    data = row[0])
            self.gr.add_vertex(row[0], row[1], row[2], row[3])
        
        cu.execute("SELECT * FROM connectors;")
        out = cu.fetchall()
        for row in out:
            new_marker = self.map_widget.set_marker(row[1], row[2],
                                                    text=row[3],
                                                    icon="connector.png",
                                                    data = row[0])
            self.gr.add_vertex(row[0], row[1], row[2], row[3])
        
        cu.execute("SELECT * FROM pipes;")
        out = cu.fetchall()
        for row in out:
            buff = [(row[3], row[4]), (row[5], row[6])]
            self.map_widget.set_polygon(buff, data=(row[1], row[2]))
            self.gr.add_edge(row[0], self.gr.get_vertex(row[1]), self.gr.get_vertex(row[2]))

        cx.commit()
        cx.close()
        
    def save(self):
        cx = sqlite3.connect("schemas/water.db")
        cu = cx.cursor()
        pos = self.map_widget.convert_canvas_coords_to_decimal_coords(self.map_widget.width / 2, self.map_widget.height / 2)
        print(pos)
        cu.execute("DELETE FROM sources;")
        cu.execute("DELETE FROM consumers;")
        cu.execute("DELETE FROM connectors;")
        cu.execute("DELETE FROM pipes;")
        cu.execute("DELETE FROM map;")
        cu.execute("INSERT INTO map (pos1, pos2, zoom) VALUES (?, ?, ?);", (pos[0],
                                                                            pos[1],
                                                                            self.map_widget.zoom))
        for item in self.gr.get_all_vertexes():
            if item[0][:5] == "Sourc":
                print("src")
                cu.execute("INSERT INTO sources (name, coord1, coord2, value) VALUES (?, ?, ?, ?);", 
                           (item[0], item[1], item[2], item[3]))         
            if item[0][:5] == "Consu":
                print("cns")
                cu.execute("INSERT INTO consumers (name, coord1, coord2, value) VALUES (?, ?, ?, ?);", 
                           (item[0], item[1], item[2], item[3]))    
            if item[0][:5] == "Conne":
                print("con")
                cu.execute("INSERT INTO connectors (name, coord1, coord2, value) VALUES (?, ?, ?, ?);", 
                           (item[0], item[1], item[2], item[3]))

        for item in self.gr.get_all_edges():
            print("pip")
            cu.execute("INSERT INTO pipes (name, name1, name2, coord11, coord12, coord21, coord22) VALUES (?, ?, ?, ?, ?, ?, ?);", 
                       (item[0], item[1][0], item[2][0], item[1][1], item[1][2], item[2][1], item[2][2]))
        cx.commit()
        cx.close()

    def __init__(self):


        #граф-----------------------------------
        self.gr = NG.Graph()
        self.firstpoint = None
        self.secondpoint = None
        self.root = Tk()
        self.root.geometry('1200x600')
        #self.root.state('zoomed')
        #вывод текста справа
        self.type = ttk.Label()
        self.name = ttk.Label()
        self.coordinates = ttk.Label()
        self.props_name = [ttk.Label() for i in range(5)]
        self.props_value = [ttk.Entry(width=40) for i in range(5)]
        self.save_button = ttk.Button(text='Сохранить',)
      
              
        #верхний бар------------------------------------------------------
        self.mainmenu = Menu(self.root) 
        self.root.config(menu=self.mainmenu) 
     
        #работа с файлами
        self.filemenu = Menu(self.mainmenu, tearoff=0)
        self.filemenu.add_command(label="Создать новую схему(с картой)", 
                 command=self.open_new_map)
        self.filemenu.add_command(label="Открыть...",
                  command=self.load)
        self.filemenu.add_command(label="Сохранить...",
                  command=self.save)
        self.filemenu.add_command(label="Выход")
        #работа с объектами
        self.addObjectmenu = Menu(self.mainmenu, tearoff=0)
        self.addObjectmenu.add_command(label="Добавить объект")#, command=self.addMarker)
        self.addObjectmenu.add_command(label="Проложить ТРУБУ)")
        #справка
        self.helpmenu = Menu(self.mainmenu, tearoff=0)
        self.helpmenu.add_command(label="Помощь")
        self.helpmenu.add_command(label="О программе")

        self.mainmenu.add_cascade(label="Файл", menu=self.filemenu)
        self.mainmenu.add_cascade(label="Добавить объект", menu=self.addObjectmenu)
        self.mainmenu.add_cascade(label="Справка", menu=self.helpmenu)
        
        #self.root.bind("<Configure>", self.onChange)
        self.root.mainloop()



app = App()
