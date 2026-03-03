#!/usr/bin/env python3
# =============================================================================
# NAVE ESPACIAL DFD-XL MECÁNICA - PROTOTIPO CNC/IMPRESIÓN 3D
# =============================================================================
# Modelo paramétrico para fabricación CNC e impresión 3D
# Sistema de paneles solares retráctiles con enfriamiento
# Antenas de alta ganancia, sensores de navegación solar
# Truss estructural con interfaces CNC
# Base de montaje con agujeros para fijaciones
# Escudos TPS multilayer avanzados
# Blindajes, radiadores en sombra, tanques, sensores y tren de aterrizaje
# Unidades: mm (milímetros)
# =============================================================================

import FreeCAD as App
import Part
import math

# =============================================================================
# CLASES Y FUNCIONES AUXILIARES
# =============================================================================

class SpacecraftPart:
    """Clase base para partes de la nave espacial"""
    
    def __init__(self, name):
        self.name = name
        self.shape = None
        self.parts = []
    
    def create(self):
        """Método para crear la forma - implementado en subclases"""
        pass
    
    def get_shape(self):
        """Retorna la forma creada"""
        return self.shape
    
    def add_to_doc(self, doc):
        """Añade el objeto al documento FreeCAD"""
        if self.shape:
            obj = doc.addObject("Part::Feature", self.name)
            obj.Shape = self.shape
            return obj
        return None


class ParametricSpacecraft:
    """
    Clase principal paramétrica para generar la nave espacial
    con todas las características mecánicas para CNC/impresión 3D
    """
    
    def __init__(self):
        self.doc = App.newDocument("Nave_DFD_XL_Mechanical")
        self.parts = {}
        
        # =========================================================================
        # PARÁMETROS PRINCIPALES - Configuración dimensional
        # =========================================================================
        self.P = {
            # Escala general
            'scale': 1.0,
            
            # ---------------------------------------------------------------
            # FUSELAJE PRINCIPAL - Estilo DFD (Dropped Flat)
            # ---------------------------------------------------------------
            'nose_len': 1500.0,      # Longitud del morro
            'nose_base_d': 1100.0,   # Diámetro base del morro
            'mid_len': 3000.0,       # Longitud sección media
            'mid_d': 1800.0,         # Diámetro sección media
            'rear_len': 1500.0,      # Longitud trasera
            'rear_d': 2200.0,        # Diámetro trasero
            'hull_t': 30.0,          # Espesor del casco
            
            # ---------------------------------------------------------------
            # ESCUDO TÉRMICO FRONTAL MULTILAYER (TPS - Thermal Protection System)
            # ---------------------------------------------------------------
            'shield_d': 2600.0,      # Diámetro del escudo
            'shield_flecha': 80.0,   # Flecha/abombamiento frontal
            't_ceramic': 4.0,        # Espesor capa cerámica (LI-900)
            't_foam': 120.0,         # Espesor foam aislante (LI-2200)
            't_cc': 12.0,            # Espesor carbono-carbono trasero
            'rim_w': 60.0,           # Ancho del reborde perimetral
            'rim_h': 80.0,           # Altura del reborde
            
            # ---------------------------------------------------------------
            # BLINDAJES TPS - Mangas alrededor del fuselaje y reactor
            # ---------------------------------------------------------------
            'hull_shield_t': 80.0,   # Espesor blindaje casco
            'hull_shield_l': 2800.0, # Longitud blindaje casco
            'reactor_shield_t': 120.0, # Espesor blindaje reactor
            'reactor_shield_l': 2200.0, # Longitud blindaje reactor
            
            # ---------------------------------------------------------------
            # REACTOR Y SISTEMA DE PROPULSIÓN
            # ---------------------------------------------------------------
            'reactor_d': 1500.0,     # Diámetro del reactor
            'reactor_l': 1800.0,     # Longitud del reactor
            'nozzle_l': 1000.0,      # Longitud de la boquilla
            'nozzle_exit_d': 2200.0, # Diámetro de salida de boquilla
            
            # ---------------------------------------------------------------
            # MÓDULO HÁBITAT Y CABINA
            # ---------------------------------------------------------------
            'hab_d': 1400.0,         # Diámetro del hábitat
            'hab_l': 2500.0,         # Longitud del hábitat
            'cockpit_d': 900.0,      # Diámetro de la cabina
            'cockpit_l': 800.0,      # Longitud de la cabina
            'window_r': 150.0,       # Radio de la ventana
            
            # ---------------------------------------------------------------
            # TANQUES DE COMBUSTIBLE
            # ---------------------------------------------------------------
            'tank_r': 400.0,         # Radio tanques laterales
            'tank_l': 2000.0,        # Longitud tanques
            'tank_off': 1200.0,      # Offset lateral tanques
            'sphere_r': 450.0,       # Radio tanques esféricos
            'sphere_off': 1600.0,    # Offset tanques esféricos
            
            # ---------------------------------------------------------------
            # RADIADORES EN SOMBRA (Shadow Radiators)
            # ---------------------------------------------------------------
            'wing_span': 2500.0,     # Envergadura radiadores
            'wing_th': 60.0,         # Espesor radiadores
            'wing_l': 2200.0,        # Longitud radiadores
            'wing_back_offset': 1200.0, # Offset hacia atrás
            
            # ---------------------------------------------------------------
            # SISTEMA DE CONTROL TÉRMICO - Collar y deflectores
            # ---------------------------------------------------------------
            'collar_d_delta': 300.0, # Incremento diámetro collar
            'collar_h': 120.0,       # Altura del collar
            'collar_t': 40.0,        # Espesor del collar
            'def_count': 8,          # Número de deflectores
            'def_l': 800.0,          # Longitud deflectores
            'def_w': 160.0,          # Ancho deflectores
            'def_t': 30.0,           # Espesor deflectores
            
            # ---------------------------------------------------------------
            # ANTENAS
            # ---------------------------------------------------------------
            'mast_l': 1000.0,        # Longitud mástil antenas
            'mast_r': 40.0,          # Radio mástil
            'dish_r': 400.0,         # Radio plato parabólico
            'hg_antenna_dish_r': 600.0, # Radio antena alta ganancia
            'hg_antenna_mast_l': 1500.0, # Longitud mástil HG
            
            # ---------------------------------------------------------------
            # TREN DE ATERRIZAJE
            # ---------------------------------------------------------------
            'leg_r': 100.0,          # Radio pata
            'leg_l': 800.0,          # Longitud pata
            'foot_r': 250.0,         # Radio pie/patín
            'foot_t': 50.0,          # Espesor pie
            'retractable': True,     # Tren retráctil
            
            # ---------------------------------------------------------------
            # PUERTOS DE ACOPLAMIENTOS Y ESCOTILLAS
            # ---------------------------------------------------------------
            'dock_r': 400.0,         # Radio puerto acoplamiento
            'dock_l': 300.0,         # Longitud puerto
            'dock_off': 800.0,       # Offset puerto
            
            # ---------------------------------------------------------------
            # SENSORES EXTERNOS
            # ---------------------------------------------------------------
            'sensor_r': 50.0,        # Radio sensores
            'sensor_l': 200.0,       # Longitud sensores
            
            # ---------------------------------------------------------------
            # REFUERZOS INTERNOS
            # ---------------------------------------------------------------
            'beam_r': 50.0,          # Radio refuerzos
            'beam_l': 3000.0,        # Longitud refuerzos
            
            # ---------------------------------------------------------------
            # PANELES SOLARES RETRÁCTILES CON ENFRIAMIENTO
            # ---------------------------------------------------------------
            'panel_l': 3000.0,       # Longitud panel
            'panel_w': 1500.0,       # Ancho panel
            'panel_th': 20.0,       # Espesor panel
            'panel_count': 4,        # Número de paneles
            'boom_r': 50.0,          # Radio mástil extensores
            'boom_l': 4000.0,        # Longitud mástil
            'cooling_tube_r': 10.0, # Radio tubos enfriamiento
            'cooling_channels': 8,   # Canales de refrigeración
            'retraction_angle': 30.0, # Ángulo de retracción
            
            # ---------------------------------------------------------------
            # INSTRUMENTOS CIENTÍFICOS
            # ---------------------------------------------------------------
            'fields_boom_l': 5000.0, # Longitud boom FIELDS
            'fields_boom_r': 30.0,   # Radio boom FIELDS
            'fields_sensor_r': 100.0, # Radio sensor FIELDS
            'sweap_sensor_r': 80.0,  # Radio sensor SWEAP
            'isis_sensor_r': 70.0,   # Radio sensor ISIS
            'wispr_camera_r': 60.0,  # Radio cámara WISPR
            
            # ---------------------------------------------------------------
            # SENSORES DE NAVEGACIÓN SOLAR
            # ---------------------------------------------------------------
            'nav_sensor_r': 40.0,    # Radio sensores navegación
            'nav_sensor_count': 6,   # Número de sensores
            'sun_sensor_fov': 60.0,  # Campo de vista sensores
            
            # ---------------------------------------------------------------
            # TRUSS ESTRUCTURAL CON INTERFACES CNC
            # ---------------------------------------------------------------
            'truss_beam_r': 80.0,   # Radio vigas truss
            'truss_beam_l': 6000.0, # Longitud vigas truss
            'truss_count': 8,        # Número de vigas
            'truss_node_r': 120.0,  # Radio nodos conexión
            'truss_cross bracing': True, # Riostras cruzadas
            
            # ---------------------------------------------------------------
            # BASE DE MONTAJE CON AGUJEROS PARA FIJACIONES
            # ---------------------------------------------------------------
            'base_d': 3000.0,        # Diámetro base
            'base_h': 200.0,         # Altura base
            'base_rim_t': 30.0,      # Espesor reborde base
            
            # ---------------------------------------------------------------
            # CARACTERÍSTICAS CNC - Agujeros, roscas, fijaciones
            # ---------------------------------------------------------------
            'bolt_d': 20.0,          # Diámetro perno
            'bolt_head_d': 30.0,     # Diámetro cabeza perno
            'bolt_head_h': 10.0,     # Altura cabeza perno
            'bolt_count': 12,        # Número de pernos
            'thread_pitch': 2.0,     # Paso de rosca (mm)
            'interface_holes_d': 50.0, # Diámetro agujeros interfaz
            'interface_holes_count': 8, # Agujeros por viga
            'clearance': 0.5,        # Tolerancia de clearance (mm)
            'tolerance': 0.2,        # Tolerancia general (mm)
            
            # ---------------------------------------------------------------
            # ESCUDOS MULTILAYER ADICIONALES
            # ---------------------------------------------------------------
            'mli_layers': 15,        # Capas MLI (Multi-Layer Insulation)
            'mli_spacing': 0.5,      # Espaciamiento capas
            'radiator_area': 15.0,   # Área radiadores (m²)
            
            # ---------------------------------------------------------------
            # SISTEMA DE ENFRIAMIENTO ACTIVO
            # ---------------------------------------------------------------
            'cooling_pump_r': 150.0, # Radio bomba refrigerante
            'cooling_pipes': 6,      # Número de tuberías
            'heat_exchanger_r': 200.0, # Radio intercambiador
            
            # ---------------------------------------------------------------
            # TOLERANCIAS DE FABRICACIÓN
            # ---------------------------------------------------------------
            'overlap': 2.0,          # Solape para fusión robusta
            'print_tolerance': 0.3,  # Tolerancia impresión 3D
            'cnc_tolerance': 0.05,   # Tolerancia CNC
        }
    
    def add_object(self, shape, name):
        """Añade una forma al documento"""
        if shape:
            obj = self.doc.addObject("Part::Feature", name)
            obj.Shape = shape
            self.parts[name] = obj
            return obj
        return None
    
    def create_hull(self):
        """Crea el fuselaje principal de la nave"""
        P = self.P
        
        # Morro cónico
        nose = Part.makeCone(0, P['nose_base_d']/2, P['nose_len'])
        
        # Sección media cilíndrica
        mid = Part.makeCylinder(P['mid_d']/2, P['mid_len'])
        mid.translate(App.Vector(0, 0, P['nose_len']))
        
        # Sección trasera cónica
        rear = Part.makeCone(P['rear_d']/2, P['mid_d']/2, P['rear_len'])
        rear.translate(App.Vector(0, 0, P['nose_len'] + P['mid_len']))
        
        # Unión del fuselaje
        hull = nose.fuse(mid).fuse(rear)
        
        # Añadir al documento
        self.add_object(hull, "01_Hull_Main")
        
        return hull
    
    def create_thermal_shield(self):
        """Crea el escudo térmico frontal multilayer (TPS)"""
        P = self.P
        shield_R = P['shield_d'] / 2.0
        
        # --- Capa 1: Cerámica frontal (LI-900) ---
        # Disco base
        ceramic = Part.makeCylinder(shield_R, P['t_ceramic'])
        # Proyección cónica (flecha)
        cone = Part.makeCone(shield_R, shield_R - 40.0, P['shield_flecha'])
        cone.translate(App.Vector(0, 0, -P['shield_flecha']))
        ceramic_layer = ceramic.fuse(cone)
        
        # --- Capa 2: Foam aislante (LI-2200) ---
        foam = Part.makeCylinder(shield_R - P['overlap'], P['t_foam'])
        foam.translate(App.Vector(0, 0, P['t_ceramic'] - P['overlap']))
        
        # --- Capa 3: Carbón-Carbono trasero ---
        cc_back = Part.makeCylinder(shield_R - 2*P['overlap'], P['t_cc'])
        cc_back.translate(App.Vector(0, 0, P['t_ceramic'] + P['t_foam'] - 2*P['overlap']))
        
        # --- Reborde perimetral ---
        rim_outer = Part.makeCylinder(shield_R, P['rim_h'])
        rim_inner = Part.makeCylinder(shield_R - P['rim_w'], P['rim_h'])
        rim = rim_outer.cut(rim_inner)
        rim.translate(App.Vector(0, 0, P['t_ceramic'] + P['t_foam'] + P['t_cc'] - P['rim_h']))
        
        # --- Ensamble completo del escudo ---
        shield = ceramic_layer.fuse(foam).fuse(cc_back).fuse(rim)
        # Posicionar delante del fuselaje
        total_depth = P['t_ceramic'] + P['t_foam'] + P['t_cc']
        shield.translate(App.Vector(0, 0, -total_depth))
        
        self.add_object(shield, "02_TPS_Front_Shield")
        
        # --- Crear tapa protectora separable ---
        cap = Part.makeCylinder(shield_R * 0.9, 50)
        cap.translate(App.Vector(0, 0, -total_depth - 50))
        self.add_object(cap, "02a_TPS_Cap")
        
        return shield
    
    def create_hull_shields(self):
        """Crea los blindajes TPS alrededor del fuselaje y reactor"""
        P = self.P
        
        # --- Blindaje del casco (sección media) ---
        hull_shield = Part.makeCylinder(
            P['mid_d']/2 + P['hull_shield_t'], 
            P['hull_shield_l']
        )
        hull_shield.translate(App.Vector(
            0, 0, 
            P['nose_len'] + (P['mid_len'] - P['hull_shield_l'])/2.0
        ))
        
        # Añadir anillos de refuerzo
        ring_count = 4
        for i in range(ring_count):
            z = P['nose_len'] + (P['mid_len'] / (ring_count + 1)) * (i + 1)
            ring = Part.makeTorus(
                P['mid_d']/2 + P['hull_shield_t'] + 20,
                20
            )
            ring.translate(App.Vector(0, 0, z))
            hull_shield = hull_shield.fuse(ring)
        
        self.add_object(hull_shield, "03_Hull_TPS_Shield")
        
        # --- Blindaje del reactor ---
        reactor_shield = Part.makeCylinder(
            P['reactor_d']/2 + P['reactor_shield_t'],
            P['reactor_shield_l']
        )
        reactor_shield.translate(App.Vector(
            0, 0,
            P['nose_len'] + P['mid_len'] - 200.0
        ))
        
        # Añadir aletas de refrigeración
        fin_count = 12
        for i in range(fin_count):
            angle = i * (360.0 / fin_count)
            fin = Part.makeBox(
                P['reactor_shield_t'] * 2,
                P['reactor_shield_l'] / 20,
                P['reactor_shield_l']
            )
            rad = P['reactor_d']/2 + P['reactor_shield_t']
            fin.Placement = App.Placement(
                App.Vector(rad * math.cos(math.radians(angle)),
                          rad * math.sin(math.radians(angle)),
                          P['nose_len'] + P['mid_len'] - 200.0),
                App.Rotation(App.Vector(0, 0, 1), angle)
            )
            reactor_shield = reactor_shield.fuse(fin)
        
        self.add_object(reactor_shield, "04_Reactor_TPS_Shield")
        
        return hull_shield, reactor_shield
    
    def create_reactor(self):
        """Crea el reactor nuclear y el sistema de propulsión"""
        P = self.P
        
        # --- Reactor principal ---
        reactor = Part.makeCylinder(P['reactor_d']/2, P['reactor_l'])
        reactor.translate(App.Vector(0, 0, P['nose_len'] + 1200))
        
        # Boquilla de expansión
        nozzle = Part.makeCone(
            P['rear_d']/2,
            P['nozzle_exit_d']/2,
            P['nozzle_l']
        )
        nozzle.translate(App.Vector(
            0, 0,
            P['nose_len'] + P['mid_len'] + P['rear_len']
        ))
        
        # Ensamble del reactor
        reactor_full = reactor.fuse(nozzle)
        
        # Añadir núcleo interno (representación)
        core = Part.makeCylinder(P['reactor_d']/3, P['reactor_l'] * 0.8)
        core.translate(App.Vector(0, 0, P['nose_len'] + 1200))
        
        self.add_object(reactor, "05_Reactor_Core")
        self.add_object(nozzle, "06_Reactor_Nozzle")
        
        return reactor_full
    
    def create_cockpit_habitat(self):
        """Crea la cabina de mando y el módulo hábitat"""
        P = self.P
        
        # --- Cabina de mando ---
        cockpit = Part.makeCylinder(P['cockpit_d']/2, P['cockpit_l'])
        cockpit.translate(App.Vector(0, 0, 50))
        
        # Ventana (restar esfera)
        window = Part.makeSphere(P['window_r'])
        window.translate(App.Vector(P['cockpit_d']/3, 0, P['cockpit_l']/2))
        cockpit_cut = cockpit.cut(window)
        
        # Marco de ventana
        frame_outer = Part.makeTorus(P['window_r'] + 20, 15)
        frame_outer.translate(App.Vector(P['cockpit_d']/3, 0, P['cockpit_l']/2))
        frame_outer.rotate(
            App.Vector(P['cockpit_d']/3, 0, P['cockpit_l']/2),
            App.Vector(1, 0, 0),
            90
        )
        
        cockpit_final = cockpit_cut.fuse(frame_outer)
        self.add_object(cockpit_final, "07_Cockpit")
        
        # --- Módulo hábitat ---
        hab = Part.makeCylinder(P['hab_d']/2, P['hab_l'])
        hab.translate(App.Vector(0, 0, P['nose_len'] + P['mid_len'] + 500))
        
        # Anillos de presión
        ring_positions = [0, P['hab_l']/4, P['hab_l']/2, 3*P['hab_l']/4, P['hab_l']]
        for z_offset in ring_positions:
            ring = Part.makeTorus(P['hab_d']/2 + 10, 15)
            ring.translate(App.Vector(0, 0, P['nose_len'] + P['mid_len'] + 500 + z_offset))
            hab = hab.fuse(ring)
        
        self.add_object(hab, "08_Habitat_Module")
        
        return cockpit_final, hab
    
    def create_fuel_tanks(self):
        """Crea los tanques de combustible"""
        P = self.P
        
        # --- Tanques laterales cilíndricos ---
        tankL = Part.makeCylinder(P['tank_r'], P['tank_l'])
        tankL.translate(App.Vector(P['tank_off'], 0, P['nose_len'] + 1000))
        
        tankR = Part.makeCylinder(P['tank_r'], P['tank_l'])
        tankR.translate(App.Vector(-P['tank_off'], 0, P['nose_len'] + 1000))
        
        # --- Tanques esféricos ---
        sphereL = Part.makeSphere(P['sphere_r'])
        sphereL.translate(App.Vector(P['sphere_off'], 0, P['nose_len'] + 2500))
        
        sphereR = Part.makeSphere(P['sphere_r'])
        sphereR.translate(App.Vector(-P['sphere_off'], 0, P['nose_len'] + 2500))
        
        # Conectar tanques con tuberías
        pipes = []
        for i, (t1_z, t2_z) in enumerate([(1000, 2500), (-1000, 2500)]):
            for side in [1, -1]:
                pipe = Part.makeCylinder(50, abs(t2_z - t1_z))
                pipe.translate(App.Vector(
                    side * (P['tank_off'] if i == 0 else P['sphere_off']),
                    0,
                    P['nose_len'] + (t1_z + t2_z) / 2
                ))
                pipes.append(pipe)
        
        tanks = tankL.fuse(tankR).fuse(sphereL).fuse(sphereR)
        for pipe in pipes:
            tanks = tanks.fuse(pipe)
        
        self.add_object(tankL, "09_Tank_Left")
        self.add_object(tankR, "10_Tank_Right")
        self.add_object(sphereL, "11_Tank_Sphere_Left")
        self.add_object(sphereR, "12_Tank_Sphere_Right")
        
        return tanks
    
    def create_radiators(self):
        """Crea los radiadores en sombra"""
        P = self.P
        
        # --- Paneles radiadores ---
        wingL = Part.makeBox(P['wing_span'], P['wing_th'], P['wing_l'])
        wingL.translate(App.Vector(
            -P['wing_span']/2,
            -P['mid_d']/2 - 150,
            P['nose_len'] + P['mid_len'] + P['wing_back_offset']
        ))
        
        wingR = Part.makeBox(P['wing_span'], P['wing_th'], P['wing_l'])
        wingR.translate(App.Vector(
            -P['wing_span']/2,
            P['mid_d']/2 + 150,
            P['nose_len'] + P['mid_len'] + P['wing_back_offset']
        ))
        
        # Añadir aletas de disipación
        for wing in [wingL, wingR]:
            fin_count = 20
            for i in range(fin_count):
                z = P['nose_len'] + P['mid_len'] + P['wing_back_offset'] + (i - fin_count/2) * (P['wing_l'] / fin_count)
                fin = Part.makeBox(P['wing_span']/10, P['wing_th']*2, 5)
                fin.translate(App.Vector(0, wing.BoundBox.YMin - 10, z))
                wing = wing.fuse(fin)
        
        wings = wingL.fuse(wingR)
        
        self.add_object(wingL, "13_Radiator_Left")
        self.add_object(wingR, "14_Radiator_Right")
        
        return wings
    
    def create_thermal_collar(self):
        """Crea el collar térmico y los deflectores"""
        P = self.P
        
        # --- Collar térmico ---
        collarOD = P['mid_d'] + P['collar_d_delta']
        collar = Part.makeCylinder(collarOD/2.0, P['collar_h'])
        collar_inner = Part.makeCylinder(collarOD/2.0 - P['collar_t'], P['collar_h'])
        collar = collar.cut(collar_inner)
        
        collar.translate(App.Vector(
            0, 0,
            P['nose_len'] + P['mid_len']/2.0 - P['collar_h']/2.0
        ))
        
        self.add_object(collar, "15_Thermal_Collar")
        
        # --- Deflectores ---
        deflectors = []
        for i in range(P['def_count']):
            angle = i * (360.0 / P['def_count'])
            
            # Placa deflectora
            d = Part.makeBox(P['def_l'], P['def_w'], P['def_t'])
            d.translate(App.Vector(-P['def_l']/2.0, -P['def_w']/2.0, 0))
            
            # Rotar y posicionar
            baseR = collarOD/2.0 + P['overlap']
            center = App.Vector(baseR * math.cos(math.radians(angle)),
                              baseR * math.sin(math.radians(angle)),
                              P['nose_len'] + P['mid_len']/2.0 - P['def_t']/2.0)
            
            d.Placement = App.Placement(
                center,
                App.Rotation(App.Vector(0, 0, 1), angle)
            )
            deflectors.append(d)
        
        deflectores = deflectors[0]
        for d in deflectors[1:]:
            deflectores = deflectores.fuse(d)
        
        self.add_object(deflectores, "16_Deflectors")
        
        return collar, deflectores
    
    def create_solar_panels(self):
        """Crea los paneles solares retráctiles con sistema de enfriamiento"""
        P = self.P
        
        all_panels = []
        
        for i in range(P['panel_count']):
            angle = i * (360.0 / P['panel_count'])
            rad_angle = math.radians(angle)
            
            # --- Mástil/extensor ---
            boom = Part.makeCylinder(P['boom_r'], P['boom_l'])
            boom_center = App.Vector(
                P['mid_d']/2 * math.cos(rad_angle),
                P['mid_d']/2 * math.sin(rad_angle),
                P['nose_len'] + P['mid_len'] + 500
            )
            boom.translate(boom_center)
            
            # --- Panel solar ---
            panel = Part.makeBox(P['panel_l'], P['panel_w'], P['panel_th'])
            panel_center = App.Vector(
                P['mid_d']/2 * math.cos(rad_angle) + P['boom_l'] * math.cos(rad_angle),
                P['mid_d']/2 * math.sin(rad_angle) + P['boom_l'] * math.sin(rad_angle),
                P['nose_len'] + P['mid_len'] + 500
            )
            panel.translate(panel_center)
            
            # --- Tubos de enfriamiento ---
            cooling_tubes = []
            tube_spacing = P['panel_w'] / (P['cooling_channels'] + 1)
            for j in range(P['cooling_channels']):
                tube = Part.makeCylinder(P['cooling_tube_r'], P['panel_l'])
                tube.translate(App.Vector(
                    panel_center.x,
                    panel_center.y - P['panel_w']/2 + tube_spacing * (j + 1),
                    panel_center.z + P['panel_th']/2
                ))
                cooling_tubes.append(tube)
            
            # --- Mástil de soporte del panel ---
            support = Part.makeCylinder(P['boom_r'] * 0.5, P['panel_w'])
            support.translate(App.Vector(
                panel_center.x,
                panel_center.y,
                panel_center.z
            ))
            support.rotate(panel_center, App.Vector(1, 0, 0), 90)
            
            # Ensamble del panel
            panel_assembly = boom.fuse(panel).fuse(support)
            for tube in cooling_tubes:
                panel_assembly = panel_assembly.fuse(tube)
            
            all_panels.append(panel_assembly)
        
        solar_panels = all_panels[0]
        for p in all_panels[1:]:
            solar_panels = solar_panels.fuse(p)
        
        self.add_object(solar_panels, "17_Solar_Panels")
        
        return solar_panels
    
    def create_structural_truss(self):
        """Crea el truss estructural con interfaces CNC"""
        P = self.P
        
        truss_beams = []
        
        for i in range(P['truss_count']):
            angle = i * (360.0 / P['truss_count'])
            rad_angle = math.radians(angle)
            
            # --- Viga principal ---
            beam = Part.makeCylinder(P['truss_beam_r'], P['truss_beam_l'])
            beam.translate(App.Vector(
                P['mid_d']/2 * math.cos(rad_angle),
                P['mid_d']/2 * math.sin(rad_angle),
                P['nose_len']
            ))
            
            # --- Nodos de conexión ---
            node_spacing = P['truss_beam_l'] / (P['interface_holes_count'] + 1)
            for j in range(P['interface_holes_count']):
                z_pos = P['nose_len'] + node_spacing * (j + 1)
                node = Part.makeSphere(P['truss_node_r'])
                node.translate(App.Vector(
                    P['mid_d']/2 * math.cos(rad_angle),
                    P['mid_d']/2 * math.sin(rad_angle),
                    z_pos
                ))
                beam = beam.fuse(node)
            
            # --- Agujeros de interfaz (para tornillos) ---
            for j in range(P['interface_holes_count']):
                z_pos = P['nose_len'] + node_spacing * (j + 1)
                
                # Agujero pasante
                hole = Part.makeCylinder(
                    (P['interface_holes_d']/2 + P['clearance']),
                    P['truss_beam_r'] * 2
                )
                hole.translate(App.Vector(
                    P['mid_d']/2 * math.cos(rad_angle),
                    P['mid_d']/2 * math.sin(rad_angle),
                    z_pos
                ))
                beam = beam.cut(hole)
            
            truss_beams.append(beam)
        
        # --- Riostras cruzadas ---
        if P['truss_cross bracing']:
            for i in range(P['truss_count']):
                for j in range(i + 1, P['truss_count']):
                    # Crear riostra entre vigas
                    angle1 = i * (360.0 / P['truss_count'])
                    angle2 = j * (360.0 / P['truss_count'])
                    
                    # No crear riostras si son adyacentes
                    if abs(angle2 - angle1) < 45:
                        continue
                    
                    rad1 = math.radians(angle1)
                    rad2 = math.radians(angle2)
                    
                    start = App.Vector(
                        P['mid_d']/2 * math.cos(rad1),
                        P['mid_d']/2 * math.sin(rad1),
                        P['nose_len'] + P['truss_beam_l']/2
                    )
                    end = App.Vector(
                        P['mid_d']/2 * math.cos(rad2),
                        P['mid_d']/2 * math.sin(rad2),
                        P['nose_len'] + P['truss_beam_l']/2
                    )
                    
                    # Crear tubo entre puntos
                    length = (end - start).Length
                    if length > 0:
                        cross = Part.makeCylinder(P['truss_beam_r']/3, length)
                        mid = App.Vector(
                            (start.x + end.x) / 2,
                            (start.y + end.y) / 2,
                            (start.z + end.z) / 2
                        )
                        cross.translate(mid)
                        
                        # Rotar para alinear
                        direction = end - start
                        if direction.x != 0 or direction.y != 0:
                            angle_xy = math.atan2(direction.y, direction.x)
                            cross.rotate(mid, App.Vector(0, 0, 1), math.degrees(angle_xy))
                        
                        for beam in truss_beams:
                            beam = beam.fuse(cross)
        
        truss = truss_beams[0]
        for b in truss_beams[1:]:
            truss = truss.fuse(b)
        
        self.add_object(truss, "18_Structural_Truss")
        
        return truss
    
    def create_mounting_base(self):
        """Crea la base de montaje con agujeros para fijaciones CNC"""
        P = self.P
        
        # --- Base principal ---
        base = Part.makeCylinder(P['base_d']/2, P['base_h'])
        
        # Reborde
        base_rim = Part.makeTorus(P['base_d']/2 - P['base_rim_t']/2, P['base_rim_t']/2)
        base_rim.translate(App.Vector(0, 0, P['base_h']))
        
        base = base.fuse(base_rim)
        base.translate(App.Vector(0, 0, -P['base_h']))
        
        # --- Agujeros para pernos de fijación ---
        bolt_holes = []
        for i in range(P['bolt_count']):
            angle = i * (360.0 / P['bolt_count'])
            
            # Agujero pasante
            hole = Part.makeCylinder(
                (P['bolt_d']/2 + P['clearance']),
                P['base_h'] * 2
            )
            hole.translate(App.Vector(
                (P['base_d']/2 - 200) * math.cos(math.radians(angle)),
                (P['base_d']/2 - 200) * math.sin(math.radians(angle)),
                0
            ))
            bolt_holes.append(hole)
            
            # Cabeza de perno (modelo)
            bolt_head = Part.makeCylinder(P['bolt_head_d']/2, P['bolt_head_h'])
            bolt_head.translate(App.Vector(
                (P['base_d']/2 - 200) * math.cos(math.radians(angle)),
                (P['base_d']/2 - 200) * math.sin(math.radians(angle)),
                P['base_h'] - P['bolt_head_h']/2
            ))
            base = base.fuse(bolt_head)
        
        # Cortar agujeros
        for hole in bolt_holes:
            base = base.cut(hole)
        
        # --- Agujeros de instalación adicionales ---
        install_holes = []
        for i in range(8):
            angle = i * (45.0)
            hole = Part.makeCylinder(15, P['base_h'])
            hole.translate(App.Vector(
                (P['base_d']/2 - 100) * math.cos(math.radians(angle)),
                (P['base_d']/2 - 100) * math.sin(math.radians(angle)),
                0
            ))
            install_holes.append(hole)
        
        for hole in install_holes:
            base = base.cut(hole)
        
        self.add_object(base, "19_Mounting_Base")
        
        return base
    
    def create_antennas(self):
        """Crea las antenas de comunicación"""
        P = self.P
        
        # --- Antena de baja ganancia ---
        mast = Part.makeCylinder(P['mast_r'], P['mast_l'])
        mast.translate(App.Vector(
            P['mid_d']/2 + 100, 0,
            P['nose_len'] + P['mid_len']
        ))
        
        # Plato parabólico
        dish = Part.makeCone(P['dish_r'], P['dish_r'] - 200.0, 180.0)
        dish.translate(App.Vector(
            P['mid_d']/2 + 100, 0,
            P['nose_len'] + P['mid_len'] + P['mast_l']
        ))
        
        antenna = mast.fuse(dish)
        self.add_object(antenna, "20_Low_Gain_Antenna")
        
        # --- Antena de alta ganancia ---
        hg_mast = Part.makeCylinder(P['mast_r'], P['hg_antenna_mast_l'])
        hg_mast.translate(App.Vector(
            -P['mid_d']/2 - 200, 0,
            P['nose_len'] + P['mid_len'] + 1000
        ))
        
        hg_dish = Part.makeCone(
            P['hg_antenna_dish_r'],
            P['hg_antenna_dish_r'] - 300,
            200
        )
        hg_dish.translate(App.Vector(
            -P['mid_d']/2 - 200, 0,
            P['nose_len'] + P['mid_len'] + 1000 + P['hg_antenna_mast_l']
        ))
        
        hg_antenna = hg_mast.fuse(hg_dish)
        self.add_object(hg_antenna, "21_High_Gain_Antenna")
        
        return antenna, hg_antenna
    
    def create_navigation_sensors(self):
        """Crea los sensores de navegación solar"""
        P = self.P
        
        sensors = []
        for i in range(P['nav_sensor_count']):
            angle = i * (360.0 / P['nav_sensor_count'])
            
            # Sensor (esfera con Housing)
            sensor = Part.makeSphere(P['nav_sensor_r'])
            sensor.translate(App.Vector(
                P['mid_d']/2 * math.cos(math.radians(angle)),
                P['mid_d']/2 * math.sin(math.radians(angle)),
                P['nose_len'] + 500
            ))
            
            # Housing del sensor
            housing = Part.makeCylinder(P['nav_sensor_r'] * 2, P['nav_sensor_r'])
            housing.translate(App.Vector(
                P['mid_d']/2 * math.cos(math.radians(angle)),
                P['mid_d']/2 * math.sin(math.radians(angle)),
                P['nose_len'] + 500
            ))
            
            sensor = sensor.fuse(housing)
            sensors.append(sensor)
        
        nav_sensors = sensors[0]
        for s in sensors[1:]:
            nav_sensors = nav_sensors.fuse(s)
        
        self.add_object(nav_sensors, "22_Navigation_Sensors")
        
        return nav_sensors
    
    def create_landing_gear(self):
        """Crea el tren de aterrizaje"""
        P = self.P
        
        legs = []
        angles = [0, 90, 180, 270]
        
        for angle in angles:
            rad = math.radians(angle)
            
            # --- Pata principal ---
            leg = Part.makeCylinder(P['leg_r'], P['leg_l'])
            leg.translate(App.Vector(
                P['mid_d']/2 * math.cos(rad),
                P['mid_d']/2 * math.sin(rad),
                0
            ))
            
            # --- Pie/patín de aterrizaje ---
            foot = Part.makeCylinder(P['foot_r'], P['foot_t'])
            foot.translate(App.Vector(
                P['mid_d']/2 * math.cos(rad),
                P['mid_d']/2 * math.sin(rad),
                -P['foot_t']
            ))
            
            # --- Sistema de retracción (representación) ---
            if P['retractable']:
                cylinder = Part.makeCylinder(P['leg_r'] * 1.5, P['leg_r'] * 2)
                cylinder.translate(App.Vector(
                    P['mid_d']/2 * math.cos(rad),
                    P['mid_d']/2 * math.sin(rad),
                    P['leg_l']/2
                ))
                leg = leg.fuse(cylinder)
            
            leg = leg.fuse(foot)
            legs.append(leg)
        
        landing = legs[0]
        for l in legs[1:]:
            landing = landing.fuse(l)
        
        self.add_object(landing, "23_Landing_Gear")
        
        return landing
    
    def create_scientific_instruments(self):
        """Crea los instrumentos científicos"""
        P = self.P
        
        # --- FIELDS: booms para campos eléctricos/magnéticos ---
        fields_boom = Part.makeCylinder(P['fields_boom_r'], P['fields_boom_l'])
        fields_boom.translate(App.Vector(
            0, P['mid_d']/2 + 200,
            P['nose_len'] + 1000
        ))
        
        # Sensor FIELDS
        fields_sensor = Part.makeSphere(P['fields_sensor_r'])
        fields_sensor.translate(App.Vector(
            0, P['mid_d']/2 + 200 + P['fields_boom_l'],
            P['nose_len'] + 1000
        ))
        
        fields = fields_boom.fuse(fields_sensor)
        self.add_object(fields, "24_Fields_Instrument")
        
        # --- SWEAP: detector de partículas ---
        sweap = Part.makeSphere(P['sweap_sensor_r'])
        sweap.translate(App.Vector(
            P['mid_d']/2 + 300, 0,
            P['nose_len'] + 1500
        ))
        self.add_object(sweap, "25_SWEAP_Instrument")
        
        # --- ISIS: partículas energéticas ---
        isis = Part.makeSphere(P['isis_sensor_r'])
        isis.translate(App.Vector(
            -P['mid_d']/2 - 300, 0,
            P['nose_len'] + 1500
        ))
        self.add_object(isis, "26_ISIS_Instrument")
        
        # --- WISPR: cámaras ---
        wispr = Part.makeSphere(P['wispr_camera_r'])
        wispr.translate(App.Vector(
            0, -P['mid_d']/2 - 200,
            P['nose_len'] + 2000
        ))
        self.add_object(wispr, "27_WISPR_Instrument")
        
        return fields, sweap, isis, wispr
    
    def create_docking_ports(self):
        """Crea los puertos de acoplamiento"""
        P = self.P
        
        # Puerto izquierdo
        dockL = Part.makeCylinder(P['dock_r'], P['dock_l'])
        dockL.translate(App.Vector(P['dock_off'], 0, P['nose_len'] + 1800))
        
        # Puerto derecho
        dockR = Part.makeCylinder(P['dock_r'], P['dock_l'])
        dockR.translate(App.Vector(-P['dock_off'], 0, P['nose_len'] + 1800))
        
        # Anillos de sellado
        for dock in [dockL, dockR]:
            ring = Part.makeTorus(P['dock_r'] + 20, 15)
            ring.translate(dock.Center)
            dock = dock.fuse(ring)
        
        docking = dockL.fuse(dockR)
        
        self.add_object(dockL, "28_Docking_Port_Left")
        self.add_object(dockR, "29_Docking_Port_Right")
        
        return docking
    
    def create_internal_beams(self):
        """Crea los refuerzos internos"""
        P = self.P
        
        beams = []
        
        # Vigas longitudinales
        for i in range(4):
            angle = i * 90.0
            beam = Part.makeCylinder(P['beam_r'], P['beam_l'])
            beam.translate(App.Vector(
                P['mid_d']/4 * math.cos(math.radians(angle)),
                P['mid_d']/4 * math.sin(math.radians(angle)),
                P['nose_len']
            ))
            beams.append(beam)
        
        # Vigas transversales
        for z in [P['nose_len'], P['nose_len'] + P['mid_len']/2, P['nose_len'] + P['mid_len']]:
            ring = Part.makeTorus(P['mid_d']/4, P['beam_r'])
            ring.translate(App.Vector(0, 0, z))
            beams.append(ring)
        
        result = beams[0]
        for b in beams[1:]:
            result = result.fuse(b)
        
        self.add_object(result, "30_Internal_Beams")
        
        return result
    
    def create_cooling_system(self):
        """Crea el sistema de enfriamiento activo"""
        P = self.P
        
        # --- Bomba de refrigerante ---
        pump = Part.makeCylinder(P['cooling_pump_r'], P['cooling_pump_r'] * 2)
        pump.translate(App.Vector(0, 0, P['nose_len'] + P['mid_len']))
        self.add_object(pump, "31_Cooling_Pump")
        
        # --- Intercambiador de calor ---
        exchanger = Part.makeCylinder(P['heat_exchanger_r'], P['heat_exchanger_r'])
        exchanger.translate(App.Vector(0, 0, P['nose_len'] + P['mid_len'] + 500))
        
        # Aletas del intercambiador
        fin_count = 20
        for i in range(fin_count):
            angle = i * (360.0 / fin_count)
            fin = Part.makeBox(10, P['heat_exchanger_r'] * 1.5, 5)
            fin.Placement = App.Placement(
                App.Vector(0, 0, P['nose_len'] + P['mid_len'] + 500),
                App.Rotation(App.Vector(0, 0, 1), angle)
            )
            exchanger = exchanger.fuse(fin)
        
        self.add_object(exchanger, "32_Heat_Exchanger")
        
        # --- Tuberías de refrigerante ---
        pipes = []
        for i in range(P['cooling_pipes']):
            angle = i * (360.0 / P['cooling_pipes'])
            pipe = Part.makeCylinder(15, P['mid_len'])
            pipe.translate(App.Vector(
                P['mid_d']/3 * math.cos(math.radians(angle)),
                P['mid_d']/3 * math.sin(math.radians(angle)),
                P['nose_len'] + P['mid_len']/2
            ))
            pipes.append(pipe)
        
        result = pipes[0]
        for p in pipes[1:]:
            result = result.fuse(p)
        
        self.add_object(result, "33_Cooling_Pipes")
        
        return pump, exchanger, result
    
    def create_all_parts(self):
        """Crea todas las partes de la nave"""
        
        # Sistema de estructura principal
        self.create_hull()
        self.create_thermal_shield()
        self.create_hull_shields()
        
        # Sistema de propulsión
        self.create_reactor()
        
        # Sistemas de生存
        self.create_cockpit_habitat()
        self.create_fuel_tanks()
        
        # Control térmico
        self.create_radiators()
        self.create_thermal_collar()
        self.create_cooling_system()
        
        # Paneles solares
        self.create_solar_panels()
        
        # Estructura
        self.create_structural_truss()
        self.create_mounting_base()
        self.create_internal_beams()
        
        # Sistemas de comunicación y navegación
        self.create_antennas()
        self.create_navigation_sensors()
        
        # Tren de aterrizaje
        self.create_landing_gear()
        
        # Instrumentos científicos
        self.create_scientific_instruments()
        
        # Puertos
        self.create_docking_ports()
        
        # Recomputar documento
        self.doc.recompute()
        
        return self.parts
    
    def export_stl(self, filename, part_name=None):
        """Exporta partes a formato STL para impresión 3D"""
        import Mesh
        
        if part_name:
            if part_name in self.parts:
                mesh = Mesh.Mesh(self.parts[part_name].Shape.tessellate(0.01))
                mesh.write(filename)
        else:
            # Exportar todas las partes
            for name, obj in self.parts.items():
                try:
                    stl_file = filename.replace('.stl', f'_{name}.stl')
                    mesh = Mesh.Mesh(obj.Shape.tessellate(0.01))
                    mesh.write(stl_file)
                except:
                    pass
    
    def get_part_list(self):
        """Retorna lista de partes creadas"""
        return list(self.parts.keys())


def create_sample():
    """Función de ejemplo para crear la nave"""
    # Crear instancia
    nave = ParametricSpacecraft()
    
    # Crear todas las partes
    parts = nave.create_all_parts()
    
    # Obtener lista de partes
    part_list = nave.get_part_list()
    
    print("=" * 60)
    print("NAVE ESPACIAL DFD-XL - PROTOTIPO MECÁNICO CNC/3D")
    print("=" * 60)
    print(f"\nTotal de partes creadas: {len(part_list)}")
    print("\nLista de componentes:")
    for i, part in enumerate(part_list, 1):
        print(f"  {i:2d}. {part}")
    
    print("\n" + "=" * 60)
    print("Parámetros principales:")
    print("=" * 60)
    print(f"  Longitud total: {nave.P['nose_len'] + nave.P['mid_len'] + nave.P['rear_len']:.0f} mm")
    print(f"  Diámetro máximo: {nave.P['rear_d']:.0f} mm")
    print(f"  Diámetro base montaje: {nave.P['base_d']:.0f} mm")
    print(f"  Paneles solares: {nave.P['panel_count']} unidades")
    print(f"  Vigas truss: {nave.P['truss_count']} unidades")
    print(f"  Perfiles de fijación: {nave.P['bolt_count']} pernos")
    print("=" * 60)
    
    return nave


# =============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# =============================================================================
if __name__ == "__main__":
    nave = create_sample()
    
    print("\n¡Modelo creado exitosamente!")
    print("Para visualizar en FreeCAD, ejecuta este script desde FreeCAD")
