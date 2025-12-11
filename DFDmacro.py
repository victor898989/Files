import FreeCAD as App, Part, math

doc = App.newDocument("Nave_DFD_XL_Solar")

# ========================
# Parámetros
# ========================
P = {
    'scale': 2.0,  # nave más grande

    # Fuselaje (igual base, estilo DFD)
    'nose_len': 1500.0, 'nose_base_d': 1100.0,
    'mid_len': 3000.0, 'mid_d': 1800.0,
    'rear_len': 1500.0, 'rear_d': 2200.0,
    'hull_t': 30.0,

    # Escudo térmico frontal multilayer (TPS)
    'shield_d': 2600.0,      # diámetro del escudo principal
    'shield_flecha': 80.0,   # flecha/abombamiento frontal
    't_ceramic': 4.0, 't_foam': 120.0, 't_cc': 12.0,
    'rim_w': 60.0, 'rim_h': 80.0,

    # Mangas/blindajes TPS alrededor del fuselaje y reactor
    'hull_shield_t': 80.0, 'hull_shield_l': 2800.0,
    'reactor_shield_t': 120.0, 'reactor_shield_l': 2200.0,

    # Reactor (como base DFD)
    'reactor_d': 1500.0, 'reactor_l': 1800.0,

    # Módulo hábitat
    'hab_d': 1400.0, 'hab_l': 2500.0,

    # Cabina
    'cockpit_d': 900.0, 'cockpit_l': 800.0, 'window_r': 150.0,

    # Tanques laterales
    'tank_r': 400.0, 'tank_l': 2000.0, 'tank_off': 1200.0,

    # Tanques esféricos
    'sphere_r': 450.0, 'sphere_off': 1600.0,

    # Radiadores (reformulados a sombra trasera)
    'wing_span': 2500.0, 'wing_th': 60.0, 'wing_l': 2200.0, 'wing_back_offset': 1200.0,

    # Collar térmico y paravientos (deflectores)
    'collar_d_delta': 300.0, 'collar_h': 120.0, 'collar_t': 40.0,
    'def_count': 8, 'def_l': 800.0, 'def_w': 160.0, 'def_t': 30.0,

    # Antenas
    'mast_l': 1000.0, 'mast_r': 40.0, 'dish_r': 400.0,

    # Tren de aterrizaje
    'leg_r': 100.0, 'leg_l': 800.0, 'foot_r': 250.0, 'foot_t': 50.0,

    # Escotillas y acoplamiento
    'dock_r': 400.0, 'dock_l': 300.0, 'dock_off': 800.0,

    # Sensores
    'sensor_r': 50.0, 'sensor_l': 200.0,

    # Refuerzos internos
    'beam_r': 50.0, 'beam_l': 3000.0,

    # Tolerancias de solape para fusión robusta
    'overlap': 2.0,

    # Paneles solares retráctiles con enfriamiento
    'panel_l': 3000.0, 'panel_w': 1500.0, 'panel_th': 20.0, 'panel_count': 4,
    'boom_r': 50.0, 'boom_l': 4000.0, 'cooling_tube_r': 10.0,

    # Instrumentos científicos
    'fields_boom_l': 5000.0, 'fields_boom_r': 30.0, 'fields_sensor_r': 100.0,
    'sweap_sensor_r': 80.0, 'isis_sensor_r': 70.0, 'wispr_camera_r': 60.0,

    # Antenas de alta ganancia
    'hg_antenna_dish_r': 600.0, 'hg_antenna_mast_l': 1500.0,

    # Sensores de navegación solar
    'nav_sensor_r': 40.0, 'nav_sensor_count': 6,

    # Truss estructural
    'truss_beam_r': 80.0, 'truss_beam_l': 6000.0, 'truss_count': 8,

    # Base de montaje
    'base_d': 3000.0, 'base_h': 200.0
}

# ========================
# Función auxiliar
# ========================
def add_obj(shape, name):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj

# ========================
# Fuselaje principal (base DFD)
# ========================
nose = Part.makeCone(0, P['nose_base_d']/2, P['nose_len'])
mid = Part.makeCylinder(P['mid_d']/2, P['mid_len'])
mid.translate(App.Vector(0,0,P['nose_len']))
rear = Part.makeCone(P['rear_d']/2, P['mid_d']/2, P['rear_len'])
rear.translate(App.Vector(0,0,P['nose_len']+P['mid_len']))
hull = nose.fuse(mid).fuse(rear)

# ========================
# Escudo térmico frontal multilayer (TPS)
# ========================
shield_R = P['shield_d']/2.0
# Cara cerámica (disco + flecha mediante cono corto)
cer = Part.makeCylinder(shield_R, P['t_ceramic'])
cone = Part.makeCone(shield_R, shield_R - 40.0, P['shield_flecha'])
cone.translate(App.Vector(0,0,-P['shield_flecha']))
cer = cer.fuse(cone)

# Núcleo foam
foam = Part.makeCylinder(shield_R - P['overlap'], P['t_foam'])
foam.translate(App.Vector(0,0,P['t_ceramic'] - P['overlap']))

# Capa trasera C/C
back = Part.makeCylinder(shield_R - 2*P['overlap'], P['t_cc'])
back.translate(App.Vector(0,0,P['t_ceramic'] + P['t_foam'] - 2*P['overlap']))

# Rim perimetral
rimOD = shield_R; rimID = shield_R - P['rim_w']
rim = Part.makeCylinder(rimOD, P['rim_h']).cut(Part.makeCylinder(rimID, P['rim_h']))
rim.translate(App.Vector(0,0,P['t_ceramic'] + P['t_foam'] + P['t_cc'] - P['rim_h']))

# Ensamble del escudo como sólido único
shield = cer.fuse(foam).fuse(back).fuse(rim)
# Posicionamiento delante del fuselaje
shield.translate(App.Vector(0,0,-(P['t_ceramic'] + P['t_foam'] + P['t_cc'])))

# ========================
# Blindajes TPS alrededor del fuselaje y reactor (mangas)
# ========================
# Manga cilindrica sobre sección media
hull_shield = Part.makeCylinder(P['mid_d']/2 + P['hull_shield_t'], P['hull_shield_l'])
hull_shield.translate(App.Vector(0,0,P['nose_len'] + (P['mid_len'] - P['hull_shield_l'])/2.0))

# Manga reactor
reactor_shield = Part.makeCylinder(P['reactor_d']/2 + P['reactor_shield_t'], P['reactor_shield_l'])
reactor_shield.translate(App.Vector(0,0,P['nose_len'] + P['mid_len'] - 200.0))

# ========================
# Reactor + boquilla (base DFD)
# ========================
reactor = Part.makeCylinder(P['reactor_d']/2, P['reactor_l'])
reactor.translate(App.Vector(0,0,P['nose_len']+1200))
nozzle = Part.makeCone(P['rear_d']/2, P['rear_d'], 1000)
nozzle.translate(App.Vector(0,0,P['nose_len']+P['mid_len']+P['rear_len']))
reactor_full = reactor.fuse(nozzle)

# ========================
# Módulo hábitat
# ========================
hab = Part.makeCylinder(P['hab_d']/2, P['hab_l'])
hab.translate(App.Vector(0,0,P['nose_len']+P['mid_len']+500))

# ========================
# Cabina de mando
# ========================
cockpit = Part.makeCylinder(P['cockpit_d']/2, P['cockpit_l'])
cockpit.translate(App.Vector(0,0,50))
window = Part.makeSphere(P['window_r'])
window.translate(App.Vector(P['cockpit_d']/3,0,P['cockpit_l']/2))
cockpit_cut = cockpit.cut(window)

# ========================
# Tanques laterales y esféricos
# ========================
tankL = Part.makeCylinder(P['tank_r'], P['tank_l'])
tankL.translate(App.Vector(P['tank_off'],0,P['nose_len']+1000))
tankR = Part.makeCylinder(P['tank_r'], P['tank_l'])
tankR.translate(App.Vector(-P['tank_off'],0,P['nose_len']+1000))
sphereL = Part.makeSphere(P['sphere_r'])
sphereL.translate(App.Vector(P['sphere_off'],0,P['nose_len']+2500))
sphereR = Part.makeSphere(P['sphere_r'])
sphereR.translate(App.Vector(-P['sphere_off'],0,P['nose_len']+2500))
tanks = tankL.fuse(tankR).fuse(sphereL).fuse(sphereR)

# ========================
# Radiadores en sombra (reubicados hacia atrás)
# ========================
wingL = Part.makeBox(P['wing_span'], P['wing_th'], P['wing_l'])
wingL.translate(App.Vector(-P['wing_span']/2, -P['mid_d']/2-150, P['nose_len']+P['mid_len']+P['wing_back_offset']))
wingR = Part.makeBox(P['wing_span'], P['wing_th'], P['wing_l'])
wingR.translate(App.Vector(-P['wing_span']/2, P['mid_d']/2+150, P['nose_len']+P['mid_len']+P['wing_back_offset']))
wings = wingL.fuse(wingR)

# ========================
# Collar térmico y paravientos (deflectores)
# ========================
collarOD = P['mid_d'] + P['collar_d_delta']
collar = Part.makeCylinder(collarOD/2.0, P['collar_h']).cut(Part.makeCylinder((collarOD/2.0 - P['collar_t']), P['collar_h']))
# Centrado en mitad del tramo medio
collar.translate(App.Vector(0,0,P['nose_len'] + P['mid_len']/2.0 - P['collar_h']/2.0))

# Deflectores longitudinales (placas) alrededor del mid
defs = []
for i in range(P['def_count']):
    ang = i * (360.0 / P['def_count'])
    d = Part.makeBox(P['def_l'], P['def_w'], P['def_t'])
    d.translate(App.Vector(-P['def_l']/2.0, -P['def_w']/2.0, P['nose_len'] + P['mid_len']/2.0 - P['def_t']/2.0))
    # Rotamos alrededor del eje Z para distribuir como pétalos alrededor del collar
    # Luego desplazamos radialmente hasta el radio del collar
    baseR = collarOD/2.0 + P['overlap']
    d.Placement = App.Placement(App.Vector(baseR,0,0), App.Rotation(App.Vector(0,0,1), ang))
    defs.append(d)
deflectores = defs[0]
for d in defs[1:]:
    deflectores = deflectores.fuse(d)

# ========================
# Escotillas y acoplamientos
# ========================
dockL = Part.makeCylinder(P['dock_r'], P['dock_l'])
dockL.translate(App.Vector(P['dock_off'],0,P['nose_len']+1800))
dockR = Part.makeCylinder(P['dock_r'], P['dock_l'])
dockR.translate(App.Vector(-P['dock_off'],0,P['nose_len']+1800))
docking = dockL.fuse(dockR)

# ========================
# Sensores y cámaras externas
# ========================
sensor1 = Part.makeSphere(P['sensor_r'])
sensor1.translate(App.Vector(P['mid_d']/2+100,0,P['nose_len']+2000))
sensor2 = Part.makeSphere(P['sensor_r'])
sensor2.translate(App.Vector(-P['mid_d']/2-100,0,P['nose_len']+2000))
sensors = sensor1.fuse(sensor2)

# ========================
# Refuerzos internos
# ========================
beam1 = Part.makeCylinder(P['beam_r'], P['beam_l'])
beam1.translate(App.Vector(0,0,P['nose_len']))
beam2 = Part.makeCylinder(P['beam_r'], P['beam_l'])
beam2.translate(App.Vector(0,0,P['nose_len']+P['mid_len']))
beams = beam1.fuse(beam2)

# ========================
# Antena + parabólica
# ========================
mast = Part.makeCylinder(P['mast_r'], P['mast_l'])
mast.translate(App.Vector(P['mid_d']/2+100,0,P['nose_len']+P['mid_len']))
dish = Part.makeSphere(P['dish_r'])
# Simular plato comprimido (paraboloide aproximado): escalado no está directamente en Part,
# así que modelamos plato por corte simple
dish_flat = Part.makeCone(P['dish_r'], P['dish_r']-200.0, 180.0)
dish_flat.translate(App.Vector(P['mid_d']/2+100,0,P['nose_len']+P['mid_len']+P['mast_l']))
antenna = mast.fuse(dish_flat)

# ========================
# Tren de aterrizaje 4 patas
# ========================
legs = []
for angle in [0,90,180,270]:
    leg = Part.makeCylinder(P['leg_r'], P['leg_l'])
    leg.translate(App.Vector(P['mid_d']/2*math.cos(math.radians(angle)),
                             P['mid_d']/2*math.sin(math.radians(angle)),0))
    foot = Part.makeCylinder(P['foot_r'], P['foot_t'])
    foot.translate(App.Vector(P['mid_d']/2*math.cos(math.radians(angle)),
                              P['mid_d']/2*math.sin(math.radians(angle)),-P['foot_t']))
    legs.append(leg.fuse(foot))
landing_full = legs[0].fuse(legs[1]).fuse(legs[2]).fuse(legs[3])

# ========================
# Paneles solares retráctiles con sistema de enfriamiento
# ========================
panels = []
for i in range(P['panel_count']):
    ang = i * (360.0 / P['panel_count'])
    boom = Part.makeCylinder(P['boom_r'], P['boom_l'])
    boom.translate(App.Vector(P['mid_d']/2 * math.cos(math.radians(ang)),
                              P['mid_d']/2 * math.sin(math.radians(ang)),
                              P['nose_len'] + P['mid_len'] + 500))
    panel = Part.makeBox(P['panel_l'], P['panel_w'], P['panel_th'])
    panel.translate(App.Vector(P['mid_d']/2 * math.cos(math.radians(ang)) + P['boom_l'] * math.cos(math.radians(ang)),
                               P['mid_d']/2 * math.sin(math.radians(ang)) + P['boom_l'] * math.sin(math.radians(ang)),
                               P['nose_len'] + P['mid_len'] + 500))
    # Cooling tubes
    cooling = Part.makeCylinder(P['cooling_tube_r'], P['panel_l'])
    cooling.translate(App.Vector(P['mid_d']/2 * math.cos(math.radians(ang)) + P['boom_l'] * math.cos(math.radians(ang)),
                                 P['mid_d']/2 * math.sin(math.radians(ang)) + P['boom_l'] * math.sin(math.radians(ang)),
                                 P['nose_len'] + P['mid_len'] + 500 + P['panel_th']/2))
    panels.append(boom.fuse(panel).fuse(cooling))
solar_panels = panels[0]
for p in panels[1:]:
    solar_panels = solar_panels.fuse(p)

# ========================
# Instrumentos científicos
# ========================
# FIELDS: booms for electric/magnetic fields
fields_boom = Part.makeCylinder(P['fields_boom_r'], P['fields_boom_l'])
fields_boom.translate(App.Vector(0, P['mid_d']/2 + 200, P['nose_len'] + 1000))
fields_sensor = Part.makeSphere(P['fields_sensor_r'])
fields_sensor.translate(App.Vector(0, P['mid_d']/2 + 200 + P['fields_boom_l'], P['nose_len'] + 1000))
fields = fields_boom.fuse(fields_sensor)

# SWEAP: particle detector
sweap = Part.makeSphere(P['sweap_sensor_r'])
sweap.translate(App.Vector(P['mid_d']/2 + 300, 0, P['nose_len'] + 1500))

# ISʘIS: energetic particles
isis = Part.makeSphere(P['isis_sensor_r'])
isis.translate(App.Vector(-P['mid_d']/2 - 300, 0, P['nose_len'] + 1500))

# WISPR: cameras
wispr = Part.makeSphere(P['wispr_camera_r'])
wispr.translate(App.Vector(0, -P['mid_d']/2 - 200, P['nose_len'] + 2000))

instruments = fields.fuse(sweap).fuse(isis).fuse(wispr)

# ========================
# Antenas de alta ganancia
# ========================
hg_mast = Part.makeCylinder(P['mast_r'], P['hg_antenna_mast_l'])
hg_mast.translate(App.Vector(-P['mid_d']/2 - 200, 0, P['nose_len'] + P['mid_len'] + 1000))
hg_dish = Part.makeCone(P['hg_antenna_dish_r'], P['hg_antenna_dish_r'] - 300, 200)
hg_dish.translate(App.Vector(-P['mid_d']/2 - 200, 0, P['nose_len'] + P['mid_len'] + 1000 + P['hg_antenna_mast_l']))
hg_antenna = hg_mast.fuse(hg_dish)

# ========================
# Sensores de navegación solar
# ========================
nav_sensors = []
for i in range(P['nav_sensor_count']):
    ang = i * (360.0 / P['nav_sensor_count'])
    sensor = Part.makeSphere(P['nav_sensor_r'])
    sensor.translate(App.Vector(P['mid_d']/2 * math.cos(math.radians(ang)),
                                P['mid_d']/2 * math.sin(math.radians(ang)),
                                P['nose_len'] + 500))
    nav_sensors.append(sensor)
nav_full = nav_sensors[0]
for s in nav_sensors[1:]:
    nav_full = nav_full.fuse(s)

# ========================
# Truss estructural
# ========================
truss_beams = []
for i in range(P['truss_count']):
    ang = i * (360.0 / P['truss_count'])
    beam = Part.makeCylinder(P['truss_beam_r'], P['truss_beam_l'])
    beam.translate(App.Vector(P['mid_d']/2 * math.cos(math.radians(ang)),
                              P['mid_d']/2 * math.sin(math.radians(ang)),
                              P['nose_len']))
    truss_beams.append(beam)
truss = truss_beams[0]
for b in truss_beams[1:]:
    truss = truss.fuse(b)

# ========================
# Base de montaje
# ========================
base = Part.makeCylinder(P['base_d']/2, P['base_h'])
base.translate(App.Vector(0, 0, -P['base_h']))

# ========================
# Ensamblaje final con fusión robusta
# ========================
nave = hull
for part in [shield, hull_shield, reactor_shield, cockpit_cut, reactor_full, hab, tanks,
             wings, collar, deflectores, docking, sensors, beams, antenna, landing_full,
             solar_panels, instruments, hg_antenna, nav_full, truss, base]:
    try:
        nave = nave.fuse(part)
    except Exception:
        # micro-solape para evitar coplanaridades estrictas
        part.translate(App.Vector(0,0,0.2))
        nave = nave.fuse(part)

nave_obj = add_obj(nave, "Nave_DFD_XL_Solar")
doc.recompute()
