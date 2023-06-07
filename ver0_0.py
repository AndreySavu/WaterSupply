from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import TKmv
import sqlite3
import norm_graph as NG
import math

class App:

    def create_db(self, name):
        cx = sqlite3.connect(name)
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
        cu.execute("CREATE TABLE map (\
	                id INTEGER DEFAULT 1,\
	                pos1 DOUBLE,\
	                pos2 DOUBLE,\
	                zoom INTEGER);")
        cx.commit()
        cx.close()

    def clear_db(self, name):
        cx = sqlite3.connect(name)
        cu = cx.cursor()
        cu.execute("DELETE FROM sources;")
        cu.execute("DELETE FROM towers;")
        cu.execute("DELETE FROM reservoirs;")
        cu.execute("DELETE FROM connectors;")
        cu.execute("DELETE FROM consumers;")
        cu.execute("DELETE FROM pipes;")
        cu.execute("DELETE FROM map;")
        cx.commit()
        cx.close()

    def add_marker_source(self, coords):
        adress = str(TKmv.convert_coordinates_to_address(coords[0], coords[1]).street) + \
            " " + str(TKmv.convert_coordinates_to_address(coords[0], coords[1]).housenumber)
        dat = "Source" + str(self.last_N_of_object[0] + 1)
        self.map_widget.set_marker(coords[0], coords[1],
                                    text = "ИСТ " + adress,
                                    icon = "icons/source.png",
                                    data = dat)                          
        self.gr.add_vertex(dat, coords[0], coords[1], (0, 0, 0, 0))
        self.last_N_of_object[0] += 1

    def add_marker_tower(self, coords):
        adress = str(TKmv.convert_coordinates_to_address(coords[0], coords[1]).street) + \
            " " + str(TKmv.convert_coordinates_to_address(coords[0], coords[1]).housenumber)
        dat = "WaterTower" + str(self.last_N_of_object[1] + 1)
        self.map_widget.set_marker(coords[0], coords[1],
                                                text = "ВНБ " + adress,
                                                icon = "icons/tower.png",
                                                data = dat)                          
        self.gr.add_vertex(dat, coords[0], coords[1], (0, 0, 0, 0, 0))
        self.last_N_of_object[1] += 1
        
    def add_marker_reservoir(self, coords):
        adress = str(TKmv.convert_coordinates_to_address(coords[0], coords[1]).street) + \
            " " + str(TKmv.convert_coordinates_to_address(coords[0], coords[1]).housenumber)
        dat = "CounterReservoir" + str(self.last_N_of_object[2] + 1)
        self.map_widget.set_marker(coords[0], coords[1],
                                    text = "КР " + adress,
                                    icon = "icons/reservoir.png",
                                    data = dat)                          
        self.gr.add_vertex(dat, coords[0], coords[1], (0, 0, 0, 0))
        self.last_N_of_object[2] += 1

    def add_marker_consumer(self, coords):
        adress = str(TKmv.convert_coordinates_to_address(coords[0], coords[1]).street) + \
            " " + str(TKmv.convert_coordinates_to_address(coords[0], coords[1]).housenumber)
        dat = "Consumer" + str(self.last_N_of_object[3] + 1)
        self.map_widget.set_marker(coords[0], coords[1],
                                    text = "ПТР " + adress,
                                    icon = "icons/consumer.png",
                                    data = dat)
        self.gr.add_vertex(dat, coords[0], coords[1], (0, 0, 0, 0))
        self.last_N_of_object[3] += 1

    def add_marker_connector(self, coords):
        dat = "Connector" + str(self.last_N_of_object[4] + 1)
        self.map_widget.set_marker(coords[0], coords[1],
                                    text = "РЗВ " + str(round(coords[0],4)) + "; " + str(round(coords[1],4)),
                                    icon = "icons/connector.png",
                                    data = dat)
        self.gr.add_vertex(dat, coords[0], coords[1], (0, 0, 0, 0))
        self.last_N_of_object[4] += 1

    def add_line(self, coords):
        getfirstpoint = False
        getsecondpoint = False
        if self.firstpoint is None:
            for marker in self.map_widget.canvas_marker_list:
                if not (marker.get_canvas_pos(coords)[0] > marker.get_canvas_pos(marker.position)[0] + 20 or
                    marker.get_canvas_pos(coords)[0] < marker.get_canvas_pos(marker.position)[0] - 20 or
                    marker.get_canvas_pos(coords)[1] > marker.get_canvas_pos(marker.position)[1] + 20 or
                    marker.get_canvas_pos(coords)[1] < marker.get_canvas_pos(marker.position)[1] - 20):
                        self.firstpoint = marker
                        getfirstpoint = True
                        break
            if not getfirstpoint:
                print("Первая точка не найдена")
        else:
            for marker in self.map_widget.canvas_marker_list:
                if  not (marker.get_canvas_pos(coords)[0] > marker.get_canvas_pos(marker.position)[0] + 20 or
                        marker.get_canvas_pos(coords)[0] < marker.get_canvas_pos(marker.position)[0] - 20 or
                        marker.get_canvas_pos(coords)[1] > marker.get_canvas_pos(marker.position)[1] + 20 or
                        marker.get_canvas_pos(coords)[1] < marker.get_canvas_pos(marker.position)[1] - 20) and\
                        self.firstpoint.data != marker.data:
                    self.secondpoint = marker
                    getsecondpoint = True
                    buff = [self.firstpoint.position, self.secondpoint.position]
                    
                    current_amount = len(self.gr.get_all_edges())
                    dat = "Edge" + str(self.last_N_of_object[5] + 1)
                    self.gr.add_edge(dat,
                                        self.firstpoint.data,
                                        self.secondpoint.data, (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'металл', 0, 0))
                    
                    if current_amount != len(self.gr.get_all_edges()):
                        self.map_widget.set_polygon(buff, data=dat)
                        self.last_N_of_object[5] += 1

                    self.firstpoint = None
                    self.secondpoint = None
                    break
            if not getsecondpoint:
                print("Вторая точка не найдена")

            print("Edges (", len(self.gr.get_all_edges()), ":")
            print(self.gr.get_all_edges())

    def delete_marker(self, coords):
        buff = []
        for marker in self.map_widget.canvas_marker_list:
            if not (marker.get_canvas_pos(coords)[0] > marker.get_canvas_pos(marker.position)[0] + 20 or
                marker.get_canvas_pos(coords)[0] < marker.get_canvas_pos(marker.position)[0] - 20 or
                marker.get_canvas_pos(coords)[1] > marker.get_canvas_pos(marker.position)[1] + 20 or
                marker.get_canvas_pos(coords)[1] < marker.get_canvas_pos(marker.position)[1] - 20):   
                    
                for poly in self.map_widget.canvas_polygon_list:
                    if self.gr.get_edge(poly.data)[1] == marker.data or self.gr.get_edge(poly.data)[2] == marker.data:
                        buff.append(poly)
                self.gr.remove_vertex(marker.data)
                self.map_widget.delete(marker)
                for poly in buff:
                    self.map_widget.delete(poly)
                break

    def delete_line(self, coords):
        for poly in self.map_widget.canvas_polygon_list:
            a = poly.get_canvas_pos(poly.position_list[0], self.root.winfo_width()*0.7, self.root.winfo_height())
            b = poly.get_canvas_pos(poly.position_list[1], self.root.winfo_width()*0.7, self.root.winfo_height())
            c = poly.get_canvas_pos(coords, self.root.winfo_width()*0.7, self.root.winfo_height())
            if abs(math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2) - 
                   (math.sqrt((a[0] - c[0])**2 + (a[1] - c[1])**2) + math.sqrt((b[0] - c[0])**2 + (b[1] - c[1])**2))) < 0.4:
                   self.gr.remove_edge(poly.data)
                   self.map_widget.delete(poly)

    def properties(self, object_name):
        width=self.root.winfo_width()*0.7
        
        self.close_properties()

        _name = object_name
        _object = self.gr.get_vertex(_name)
        match _name[:4]:
            case 'Sour': #источник водоснабжения
                _type = 'Источник'
                list_props_name = ['Высота объекта, м', 'Расход воды, м3/час', 
                                   'Максимальный расход, м3/час', 'Напор на выходе, м', ]
            case 'Wate': #водонапорная башня
                _type = 'Водонапорная башня'
                list_props_name = ['Высота объекта, м', 'Расход воды, м3/час',
                                   'Высота воды, м', 'Объем запаса воды, м3', 
                                   'Напор, м']
            case 'Coun': #контррезервуар
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
        
        for i in range (len(list_props_name)):          
            self.props_name[i].config(text= list_props_name[i])
            self.props_name[i].place(x=width+15, y=120+i*20)
            self.props_value[i].insert(0, str(_object[3][i]))
            self.props_value[i].place(x=width+200, y=120+i*20) 

        self.save_button.config(command= self.save_properties)
        self.cancel_button.place(x= self.root.winfo_width()-300, y= self.root.winfo_height()-50)
        self.save_button.place(x= self.root.winfo_width()-200, y= self.root.winfo_height()-50)
    
    def properties_line(self, object_name):
        width=self.root.winfo_width()*0.7
        
        self.close_properties()

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
        self.coordinates.config(text = 'Конечные точки: ' + str(_object[1]) + " -- " + str(_object[2]))
        self.type.place( x=width+15, y=30)
        self.name.place( x=width+15, y=50)
        self.coordinates.place( x=width+15, y=70)
        
        for i in range (len(list_props_name)):          
            self.props_name[i].config(text= list_props_name[i]) 
            self.props_value[i].insert(0, str(_object[3][i]))
            self.props_name[i].place( x=width+15, y=120+i*20)  
            self.props_value[i].place( x=width+200, y=120+i*20) 
        last_posy = 120+len(list_props_name)*20
        
        self.props_name[11].config(text= 'Материал трубы')
        self.props_name[11].place( x=width+15, y=last_posy+20) 
        self.material.current(self.material_list.index(_object[3][11]))
        self.material.place(x=width+200, y=last_posy+20) 
        self.props_name[12].config(text= 'Наличие запорной арматуры')
        self.props_name[12].place( x=width+15, y=last_posy+40)
        self.has_valve.current(_object[3][12]) 
        self.has_valve.place(x=width+200, y=last_posy+40)
        self.props_name[13].config(text= 'Процент открытия')
        self.props_name[13].place( x=width+15, y=last_posy+60) 
        self.opened_valve.insert(0, str(_object[3][13]))
        self.opened_valve.place(x=width+200, y=last_posy+60)

        self.save_button.config(command= self.save_properties_line)
        self.cancel_button.place(x= self.root.winfo_width()-300, y= self.root.winfo_height()-50)
        self.save_button.place(x= self.root.winfo_width()-200, y= self.root.winfo_height()-50)

    def save_properties(self):
        name = self.name.cget("text")
        coords = self.coordinates.cget("text")[12:].split(' -- ')
        value = []
        match name[:4]:
            case 'Sour': 
                n_values = 4
            case 'Wate': 
                n_values = 5
            case 'Coun': 
                n_values = 4
            case 'Conn': 
                n_values = 4
            case 'Cons': 
                n_values = 4

        for i in range(n_values):
            value.append(float(self.props_value[i].get()))
        self.gr.update_vertex(name,float(coords[0]),float(coords[1]),tuple(value))

        print(self.gr.get_all_vertexes())
    
    def save_properties_line(self):
        name = self.name.cget("text")
        points = self.coordinates.cget("text")[16:].split(' -- ')
        value = []
        for i in range (11):
            value.append(float(self.props_value[i].get()))
        if self.has_valve.get() == 'нет':
            state = 0
        else:
            state = 1
        value.append(self.material.get())
        value.append(state)
        value.append(float(self.opened_valve.get()))
        self.gr.update_edge(name,points[0],points[1],tuple(value))

        print(self.gr.get_all_edges())

    def close_properties(self):
        self.type.place_forget()
        self.name.place_forget()
        self.coordinates.place_forget()
        for item in self.props_name:
            item.place_forget()
        for item in self.props_value:
            item.place_forget()
            item.delete(0,END)
        self.save_button.place_forget()
        self.cancel_button.place_forget()
        self.has_valve.place_forget() 
        self.material.place_forget() 
        self.opened_valve.place_forget() 
        self.opened_valve.delete(0,END)   
        
    def open_new_map(self, pos=(55.010159, 82.925716), zoom = 10, path_state = 0):
        self.gr.clear_graph()
        self.close_properties()
        if not path_state:
            self.path_to_file = ''
        self.last_N_of_object = [0, 0, 0, 0, 0, 0]
        self.has_valve.current(0)
        self.material.current(0)
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
        self.map_widget.add_right_click_menu_command_markers(label="Удалить объект", 
                                command=self.delete_marker,
                                pass_coords=True 
                                )
        self.map_widget.add_right_click_menu_command_markers(label="Свойства", 
                                command=self.properties,
                                pass_coords=False 
                                )
        self.map_widget.add_right_click_menu_command_lines(label="Удалить участок", 
                                command=self.delete_line,
                                pass_coords=True 
                                )
        self.map_widget.add_right_click_menu_command_lines(label="Свойства", 
                                command=self.properties_line,
                                pass_coords=False 
                                )

        
        self.map_widget.save_state_to_file
    
    def load(self):
        self.last_N_of_object = [0, 0, 0, 0, 0, 0]
        self.path_to_file = filedialog.askopenfilename(defaultextension=".txt",
                    filetypes=[("database",".db")],
                    initialdir="./schemas")
        if self.path_to_file != '':
            cx = sqlite3.connect(self.path_to_file)
            cu = cx.cursor()
            
            cu.execute("SELECT * FROM map;")
            out = cu.fetchall()
            self.open_new_map((out[0][1], out[0][2]), out[0][3], 1)
            
            cu.execute("SELECT * FROM sources;")
            out = cu.fetchall()
            for row in out:
                self.map_widget.set_marker(row[1], row[2], text = "ИСТ " + str(TKmv.convert_coordinates_to_address(row[1], row[2]).street) + 
                                                        " " + str(TKmv.convert_coordinates_to_address(row[1], row[2]).housenumber),
                                                        icon="icons/source.png", data = row[0])
                self.gr.add_vertex(row[0], row[1], row[2], (row[3], row[4], row[5], row[6]))
            if len(out)!=0:
                self.last_N_of_object[0]=int(row[0][6:])
            
            cu.execute("SELECT * FROM towers;")
            out = cu.fetchall()
            for row in out:
                self.map_widget.set_marker(row[1], row[2], text = "ВНБ " + str(TKmv.convert_coordinates_to_address(row[1], row[2]).street) + 
                                                        " " + str(TKmv.convert_coordinates_to_address(row[1], row[2]).housenumber),
                                                        icon="icons/tower.png", data = row[0])
                self.gr.add_vertex(row[0], row[1], row[2], (row[3], row[4], row[5], row[6], row[7]))
            if len(out)!=0:    
                self.last_N_of_object[1]=int(row[0][10:])
            
            cu.execute("SELECT * FROM reservoirs;")
            out = cu.fetchall()
            for row in out:
                self.map_widget.set_marker(row[1], row[2], text = "КР " + str(TKmv.convert_coordinates_to_address(row[1], row[2]).street) + 
                                                        " " + str(TKmv.convert_coordinates_to_address(row[1], row[2]).housenumber),
                                                        icon="icons/reservoir.png", data = row[0])
                self.gr.add_vertex(row[0], row[1], row[2], (row[3], row[4], row[5], row[6]))
            if len(out)!=0:
                self.last_N_of_object[2]=int(row[0][16:])
            
            cu.execute("SELECT * FROM connectors;")
            out = cu.fetchall()
            for row in out:
                self.map_widget.set_marker(row[1], row[2], text = "РЗВ " + str(TKmv.convert_coordinates_to_address(row[1], row[2]).street) + 
                                                        " " + str(TKmv.convert_coordinates_to_address(row[1], row[2]).housenumber),
                                                        icon="icons/connector.png", data = row[0])
                self.gr.add_vertex(row[0], row[1], row[2], (row[3], row[4], row[5], row[6]))
            if len(out)!=0:
                self.last_N_of_object[3]=int(row[0][9:])

            cu.execute("SELECT * FROM consumers;")
            out = cu.fetchall()
            for row in out:
                self.map_widget.set_marker(row[1], row[2], text = "ПТР " + str(TKmv.convert_coordinates_to_address(row[1], row[2]).street) + 
                                                        " " + str(TKmv.convert_coordinates_to_address(row[1], row[2]).housenumber),
                                                        icon="icons/consumer.png", data = row[0])
                self.gr.add_vertex(row[0], row[1], row[2], (row[3], row[4], row[5], row[6]))
            if len(out)!=0:
                self.last_N_of_object[4]=int(row[0][8:])
            
            cu.execute("SELECT * FROM pipes;")
            out = cu.fetchall()
            for row in out:
                point1 = self.gr.get_vertex(row[1])
                point2 = self.gr.get_vertex(row[2])
                #получаем координаты концов участка
                buff = [(point1[1], point1[2]), (point2[1], point2[2])]
                self.map_widget.set_polygon(buff, data=row[0])
                
                self.gr.add_edge(row[0], row[1], row[2], (row[3],row[4],row[5],row[6],
                                                        row[7],row[8],row[9],row[10],
                                                        row[11],row[12],row[13],row[14],
                                                        row[15],row[16]))
                if len(out)!=0:
                    self.last_N_of_object[5]=int(row[0][4:])
            cx.commit()
            cx.close()
        
    def save(self):
        self.close_properties()
        if self.path_to_file =='':
            self.save_as()
        else:
            try:
                self.clear_db(self.path_to_file)
            except:
                pass
            cx = sqlite3.connect(self.path_to_file)
            cu = cx.cursor()
            pos = self.map_widget.convert_canvas_coords_to_decimal_coords(self.map_widget.width / 2, self.map_widget.height / 2)
            
            cu.execute("INSERT OR REPLACE INTO map (pos1, pos2, zoom) VALUES (?, ?, ?);", (pos[0], pos[1], self.map_widget.zoom))

            for item in self.gr.get_all_vertexes():
                if item[0][:4] == "Sour":
                    print("src")
                    cu.execute("INSERT OR REPLACE INTO sources (name, coord1, coord2, H, G, Gmax, P) VALUES (?, ?, ?, ?, ?, ?, ?);", 
                            (item[0], float(item[1]), float(item[2]), float(item[3][0]), 
                                        float(item[3][1]), float(item[3][2]), float(item[3][3])))     
                if item[0][:4] == "Wate":
                    print("twr")
                    cu.execute("INSERT OR REPLACE INTO towers (name, coord1, coord2, H, G, Hwater, V, P) VALUES (?, ?, ?, ?, ?, ?, ?, ?);", 
                            (item[0], float(item[1]), float(item[2]), float(item[3][0]), 
                                        float(item[3][1]), float(item[3][2]), float(item[3][3]), float(item[3][4])))  
                if item[0][:4] == "Coun":
                    print("res")
                    cu.execute("INSERT OR REPLACE INTO reservoirs (name, coord1, coord2, H, G, Hwater, P) VALUES (?, ?, ?, ?, ?, ?, ?);", 
                            (item[0], float(item[1]), float(item[2]), float(item[3][0]), 
                                        float(item[3][1]), float(item[3][2]), float(item[3][3])))   
                if item[0][:4] == "Conn":
                    print("cnn")
                    cu.execute("INSERT OR REPLACE INTO connectors (name, coord1, coord2, H, G, P, Pressure) VALUES (?, ?, ?, ?, ?, ?, ?);", 
                            (item[0], float(item[1]), float(item[2]), float(item[3][0]), 
                                        float(item[3][1]), float(item[3][2]), float(item[3][3])))  
                if item[0][:4] == "Cons":
                    print("cns")
                    cu.execute("INSERT OR REPLACE INTO consumers (name, coord1, coord2, H, G, Pmin, P) VALUES (?, ?, ?, ?, ?, ?, ?);", 
                            (item[0], float(item[1]), float(item[2]), float(item[3][0]), 
                                        float(item[3][1]), float(item[3][2]), float(item[3][3])))  
            for item in self.gr.get_all_edges():
                print("pip")
                cu.execute("INSERT OR REPLACE INTO pipes (name, name1, name2, H1, H2, D, Len, G, R, Glost, Speed, Lambda, Lost,\
                        AcceptPres, Material, hasValve, opened) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", 
                        (item[0], item[1], item[2], float(item[3][0]), float(item[3][1]), float(item[3][2]), float(item[3][3]), 
                                                    float(item[3][4]), float(item[3][5]), float(item[3][6]), float(item[3][7]), 
                                                    float(item[3][8]), float(item[3][9]), float(item[3][10]), item[3][11], 
                                                    float(item[3][12]), float(item[3][13])))
            cx.commit()
            cx.close()

    
    def save_as(self):
        self.path_to_file = filedialog.asksaveasfilename(defaultextension=".txt",
                filetypes=[("database",".db")],
                initialdir="./schemas")
        if self.path_to_file != '':
            self.create_db(self.path_to_file)
            self.save()

    def __init__(self):
        #source, watertower, counterreservoir, consumer, connector, pipe
        self.last_N_of_object = [0, 0, 0, 0, 0, 0]
        self.path_to_file = ''
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
        self.props_name = [ttk.Label() for i in range(14)]
        self.props_value = [ttk.Entry(width=25) for i in range(11)] 
        self.save_button = ttk.Button(text='Сохранить')
        self.cancel_button = ttk.Button(text='Отмена', command= self.close_properties)
        self.has_valve_list = ['нет','да']
        self.has_valve = ttk.Combobox(values=self.has_valve_list, state= "readonly") #наличие запороной арматуры
        self.material_list = ['металл','пластик']
        self.material = ttk.Combobox(values=self.material_list, state= "readonly") #материал трубы участка
        self.opened_valve = ttk.Entry(width=15) #процент открытия арматуры    
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
        self.filemenu.add_command(label="Сохранить как...",
                  command=self.save_as)
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
