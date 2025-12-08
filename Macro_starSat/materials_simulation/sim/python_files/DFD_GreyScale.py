# Macro FreeCAD: Direct Fusion Drive con TPS tipo Parker, ensamblado e imprimible (todo junto)
# Autor: Víctor + Copilot
# Unidades: mm, eje longitudinal = X

import FreeCAD as App, FreeCADGui as Gui, Part, math

doc_name="Direct_Fusion_Drive"
if App.ActiveDocument is None or App.ActiveDocument.Label!=doc_name:
    App.newDocument(doc_name)
doc=App.ActiveDocument

# ========================
# Parámetros base DFD
# ========================
P={
    "nose_len":800.0,"nose_base_d":600.0,
    "mid_len":1400.0,"mid_d":900.0,
    "rear_len":800.0,"rear_d":1200.0,
    "hull_t":10.0,
    "cockpit_w":900.0,"cockpit_h":400.0,"cockpit_l":600.0,"cockpit_x0":600.0,
    "win_w":600.0,"win_h":250.0,"win_th":20.0,
    "win_y_off":0.5*(900.0/2.0-250.0/2.0),"win_z":0.0,
    "reactor_d":800.0,"reactor_l":900.0,"reactor_cx":2600.0,
    "ring_h":30.0,"ring_ro":420.0,"ring_ri":380.0,"ring_n":6,"ring_pitch":150.0,
    "coil_rect_w":80.0,"coil_rect_h":80.0,"coil_R":440.0,"coil_n":4,"coil_span":800.0,
    "moderator_t":100.0,"moderator_gap":20.0,"moderator_over":200.0,
    "tungsten_post_t":10.0,
    "nozzle_throat_d":300.0,"nozzle_exit_d":900.0,"nozzle_l":700.0,"nozzle_cx":2850.0,"nozzle_fillet_r":40.0,
    "truss_n":3,"truss_tube_w":80.0,"truss_R_attach":550.0,
    "tank_d":300.0,"tank_l":700.0,"tank_cx":1600.0,"tank_cy":300.0,"tank_cz":-150.0,
    "leg_L_fold":400.0,"leg_L_ext":600.0,"leg_foot_d":180.0,
    "leg_side_x1":1050.0,"leg_side_x2":1950.0,"leg_side_y":600.0,
    "leg_front_x":400.0,"leg_front_y":0.0,"leg_front_z":-(900.0/2.0)+50.0,
    "wing_root_w":600.0,"wing_tip_w":150.0,"wing_chord":450.0,
    "fin_h":400.0,"fin_base":200.0,
    "rad_panel_w":800.0,"rad_panel_h":600.0,"rad_panel_n":5
}

# ========================
# TPS tipo Parker y Radiadores
# ========================
TPS={"tps_d":2400.0,"tps_t":100.0,"tps_gap":120.0,"sup_L":280.0,"sup_d_base":900.0,"sup_d_tip":600.0}
RAD={"th":4.0,"mount_gap_y":30.0,"x_start":None,"gap_x":None,"count_pairs":3,"span_x":220.0,"arm_len":60.0,"arm_r":10.0}

# ========================
# Instrumentos científicos (simplificados para CAD)
# ========================
INSTRUMENTS={
    "FIELDS":{"d":200.0,"l":300.0,"cx":500.0,"cy":0.0,"cz":150.0,"booms":4,"boom_l":500.0,"boom_r":5.0},  # Campos eléctricos/magnéticos
    "SWEAP":{"d":150.0,"l":250.0,"cx":600.0,"cy":0.0,"cz":-150.0,"detectors":3},  # Viento solar
    "ISIS":{"d":180.0,"l":280.0,"cx":700.0,"cy":0.0,"cz":0.0,"telescopes":2},  # Partículas energéticas
    "WISPR":{"d":120.0,"l":200.0,"cx":800.0,"cy":0.0,"cz":100.0,"cameras":2}  # Cámara solar
}

# ========================
# TPS mejorado con aislamiento multicapa y recubrimiento cerámico
# ========================
TPS_ADVANCED={
    "insul_layers":5,"insul_t":2.0,"insul_gap":1.0,"ceramic_t":5.0,"foam_t":50.0,
    "support_beams":8,"beam_r":10.0,"beam_l":TPS["sup_L"]+100.0
}

# ========================
# Sistema de energía: Paneles solares retráctiles con refrigeración
# ========================
ENERGY={
    "panels":4,"panel_w":1000.0,"panel_h":800.0,"panel_t":10.0,"retract_l":600.0,
    "cooling_tubes":6,"tube_r":8.0,"cooling_fluid":"water",
    "cx":P["nose_len"]+P["mid_len"]+200.0,"cy":P["rear_d"]/2.0+200.0,"cz":0.0
}

# ========================
# Comunicación y navegación: Antenas HGA y sensores solares
# ========================
COMM_NAV={
    "hga_dish_d":400.0,"hga_arm_l":250.0,"hga_arm_r":15.0,"hga_cx":P["nose_len"]+300.0,"hga_cy":0.0,"hga_cz":200.0,
    "solar_sensors":4,"sensor_d":50.0,"sensor_l":30.0,"sensor_r":100.0
}

# ========================
# Estructura: Truss avanzado para soporte TPS y subsistemas
# ========================
STRUCTURE={
    "truss_beams":12,"truss_r":600.0,"truss_beam_r":15.0,"truss_beam_l":800.0,
    "mounts":6,"mount_r":20.0,"mount_h":50.0
}

# ========================
# Materiales
# ========================
MAT={
    'AL':{'name':'AA-2xxx','rho':2700.0,'E':72e9,'nu':0.33,'type':'isotropic'},
    'STEEL':{'name':'SS-304','rho':8000.0,'E':200e9,'nu':0.30,'type':'isotropic'},
    'COPPER':{'name':'Copper','rho':8960.0,'E':110e9,'nu':0.34,'type':'isotropic'},
    'CFRP':{'name':'CFRP','rho':1550.0,'Ex':130e9,'Ey':10e9,'Ez':10e9,'nu_xy':0.25,'type':'orthotropic'},
    'CC':{'name':'C/C TPS','rho':1600.0,'Ex':70e9,'Ey':70e9,'Ez':10e9,'nu_xy':0.2,'type':'orthotropic'},
    'KEVLAR':{'name':'Kevlar','rho':1440.0,'Ex':70e9,'Ey':5e9,'Ez':5e9,'nu_xy':0.27,'type':'orthotropic'}
}

# ========================
# Utilidades
# ========================
X_AXIS=App.Vector(1,0,0);Y_AXIS=App.Vector(0,1,0);Z_AXIS=App.Vector(0,0,1)
def rot_to_x():return App.Rotation(Y_AXIS,90)
def add_obj(shape,label):obj=doc.addObject("Part::Feature",label);obj.Shape=shape;return obj
def set_mat(obj,mat): 
    if not obj:return
    m=MAT.get(mat,None)if isinstance(mat,str)else mat
    if not m:return
    obj.addProperty("App::PropertyString","Material","Meta","").Material=m.get('name','')
    obj.addProperty("App::PropertyMap","MaterialData","Meta","").MaterialData={k:str(v)for k,v in m.items()}
    obj.addProperty("App::PropertyFloat","Density","Meta","").Density=m.get('rho',0.0)
def make_cyl_x(d,L,cx=0.0,cy=0.0,cz=0.0,label="CylX"):
    r=d/2.0;cyl=Part.makeCylinder(r,L);cyl.Placement=App.Placement(App.Vector(cx-L/2.0,cy,cz),rot_to_x());return add_obj(cyl,label)
def make_cone_x(d1,d2,L,cx=0.0,cy=0.0,cz=0.0,label="ConeX"):
    r1=d1/2.0;r2=d2/2.0;cone=Part.makeCone(r1,r2,L);cone.Placement=App.Placement(App.Vector(cx-L/2.0,cy,cz),rot_to_x());return add_obj(cone,label)
def make_torus_x(R,r,cx=0.0,cy=0.0,cz=0.0,label="TorusX"):
    tor=Part.makeTorus(R,r);tor.Placement=App.Placement(App.Vector(cx,cy,cz),rot_to_x());return add_obj(tor,label)
def make_box(w,d,h,cx=0.0,cy=0.0,cz=0.0,label="Box"):
    b=Part.makeBox(w,d,h);b.Placement=App.Placement(App.Vector(cx-w/2.0,cy-d/2.0,cz-h/2.0),App.Rotation());return add_obj(b,label)
def make_hollow_from_offset(outer_shape,t,label="Shell"): 
    try:
        inner=outer_shape.makeOffsetShape(-t,0.01,join=2,fill=True)
        shell=outer_shape.cut(inner)
        return add_obj(shell,label)
    except Exception:
        return add_obj(outer_shape,label+"_fallback")
def fillet_between(shpA,shpB,r):
    fused=shpA.fuse(shpB)
    try:
        edges=[e for e in fused.Edges if e.Length>30 and e.Length<10000]
        new=fused.makeFillet(r,edges);return new
    except Exception:
        return fused
def sweep_rect_around_X(R,rw,rh,cx,cy,cz,ax0,ax1,label="CoilSweep"):
    circ=Part.makeCircle(R,App.Vector(cx,cy,cz),X_AXIS);path=Part.Wire([circ])
    p0=App.Vector(0,-rw/2.0,-rh/2.0);p1=App.Vector(0,rw/2.0,-rh/2.0)
    p2=App.Vector(0,rw/2.0,rh/2.0);p3=App.Vector(0,-rw/2.0,rh/2.0)
    e1=Part.makeLine(p0,p1);e2=Part.makeLine(p1,p2);e3=Part.makeLine(p2,p3);e4=Part.makeLine(p3,p0)
    prof=Part.Wire([e1,e2,e3,e4])
    prof.Placement=App.Placement(App.Vector(cx,cy,cz),App.Rotation(X_AXIS,0))
    sweep=Part.Wire(path).makePipeShell([prof],True,True)
    return add_obj(sweep,label)

# ========================
# Funciones para instrumentos científicos
# ========================
def create_instrument_fields():
    inst = INSTRUMENTS["FIELDS"]
    body = make_cyl_x(inst["d"], inst["l"], cx=inst["cx"], cy=inst["cy"], cz=inst["cz"], label="FIELDS_Body")
    set_mat(body, 'AL')
    booms = []
    for i in range(inst["booms"]):
        ang = i * (360.0 / inst["booms"])
        y = inst["cz"] + inst["boom_l"] * math.cos(math.radians(ang))
        z = inst["cz"] + inst["boom_l"] * math.sin(math.radians(ang))
        boom = make_cyl_x(inst["boom_r"]*2, inst["boom_l"], cx=inst["cx"], cy=y, cz=z, label=f"FIELDS_Boom_{i+1}")
        set_mat(boom, 'AL')
        booms.append(boom.Shape)
    if booms:
        booms_shape = booms[0]
        for b in booms[1:]: booms_shape = booms_shape.fuse(b)
        booms_obj = add_obj(booms_shape, "FIELDS_Booms")
        set_mat(booms_obj, 'AL')
        return body.Shape.fuse(booms_shape)
    return body.Shape

def create_instrument_sweap():
    inst = INSTRUMENTS["SWEAP"]
    body = make_cyl_x(inst["d"], inst["l"], cx=inst["cx"], cy=inst["cy"], cz=inst["cz"], label="SWEAP_Body")
    set_mat(body, 'STEEL')
    detectors = []
    for i in range(inst["detectors"]):
        det = make_cyl_x(inst["d"]/3, inst["l"]/2, cx=inst["cx"] + i*50, cy=inst["cy"], cz=inst["cz"] + i*30, label=f"SWEAP_Det_{i+1}")
        set_mat(det, 'COPPER')
        detectors.append(det.Shape)
    if detectors:
        det_shape = detectors[0]
        for d in detectors[1:]: det_shape = det_shape.fuse(d)
        return body.Shape.fuse(det_shape)
    return body.Shape

def create_instrument_isis():
    inst = INSTRUMENTS["ISIS"]
    body = make_box(inst["l"], inst["d"], inst["d"], cx=inst["cx"], cy=inst["cy"], cz=inst["cz"], label="ISIS_Body")
    set_mat(body, 'STEEL')
    telescopes = []
    for i in range(inst["telescopes"]):
        tel = make_cyl_x(inst["d"]/4, inst["l"]/3, cx=inst["cx"] + i*40, cy=inst["cy"] + i*20, cz=inst["cz"], label=f"ISIS_Tel_{i+1}")
        set_mat(tel, 'AL')
        telescopes.append(tel.Shape)
    if telescopes:
        tel_shape = telescopes[0]
        for t in telescopes[1:]: tel_shape = tel_shape.fuse(t)
        return body.Shape.fuse(tel_shape)
    return body.Shape

def create_instrument_wispr():
    inst = INSTRUMENTS["WISPR"]
    body = make_box(inst["l"], inst["d"], inst["d"], cx=inst["cx"], cy=inst["cy"], cz=inst["cz"], label="WISPR_Body")
    set_mat(body, 'AL')
    cameras = []
    for i in range(inst["cameras"]):
        cam = make_cyl_x(inst["d"]/3, inst["l"]/4, cx=inst["cx"] + i*30, cy=inst["cy"], cz=inst["cz"] + i*20, label=f"WISPR_Cam_{i+1}")
        set_mat(cam, 'STEEL')
        cameras.append(cam.Shape)
    if cameras:
        cam_shape = cameras[0]
        for c in cameras[1:]: cam_shape = cam_shape.fuse(c)
        return body.Shape.fuse(cam_shape)
    return body.Shape

# ========================
# TPS avanzado con aislamiento multicapa
# ========================
def create_advanced_tps():
    tps_base = TPS_fused.Shape
    insul_layers = []
    x_start = nose_tip_x + TPS["tps_gap"] + TPS["sup_L"] + TPS["tps_t"]
    for i in range(TPS_ADVANCED["insul_layers"]):
        x = x_start + i * (TPS_ADVANCED["insul_t"] + TPS_ADVANCED["insul_gap"])
        layer = make_cyl_x(TPS["tps_d"] + 50, TPS_ADVANCED["insul_t"], cx=x, cy=0, cz=0, label=f"Insul_Layer_{i+1}")
        set_mat(layer, 'KEVLAR')
        insul_layers.append(layer.Shape)
    ceramic_coat = make_cyl_x(TPS["tps_d"] + 10, TPS_ADVANCED["ceramic_t"], cx=x_start - TPS_ADVANCED["ceramic_t"]/2, cy=0, cz=0, label="Ceramic_Coating")
    set_mat(ceramic_coat, 'CC')
    foam_core = make_cyl_x(TPS["tps_d"] - 20, TPS_ADVANCED["foam_t"], cx=x_start + TPS_ADVANCED["foam_t"]/2, cy=0, cz=0, label="Foam_Core")
    set_mat(foam_core, 'CC')
    beams = []
    for i in range(TPS_ADVANCED["support_beams"]):
        ang = i * (360.0 / TPS_ADVANCED["support_beams"])
        y = TPS["tps_d"]/2 * math.cos(math.radians(ang))
        z = TPS["tps_d"]/2 * math.sin(math.radians(ang))
        beam = make_cyl_x(TPS_ADVANCED["beam_r"]*2, TPS_ADVANCED["beam_l"], cx=nose_tip_x + TPS["tps_gap"] + TPS_ADVANCED["beam_l"]/2, cy=y, cz=z, label=f"TPS_Beam_{i+1}")
        set_mat(beam, 'STEEL')
        beams.append(beam.Shape)
    all_parts = [tps_base, ceramic_coat.Shape, foam_core.Shape] + insul_layers + beams
    fused = all_parts[0]
    for p in all_parts[1:]:
        fused = fused.fuse(p)
    return fused

# ========================
# Sistema de energía: Paneles solares retráctiles con refrigeración
# ========================
def create_energy_system():
    panels = []
    cooling_tubes = []
    for i in range(ENERGY["panels"]):
        # Panel retráctil
        panel = make_box(ENERGY["panel_t"], ENERGY["panel_w"], ENERGY["panel_h"],
                        cx=ENERGY["cx"] + i*ENERGY["retract_l"], cy=ENERGY["cy"], cz=ENERGY["cz"], label=f"Solar_Panel_{i+1}")
        set_mat(panel, 'CFRP')
        panels.append(panel.Shape)
        # Tubos de refrigeración
        for j in range(ENERGY["cooling_tubes"]):
            tube_y = ENERGY["cy"] + j * (ENERGY["panel_w"] / ENERGY["cooling_tubes"])
            tube = make_cyl_x(ENERGY["tube_r"]*2, ENERGY["panel_w"], cx=ENERGY["cx"] + i*ENERGY["retract_l"], cy=tube_y, cz=ENERGY["cz"], label=f"Cooling_Tube_{i+1}_{j+1}")
            set_mat(tube, 'COPPER')
            cooling_tubes.append(tube.Shape)
    all_parts = panels + cooling_tubes
    fused = all_parts[0]
    for p in all_parts[1:]:
        fused = fused.fuse(p)
    return fused

# ========================
# Comunicación y navegación
# ========================
def create_comm_nav():
    # Antena HGA
    hga_arm = make_cyl_x(COMM_NAV["hga_arm_r"]*2, COMM_NAV["hga_arm_l"], cx=COMM_NAV["hga_cx"] - COMM_NAV["hga_arm_l"]/2, cy=COMM_NAV["hga_cy"], cz=COMM_NAV["hga_cz"], label="HGA_Arm")
    set_mat(hga_arm, 'STEEL')
    hga_dish = make_cyl_x(COMM_NAV["hga_dish_d"], 20, cx=COMM_NAV["hga_cx"] - COMM_NAV["hga_arm_l"], cy=COMM_NAV["hga_cy"], cz=COMM_NAV["hga_cz"], label="HGA_Dish")
    set_mat(hga_dish, 'STEEL')
    hga = hga_arm.Shape.fuse(hga_dish.Shape)
    # Sensores solares
    sensors = []
    for i in range(COMM_NAV["solar_sensors"]):
        ang = i * (360.0 / COMM_NAV["solar_sensors"])
        y = COMM_NAV["sensor_r"] * math.cos(math.radians(ang))
        z = COMM_NAV["sensor_r"] * math.sin(math.radians(ang))
        sensor = make_cyl_x(COMM_NAV["sensor_d"], COMM_NAV["sensor_l"], cx=P["nose_len"] + 100, cy=y, cz=z, label=f"Solar_Sensor_{i+1}")
        set_mat(sensor, 'AL')
        sensors.append(sensor.Shape)
    all_parts = [hga] + sensors
    fused = all_parts[0]
    for p in all_parts[1:]:
        fused = fused.fuse(p)
    return fused

# ========================
# Estructura avanzada: Truss para soporte
# ========================
def create_advanced_structure():
    beams = []
    mounts = []
    for i in range(STRUCTURE["truss_beams"]):
        ang = i * (360.0 / STRUCTURE["truss_beams"])
        y = STRUCTURE["truss_r"] * math.cos(math.radians(ang))
        z = STRUCTURE["truss_r"] * math.sin(math.radians(ang))
        beam = make_cyl_x(STRUCTURE["truss_beam_r"]*2, STRUCTURE["truss_beam_l"], cx=P["nose_len"] + STRUCTURE["truss_beam_l"]/2, cy=y, cz=z, label=f"Truss_Beam_{i+1}")
        set_mat(beam, 'STEEL')
        beams.append(beam.Shape)
    for i in range(STRUCTURE["mounts"]):
        ang = i * (360.0 / STRUCTURE["mounts"])
        y = (P["rear_d"]/2 + 50) * math.cos(math.radians(ang))
        z = (P["rear_d"]/2 + 50) * math.sin(math.radians(ang))
        mount = make_cyl_x(STRUCTURE["mount_r"]*2, STRUCTURE["mount_h"], cx=P["nose_len"] + P["mid_len"] + P["rear_len"] - STRUCTURE["mount_h"]/2, cy=y, cz=z, label=f"Mount_{i+1}")
        set_mat(mount, 'STEEL')
        mounts.append(mount.Shape)
    all_parts = beams + mounts
    fused = all_parts[0]
    for p in all_parts[1:]:
        fused = fused.fuse(p)
    return fused

# ========================
# Fuselaje (sólidos)
# ========================
nose=make_cone_x(P["nose_base_d"],0.0,P["nose_len"],cx=P["nose_len"]/2.0,label="Nose"); set_mat(nose,'AL')
mid =make_cyl_x(P["mid_d"],P["mid_len"],cx=P["nose_len"]+P["mid_len"]/2.0,label="Mid");  set_mat(mid,'AL')
rear=make_cyl_x(P["rear_d"],P["rear_len"],cx=P["nose_len"]+P["mid_len"]+P["rear_len"]/2.0,label="Rear"); set_mat(rear,'AL')

# Casco hueco del fuselaje (si quieres sólido, usa fuse_fuselage_shape directamente)
fuse_fuselage_shape=nose.Shape.fuse(mid.Shape).fuse(rear.Shape)
hull=make_hollow_from_offset(fuse_fuselage_shape,P["hull_t"],label="Hull_Shell"); set_mat(hull,'AL')

# ========================
# TPS tipo Parker (pieza fusionada imprimible)
# ========================
nose_tip_x=P["nose_len"]
tps_support=make_cone_x(TPS["sup_d_base"],TPS["sup_d_tip"],TPS["sup_L"],
                        cx=nose_tip_x+TPS["tps_gap"]+TPS["sup_L"]/2.0,cy=0.0,cz=0.0,label="TPS_Support"); set_mat(tps_support,'STEEL')
tps_disk   =make_cyl_x(TPS["tps_d"],TPS["tps_t"],
                        cx=nose_tip_x+TPS["tps_gap"]+TPS["sup_L"]+TPS["tps_t"]/2.0,cy=0.0,cz=0.0,label="TPS_Shield");  set_mat(tps_disk,'CC')
TPS_fused_shape=fillet_between(tps_support.Shape,tps_disk.Shape, r=6.0)
TPS_fused=add_obj(TPS_fused_shape,"TPS_Assembly"); set_mat(TPS_fused,'CC')

# Sandwich opcional (caras C/C + núcleo Kevlar); se integra en ensamblado pero no se fusiona por defecto
face_t=6.0; core_t=max(0.0, TPS["tps_t"]-2*face_t)
if core_t>0:
    x_base=nose_tip_x+TPS["tps_gap"]+TPS["sup_L"]
    tps_face_outer=Part.makeCylinder(TPS["tps_d"]/2.0, face_t); tps_face_outer.Placement=App.Placement(App.Vector(x_base,0,0),rot_to_x())
    tps_core      =Part.makeCylinder(TPS["tps_d"]/2.0-5.0, core_t); tps_core.Placement=App.Placement(App.Vector(x_base+face_t,0,0),rot_to_x())
    tps_face_inner=Part.makeCylinder(TPS["tps_d"]/2.0, face_t); tps_face_inner.Placement=App.Placement(App.Vector(x_base+face_t+core_t,0,0),rot_to_x())
    face_out_obj=add_obj(tps_face_outer,"TPS_FaceOuter"); set_mat(face_out_obj,'CC')
    core_obj    =add_obj(tps_core,"TPS_Core");            set_mat(core_obj,'KEVLAR')
    face_in_obj =add_obj(tps_face_inner,"TPS_FaceInner"); set_mat(face_in_obj,'CC')

# ========================
# Ventanas y cabina
# ========================
win1=make_box(P["win_w"],P["win_th"],P["win_h"],cx=P["cockpit_x0"]+P["cockpit_l"]/2.0,cy=(P["mid_d"]/2.0)-P["win_th"]/2.0,cz=P["win_z"],label="Win_Right")
win2=make_box(P["win_w"],P["win_th"],P["win_h"],cx=P["cockpit_x0"]+P["cockpit_l"]/2.0,cy=-(P["mid_d"]/2.0)+P["win_th"]/2.0,cz=P["win_z"],label="Win_Left")
hull_cut=add_obj(hull.Shape.cut(win1.Shape).cut(win2.Shape),"Hull_Shell_Cut"); set_mat(hull_cut,'AL')

cockpit_box=Part.makeBox(P["cockpit_l"],P["cockpit_w"],P["cockpit_h"])
cockpit_box.Placement=App.Placement(App.Vector(P["cockpit_x0"],-P["cockpit_w"]/2.0,-P["cockpit_h"]/2.0),App.Rotation())
try: cockpit_f=cockpit_box.makeFillet(20.0,cockpit_box.Edges)
except Exception: cockpit_f=cockpit_box
cockpit=add_obj(cockpit_f,"Cockpit"); set_mat(cockpit,'AL')

# ========================
# Reactor, anillos, bobinas
# ========================
reactor=make_cyl_x(P["reactor_d"],P["reactor_l"],cx=P["reactor_cx"],label="ReactorCore"); set_mat(reactor,'STEEL')

rings=[]
x0=P["reactor_cx"]-P["reactor_l"]/2.0+P["ring_h"]/2.0
for i in range(P["ring_n"]):
    x=x0+i*P["ring_pitch"]
    ring=Part.makeTorus((P["ring_ro"]+P["ring_ri"])/2.0,(P["ring_ro"]-P["ring_ri"])/2.0)
    ring.Placement=App.Placement(App.Vector(x,0,0),rot_to_x())
    rings.append(ring)
rings_shape=rings[0]
for r in rings[1:]: rings_shape=rings_shape.fuse(r)
rings_obj=add_obj(rings_shape,"Reactor_Rings"); set_mat(rings_obj,'STEEL')

coils=[]
span=P["coil_span"]; cx0=P["reactor_cx"]-span/2.0
for i in range(P["coil_n"]):
    cx=cx0+i*(span/(max(1,(P["coil_n"]-1))))
    coil=sweep_rect_around_X(P["coil_R"],P["coil_rect_w"],P["coil_rect_h"],cx,0.0,0.0,0.0,0.0,label=f"Coil_{i+1}")
    coils.append(coil.Shape)
coils_shape=coils[0]
for c in coils[1:]: coils_shape=coils_shape.fuse(c)
coils_obj=add_obj(coils_shape,"Reactor_Coils"); set_mat(coils_obj,'COPPER')

# ========================
# Blindajes y tobera
# ========================
tw_len=P["tungsten_post_t"]; tw_ro=P["reactor_d"]/2.0; tw_ri=tw_ro-10.0
tw_tube=Part.makeCylinder(tw_ro,tw_len); tw_hole=Part.makeCylinder(tw_ri,tw_len+0.1)
tw_ring=tw_tube.cut(tw_hole)
tw_ring.Placement=App.Placement(App.Vector(P["reactor_cx"]+P["reactor_l"]/2.0-tw_len/2.0,0,0),rot_to_x())
tw_obj=add_obj(tw_ring,"Tungsten_Posterior"); set_mat(tw_obj,'STEEL')

noz=Part.makeCone(P["nozzle_throat_d"]/2.0,P["nozzle_exit_d"]/2.0,P["nozzle_l"])
noz.Placement=App.Placement(App.Vector(P["nozzle_cx"]-P["nozzle_l"]/2.0,0,0),rot_to_x())
noz_obj=add_obj(noz,"Magnetic_Nozzle"); set_mat(noz_obj,'STEEL')
try:
    filleted=fillet_between(rear.Shape,noz,P["nozzle_fillet_r"])
    nozzle_mount=add_obj(filleted,"Nozzle_Mount_Fillet"); set_mat(nozzle_mount,'STEEL')
except Exception:
    nozzle_mount=noz_obj

truss_list=[]
for k in range(P["truss_n"]):
    ang=k*(360.0/P["truss_n"])
    x_attach=P["nose_len"]+P["mid_len"]+P["rear_len"]-50.0
    y=P["truss_R_attach"]*math.cos(math.radians(ang))
    z=P["truss_R_attach"]*math.sin(math.radians(ang))
    L=300.0
    beam=Part.makeBox(L,P["truss_tube_w"],P["truss_tube_w"])
    beam.Placement=App.Placement(App.Vector(x_attach-L/2.0,y-P["truss_tube_w"]/2.0,z-P["truss_tube_w"]/2.0),App.Rotation())
    truss_list.append(beam)
truss_shape=truss_list[0]
for t in truss_list[1:]: truss_shape=truss_shape.fuse(t)
truss_obj=add_obj(truss_shape,"Nozzle_Truss"); set_mat(truss_obj,'STEEL')

mod_inner_r=P["reactor_d"]/2.0+P["moderator_gap"]; mod_outer_r=mod_inner_r+P["moderator_t"]
mod_len=P["reactor_l"]+P["moderator_over"]; mod_cx=P["reactor_cx"]
mod_outer=Part.makeCylinder(mod_outer_r,mod_len); mod_inner=Part.makeCylinder(mod_inner_r,mod_len+0.2)
mod_tube=mod_outer.cut(mod_inner)
mod_tube.Placement=App.Placement(App.Vector(mod_cx-mod_len/2.0,0,0),rot_to_x())
mod_obj=add_obj(mod_tube,"Shield_Moderator"); set_mat(mod_obj,'STEEL')

tn_ro=P["nozzle_exit_d"]/2.0+40.0; tn_ri=tn_ro-10.0; tn_len=20.0
tn_tube=Part.makeCylinder(tn_ro,tn_len); tn_hole=Part.makeCylinder(tn_ri,tn_len+0.1)
tn_ring=tn_tube.cut(tn_hole)
tn_ring.Placement=App.Placement(App.Vector(P["nozzle_cx"]+P["nozzle_l"]/2.0-tn_len/2.0,0,0),rot_to_x())
tn_obj=add_obj(tn_ring,"Tungsten_Nozzle_Rim"); set_mat(tn_obj,'STEEL')

# ========================
# Tanques laterales (sólidos)
# ========================
tank1=make_cyl_x(P["tank_d"],P["tank_l"],cx=P["tank_cx"],cy=P["tank_cy"],cz=P["tank_cz"],label="Tank_Right"); set_mat(tank1,'AL')
tank2=make_cyl_x(P["tank_d"],P["tank_l"],cx=P["tank_cx"],cy=-P["tank_cy"],cz=P["tank_cz"],label="Tank_Left"); set_mat(tank2,'AL')

# ========================
# Tren de aterrizaje (sólidos)
# ========================
def make_leg(x,y,z,L,d,label):
    shaft=Part.makeCylinder(d/4.0,L)
    foot=Part.makeCylinder(d/2.0,20.0)
    shaft.Placement=App.Placement(App.Vector(x-L/2.0,y,z),rot_to_x())
    foot.Placement=App.Placement(App.Vector(x+L/2.0-10.0,y,z-d/4.0),App.Rotation())
    return add_obj(shaft.fuse(foot),label)

leg_r = make_leg(P["leg_side_x1"], P["leg_side_y"], P["leg_front_z"], P["leg_L_fold"], P["leg_foot_d"], "Leg_Right_Front"); set_mat(leg_r,'STEEL')
leg_l = make_leg(P["leg_side_x1"],-P["leg_side_y"], P["leg_front_z"], P["leg_L_fold"], P["leg_foot_d"], "Leg_Left_Front"); set_mat(leg_l,'STEEL')
leg_r2= make_leg(P["leg_side_x2"], P["leg_side_y"], P["leg_front_z"], P["leg_L_fold"], P["leg_foot_d"], "Leg_Right_Rear"); set_mat(leg_r2,'STEEL')
leg_l2= make_leg(P["leg_side_x2"],-P["leg_side_y"], P["leg_front_z"], P["leg_L_fold"], P["leg_foot_d"], "Leg_Left_Rear"); set_mat(leg_l2,'STEEL')
leg_f = make_leg(P["leg_front_x"], P["leg_front_y"], P["leg_front_z"], P["leg_L_fold"], P["leg_foot_d"], "Leg_Nose"); set_mat(leg_f,'STEEL')

# ========================
# Alas / radiadores (alas sólidas)
# ========================
def make_trapezoid_wing(root_w,tip_w,chord,thickness=20.0,x0=1400.0,y0=0.0,z0=0.0,side=1,label="Wing"):
    x_le=x0; x_te=x0+chord; z_mid=z0
    p1=App.Vector(x_le,0,z_mid+root_w/2.0); p2=App.Vector(x_te,0,z_mid+root_w/2.0)
    p3=App.Vector(x_te,0,z_mid+tip_w/2.0); p4=App.Vector(x_le,0,z_mid+tip_w/2.0)
    wire=Part.makePolygon([p1,p2,p3,p4,p1]); face=Part.Face(wire)
    solid=face.extrude(App.Vector(0,side*(root_w-tip_w),0))
    slab=Part.makeBox(chord,thickness,(root_w+tip_w)/2.0)
    slab.Placement=App.Placement(App.Vector(x0,side*thickness/2.0,z0-(root_w+tip_w)/4.0),App.Rotation())
    return add_obj(solid.common(slab),label)

wing_r=make_trapezoid_wing(P["wing_root_w"],P["wing_tip_w"],P["wing_chord"],x0=P["nose_len"]+500.0,side= 1,label="Wing_Right"); set_mat(wing_r,'AL')
wing_l=make_trapezoid_wing(P["wing_root_w"],P["wing_tip_w"],P["wing_chord"],x0=P["nose_len"]+500.0,side=-1,label="Wing_Left");  set_mat(wing_l,'AL')

# Aleta vertical
def make_fin(h,base,thickness=20.0,x_base=None,z0=0.0,label="Fin"):
    if x_base is None: x_base=P["nose_len"]+P["mid_len"]+P["rear_len"]-300.0
    p1=App.Vector(x_base,0,z0); p2=App.Vector(x_base+base,0,z0); p3=App.Vector(x_base,0,z0+h)
    wire=Part.makePolygon([p1,p2,p3,p1]); face=Part.Face(wire)
    fin=face.extrude(App.Vector(0,thickness,0))
    fin.Placement=App.Placement(App.Vector(0,-thickness/2.0,0),App.Rotation())
    return add_obj(fin,label)
fin=make_fin(P["fin_h"],P["fin_base"],x_base=P["nose_len"]+P["mid_len"]+200.0,label="Fin_Vertical"); set_mat(fin,'AL')

# ========================
# Radiadores sólidos imprimibles (+Y / -Y)
# ========================
rads=[]
if RAD["x_start"] is None: RAD["x_start"]=P["nose_len"]+300.0
if RAD["gap_x"] is None:   RAD["gap_x"]=max(220.0, P["rad_panel_w"]*0.25)
for i in range(RAD["count_pairs"]):
    x = RAD["x_start"] + i*RAD["gap_x"]
    # +Y
    arm_r = Part.makeCylinder(RAD["arm_r"], RAD["arm_len"]); arm_r.Placement = App.Placement(App.Vector(x, P["mid_d"]/2.0, 0), rot_to_x())
    plate_r = Part.makeBox(RAD["th"], P["rad_panel_w"], P["rad_panel_h"])
    plate_r.Placement = App.Placement(App.Vector(x+RAD["arm_len"], P["mid_d"]/2.0+RAD["mount_gap_y"], -P["rad_panel_h"]/2.0), App.Rotation())
    rR = add_obj(arm_r.fuse(plate_r), f"Radiator_R_{i+1}"); set_mat(rR,'AL'); rads.append(rR)
    # -Y
    arm_l = Part.makeCylinder(RAD["arm_r"], RAD["arm_len"]); arm_l.Placement = App.Placement(App.Vector(x, -P["mid_d"]/2.0, 0), rot_to_x())
    plate_l = Part.makeBox(RAD["th"], P["rad_panel_w"], P["rad_panel_h"])
    plate_l.Placement = App.Placement(App.Vector(x+RAD["arm_len"], -(P["mid_d"]/2.0+RAD["mount_gap_y"]+P["rad_panel_w"]), -P["rad_panel_h"]/2.0), App.Rotation())
    rL = add_obj(arm_l.fuse(plate_l), f"Radiator_L_{i+1}"); set_mat(rL,'AL'); rads.append(rL)

# ========================
# Antena HGA y Panel lateral (sólidos simples)
# ========================
HGA={"arm_L":180.0,"arm_r":12.0,"dish_r":200.0,"dish_t":6.0,"x":P["nose_len"]+250.0,"y":-(P["mid_d"]/2.0+140.0),"z":120.0}
hga_arm=Part.makeCylinder(HGA["arm_r"], HGA["arm_L"]); hga_arm.Placement=App.Placement(App.Vector(HGA["x"]-HGA["arm_L"]/2.0,HGA["y"],HGA["z"]),rot_to_x())
hga_dish=Part.makeCylinder(HGA["dish_r"], HGA["dish_t"]); hga_dish.Placement=App.Placement(App.Vector(HGA["x"]-HGA["arm_L"],HGA["y"],HGA["z"]-HGA["dish_r"]/2.0),App.Rotation())
hga=add_obj(hga_arm.fuse(hga_dish),"HGA_Simple"); set_mat(hga,'STEEL')

SA={"arm_L":160.0,"arm_r":10.0,"L":700.0,"W":520.0,"H":18.0,"tilt_deg":8.0,"x":P["nose_len"]+260.0,"y":P["mid_d"]/2.0+140.0,"z":-60.0}
sa_arm=Part.makeCylinder(SA["arm_r"], SA["arm_L"]); sa_arm.Placement=App.Placement(App.Vector(SA["x"]-SA["arm_L"]/2.0,SA["y"],SA["z"]),rot_to_x())
sa_panel=Part.makeBox(SA["L"], SA["W"], SA["H"]); sa_panel.Placement=App.Placement(App.Vector(SA["x"]-SA["L"]/2.0,SA["y"]-SA["W"]/2.0,SA["z"]-SA["H"]/2.0),App.Rotation(App.Vector(1,0,0), SA["tilt_deg"]))
sa=add_obj(sa_arm.fuse(sa_panel),"Solar_Array_Simple"); set_mat(sa,'CFRP')

# ========================
# Instrumentos científicos
# ========================
fields_shape = create_instrument_fields()
fields_obj = add_obj(fields_shape, "FIELDS_Instrument")

sweap_shape = create_instrument_sweap()
sweap_obj = add_obj(sweap_shape, "SWEAP_Instrument")

isis_shape = create_instrument_isis()
isis_obj = add_obj(isis_shape, "ISIS_Instrument")

wispr_shape = create_instrument_wispr()
wispr_obj = add_obj(wispr_shape, "WISPR_Instrument")

# ========================
# TPS avanzado
# ========================
tps_advanced_shape = create_advanced_tps()
tps_advanced_obj = add_obj(tps_advanced_shape, "TPS_Advanced")

# ========================
# Sistema de energía
# ========================
energy_shape = create_energy_system()
energy_obj = add_obj(energy_shape, "Energy_System")

# ========================
# Comunicación y navegación
# ========================
comm_nav_shape = create_comm_nav()
comm_nav_obj = add_obj(comm_nav_shape, "Comm_Nav_System")

# ========================
# Estructura avanzada
# ========================
structure_shape = create_advanced_structure()
structure_obj = add_obj(structure_shape, "Advanced_Structure")

# ========================
# Ensamblado total fusionado (pieza única imprimible)
# ========================
to_fuse = [
    hull_cut, cockpit, tps_advanced_obj, nose, mid, rear,
    reactor, rings_obj, coils_obj, mod_obj, tw_obj,
    (nozzle_mount if 'nozzle_mount' in globals() else noz_obj),
    tn_obj, truss_obj, tank1, tank2,
    leg_r, leg_l, leg_r2, leg_l2, leg_f,
    wing_r, wing_l, fin, hga, sa,
    fields_obj, sweap_obj, isis_obj, wispr_obj,
    energy_obj, comm_nav_obj, structure_obj
] + rads

# Elimina posibles None y duplica protección
to_fuse = [o for o in to_fuse if o and hasattr(o,'Shape')]

fused = to_fuse[0].Shape
for o in to_fuse[1:]:
    try:
        fused = fused.fuse(o.Shape)
    except Exception:
        pass

Assembly_Fused = add_obj(fused, "Assembly_Fused")  # Sólido único imprimible
set_mat(Assembly_Fused, 'AL')  # material global visual (las subpropiedades ya están en piezas individuales)

# Opcional: compuesto no fusionado (solo visual)
compound = Part.Compound([o.Shape for o in to_fuse])
add_obj(compound, "Assembly_Compound")

doc.recompute()
print("Ensamblado mejorado completado con instrumentos científicos, TPS avanzado, sistema de energía, comunicación/navegación y estructura mejorada. Assembly_Fused (única pieza) y Assembly_Compound (visual). Listo para exportar STL/STEP.")

DFD_GRIS_mejora.py
# Macro FreeCAD: Direct Fusion Drive con TPS tipo Parker, ensamblado e imprimible (todo junto)
# Autor: Víctor + Copilot
# Unidades: mm, eje longitudinal = X

import FreeCAD as App, FreeCADGui as Gui, Part, math

doc_name="Direct_Fusion_Drive"
if App.ActiveDocument is None or App.ActiveDocument.Label!=doc_name:
    App.newDocument(doc_name)
doc=App.ActiveDocument

# ========================
# Parámetros base DFD
# ========================
P={
    "nose_len":800.0,"nose_base_d":600.0,
    "mid_len":1400.0,"mid_d":900.0,
    "rear_len":800.0,"rear_d":1200.0,
    "hull_t":10.0,
    "cockpit_w":900.0,"cockpit_h":400.0,"cockpit_l":600.0,"cockpit_x0":600.0,
    "win_w":600.0,"win_h":250.0,"win_th":20.0,
    "win_y_off":0.5*(900.0/2.0-250.0/2.0),"win_z":0.0,
    "reactor_d":800.0,"reactor_l":900.0,"reactor_cx":2600.0,
    "ring_h":30.0,"ring_ro":420.0,"ring_ri":380.0,"ring_n":6,"ring_pitch":150.0,
    "coil_rect_w":80.0,"coil_rect_h":80.0,"coil_R":440.0,"coil_n":4,"coil_span":800.0,
    "moderator_t":100.0,"moderator_gap":20.0,"moderator_over":200.0,
    "tungsten_post_t":10.0,
    "nozzle_throat_d":300.0,"nozzle_exit_d":900.0,"nozzle_l":700.0,"nozzle_cx":2850.0,"nozzle_fillet_r":40.0,
    "truss_n":3,"truss_tube_w":80.0,"truss_R_attach":550.0,
    "tank_d":300.0,"tank_l":700.0,"tank_cx":1600.0,"tank_cy":300.0,"tank_cz":-150.0,
    "leg_L_fold":400.0,"leg_L_ext":600.0,"leg_foot_d":180.0,
    "leg_side_x1":1050.0,"leg_side_x2":1950.0,"leg_side_y":600.0,
    "leg_front_x":400.0,"leg_front_y":0.0,"leg_front_z":-(900.0/2.0)+50.0,
    "wing_root_w":600.0,"wing_tip_w":150.0,"wing_chord":450.0,
    "fin_h":400.0,"fin_base":200.0,
    "rad_panel_w":800.0,"rad_panel_h":600.0,"rad_panel_n":5
}

# ========================
# TPS tipo Parker y Radiadores
# ========================
TPS={"tps_d":2400.0,"tps_t":100.0,"tps_gap":120.0,"sup_L":280.0,"sup_d_base":900.0,"sup_d_tip":600.0}
RAD={"th":4.0,"mount_gap_y":30.0,"x_start":None,"gap_x":None,"count_pairs":3,"span_x":220.0,"arm_len":60.0,"arm_r":10.0}

# ========================
# Materiales
# ========================
MAT={
    'AL':{'name':'AA-2xxx','rho':2700.0,'E':72e9,'nu':0.33,'type':'isotropic'},
    'STEEL':{'name':'SS-304','rho':8000.0,'E':200e9,'nu':0.30,'type':'isotropic'},
    'COPPER':{'name':'Copper','rho':8960.0,'E':110e9,'nu':0.34,'type':'isotropic'},
    'CFRP':{'name':'CFRP','rho':1550.0,'Ex':130e9,'Ey':10e9,'Ez':10e9,'nu_xy':0.25,'type':'orthotropic'},
    'CC':{'name':'C/C TPS','rho':1600.0,'Ex':70e9,'Ey':70e9,'Ez':10e9,'nu_xy':0.2,'type':'orthotropic'},
    'KEVLAR':{'name':'Kevlar','rho':1440.0,'Ex':70e9,'Ey':5e9,'Ez':5e9,'nu_xy':0.27,'type':'orthotropic'}
}

# ========================
# Utilidades
# ========================
X_AXIS=App.Vector(1,0,0);Y_AXIS=App.Vector(0,1,0);Z_AXIS=App.Vector(0,0,1)
def rot_to_x():return App.Rotation(Y_AXIS,90)
def add_obj(shape,label):obj=doc.addObject("Part::Feature",label);obj.Shape=shape;return obj
def set_mat(obj,mat): 
    if not obj:return
    m=MAT.get(mat,None)if isinstance(mat,str)else mat
    if not m:return
    obj.addProperty("App::PropertyString","Material","Meta","").Material=m.get('name','')
    obj.addProperty("App::PropertyMap","MaterialData","Meta","").MaterialData={k:str(v)for k,v in m.items()}
    obj.addProperty("App::PropertyFloat","Density","Meta","").Density=m.get('rho',0.0)
def make_cyl_x(d,L,cx=0.0,cy=0.0,cz=0.0,label="CylX"):
    r=d/2.0;cyl=Part.makeCylinder(r,L);cyl.Placement=App.Placement(App.Vector(cx-L/2.0,cy,cz),rot_to_x());return add_obj(cyl,label)
def make_cone_x(d1,d2,L,cx=0.0,cy=0.0,cz=0.0,label="ConeX"):
    r1=d1/2.0;r2=d2/2.0;cone=Part.makeCone(r1,r2,L);cone.Placement=App.Placement(App.Vector(cx-L/2.0,cy,cz),rot_to_x());return add_obj(cone,label)
def make_torus_x(R,r,cx=0.0,cy=0.0,cz=0.0,label="TorusX"):
    tor=Part.makeTorus(R,r);tor.Placement=App.Placement(App.Vector(cx,cy,cz),rot_to_x());return add_obj(tor,label)
def make_box(w,d,h,cx=0.0,cy=0.0,cz=0.0,label="Box"):
    b=Part.makeBox(w,d,h);b.Placement=App.Placement(App.Vector(cx-w/2.0,cy-d/2.0,cz-h/2.0),App.Rotation());return add_obj(b,label)
def make_hollow_from_offset(outer_shape,t,label="Shell"): 
    try:
        inner=outer_shape.makeOffsetShape(-t,0.01,join=2,fill=True)
        shell=outer_shape.cut(inner)
        return add_obj(shell,label)
    except Exception:
        return add_obj(outer_shape,label+"_fallback")
def fillet_between(shpA,shpB,r):
    fused=shpA.fuse(shpB)
    try:
        edges=[e for e in fused.Edges if e.Length>30 and e.Length<10000]
        new=fused.makeFillet(r,edges);return new
    except Exception:
        return fused
def sweep_rect_around_X(R,rw,rh,cx,cy,cz,ax0,ax1,label="CoilSweep"):
    circ=Part.makeCircle(R,App.Vector(cx,cy,cz),X_AXIS);path=Part.Wire([circ])
    p0=App.Vector(0,-rw/2.0,-rh/2.0);p1=App.Vector(0,rw/2.0,-rh/2.0)
    p2=App.Vector(0,rw/2.0,rh/2.0);p3=App.Vector(0,-rw/2.0,rh/2.0)
    e1=Part.makeLine(p0,p1);e2=Part.makeLine(p1,p2);e3=Part.makeLine(p2,p3);e4=Part.makeLine(p3,p0)
    prof=Part.Wire([e1,e2,e3,e4])
    prof.Placement=App.Placement(App.Vector(cx,cy,cz),App.Rotation(X_AXIS,0))
    sweep=Part.Wire(path).makePipeShell([prof],True,True)
    return add_obj(sweep,label)

# ========================
# Fuselaje (sólidos)
# ========================
nose=make_cone_x(P["nose_base_d"],0.0,P["nose_len"],cx=P["nose_len"]/2.0,label="Nose"); set_mat(nose,'AL')
mid =make_cyl_x(P["mid_d"],P["mid_len"],cx=P["nose_len"]+P["mid_len"]/2.0,label="Mid");  set_mat(mid,'AL')
rear=make_cyl_x(P["rear_d"],P["rear_len"],cx=P["nose_len"]+P["mid_len"]+P["rear_len"]/2.0,label="Rear"); set_mat(rear,'AL')

# Casco hueco del fuselaje (si quieres sólido, usa fuse_fuselage_shape directamente)
fuse_fuselage_shape=nose.Shape.fuse(mid.Shape).fuse(rear.Shape)
hull=make_hollow_from_offset(fuse_fuselage_shape,P["hull_t"],label="Hull_Shell"); set_mat(hull,'AL')

# ========================
# TPS tipo Parker (pieza fusionada imprimible)
# ========================
nose_tip_x=P["nose_len"]
tps_support=make_cone_x(TPS["sup_d_base"],TPS["sup_d_tip"],TPS["sup_L"],
                        cx=nose_tip_x+TPS["tps_gap"]+TPS["sup_L"]/2.0,cy=0.0,cz=0.0,label="TPS_Support"); set_mat(tps_support,'STEEL')
tps_disk   =make_cyl_x(TPS["tps_d"],TPS["tps_t"],
                        cx=nose_tip_x+TPS["tps_gap"]+TPS["sup_L"]+TPS["tps_t"]/2.0,cy=0.0,cz=0.0,label="TPS_Shield");  set_mat(tps_disk,'CC')
TPS_fused_shape=fillet_between(tps_support.Shape,tps_disk.Shape, r=6.0)
TPS_fused=add_obj(TPS_fused_shape,"TPS_Assembly"); set_mat(TPS_fused,'CC')

# Sandwich opcional (caras C/C + núcleo Kevlar); se integra en ensamblado pero no se fusiona por defecto
face_t=6.0; core_t=max(0.0, TPS["tps_t"]-2*face_t)
if core_t>0:
    x_base=nose_tip_x+TPS["tps_gap"]+TPS["sup_L"]
    tps_face_outer=Part.makeCylinder(TPS["tps_d"]/2.0, face_t); tps_face_outer.Placement=App.Placement(App.Vector(x_base,0,0),rot_to_x())
    tps_core      =Part.makeCylinder(TPS["tps_d"]/2.0-5.0, core_t); tps_core.Placement=App.Placement(App.Vector(x_base+face_t,0,0),rot_to_x())
    tps_face_inner=Part.makeCylinder(TPS["tps_d"]/2.0, face_t); tps_face_inner.Placement=App.Placement(App.Vector(x_base+face_t+core_t,0,0),rot_to_x())
    face_out_obj=add_obj(tps_face_outer,"TPS_FaceOuter"); set_mat(face_out_obj,'CC')
    core_obj    =add_obj(tps_core,"TPS_Core");            set_mat(core_obj,'KEVLAR')
    face_in_obj =add_obj(tps_face_inner,"TPS_FaceInner"); set_mat(face_in_obj,'CC')

# ========================
# Ventanas y cabina
# ========================
win1=make_box(P["win_w"],P["win_th"],P["win_h"],cx=P["cockpit_x0"]+P["cockpit_l"]/2.0,cy=(P["mid_d"]/2.0)-P["win_th"]/2.0,cz=P["win_z"],label="Win_Right")
win2=make_box(P["win_w"],P["win_th"],P["win_h"],cx=P["cockpit_x0"]+P["cockpit_l"]/2.0,cy=-(P["mid_d"]/2.0)+P["win_th"]/2.0,cz=P["win_z"],label="Win_Left")
hull_cut=add_obj(hull.Shape.cut(win1.Shape).cut(win2.Shape),"Hull_Shell_Cut"); set_mat(hull_cut,'AL')

cockpit_box=Part.makeBox(P["cockpit_l"],P["cockpit_w"],P["cockpit_h"])
cockpit_box.Placement=App.Placement(App.Vector(P["cockpit_x0"],-P["cockpit_w"]/2.0,-P["cockpit_h"]/2.0),App.Rotation())
try: cockpit_f=cockpit_box.makeFillet(20.0,cockpit_box.Edges)
except Exception: cockpit_f=cockpit_box
cockpit=add_obj(cockpit_f,"Cockpit"); set_mat(cockpit,'AL')

# ========================
# Reactor, anillos, bobinas
# ========================
reactor=make_cyl_x(P["reactor_d"],P["reactor_l"],cx=P["reactor_cx"],label="ReactorCore"); set_mat(reactor,'STEEL')

rings=[]
x0=P["reactor_cx"]-P["reactor_l"]/2.0+P["ring_h"]/2.0
for i in range(P["ring_n"]):
    x=x0+i*P["ring_pitch"]
    ring=Part.makeTorus((P["ring_ro"]+P["ring_ri"])/2.0,(P["ring_ro"]-P["ring_ri"])/2.0)
    ring.Placement=App.Placement(App.Vector(x,0,0),rot_to_x())
    rings.append(ring)
rings_shape=rings[0]
for r in rings[1:]: rings_shape=rings_shape.fuse(r)
rings_obj=add_obj(rings_shape,"Reactor_Rings"); set_mat(rings_obj,'STEEL')

coils=[]
span=P["coil_span"]; cx0=P["reactor_cx"]-span/2.0
for i in range(P["coil_n"]):
    cx=cx0+i*(span/(max(1,(P["coil_n"]-1))))
    coil=sweep_rect_around_X(P["coil_R"],P["coil_rect_w"],P["coil_rect_h"],cx,0.0,0.0,0.0,0.0,label=f"Coil_{i+1}")
    coils.append(coil.Shape)
coils_shape=coils[0]
for c in coils[1:]: coils_shape=coils_shape.fuse(c)
coils_obj=add_obj(coils_shape,"Reactor_Coils"); set_mat(coils_obj,'COPPER')

# ========================
# Blindajes y tobera
# ========================
tw_len=P["tungsten_post_t"]; tw_ro=P["reactor_d"]/2.0; tw_ri=tw_ro-10.0
tw_tube=Part.makeCylinder(tw_ro,tw_len); tw_hole=Part.makeCylinder(tw_ri,tw_len+0.1)
tw_ring=tw_tube.cut(tw_hole)
tw_ring.Placement=App.Placement(App.Vector(P["reactor_cx"]+P["reactor_l"]/2.0-tw_len/2.0,0,0),rot_to_x())
tw_obj=add_obj(tw_ring,"Tungsten_Posterior"); set_mat(tw_obj,'STEEL')

noz=Part.makeCone(P["nozzle_throat_d"]/2.0,P["nozzle_exit_d"]/2.0,P["nozzle_l"])
noz.Placement=App.Placement(App.Vector(P["nozzle_cx"]-P["nozzle_l"]/2.0,0,0),rot_to_x())
noz_obj=add_obj(noz,"Magnetic_Nozzle"); set_mat(noz_obj,'STEEL')
try:
    filleted=fillet_between(rear.Shape,noz,P["nozzle_fillet_r"])
    nozzle_mount=add_obj(filleted,"Nozzle_Mount_Fillet"); set_mat(nozzle_mount,'STEEL')
except Exception:
    nozzle_mount=noz_obj

truss_list=[]
for k in range(P["truss_n"]):
    ang=k*(360.0/P["truss_n"])
    x_attach=P["nose_len"]+P["mid_len"]+P["rear_len"]-50.0
    y=P["truss_R_attach"]*math.cos(math.radians(ang))
    z=P["truss_R_attach"]*math.sin(math.radians(ang))
    L=300.0
    beam=Part.makeBox(L,P["truss_tube_w"],P["truss_tube_w"])
    beam.Placement=App.Placement(App.Vector(x_attach-L/2.0,y-P["truss_tube_w"]/2.0,z-P["truss_tube_w"]/2.0),App.Rotation())
    truss_list.append(beam)
truss_shape=truss_list[0]
for t in truss_list[1:]: truss_shape=truss_shape.fuse(t)
truss_obj=add_obj(truss_shape,"Nozzle_Truss"); set_mat(truss_obj,'STEEL')

mod_inner_r=P["reactor_d"]/2.0+P["moderator_gap"]; mod_outer_r=mod_inner_r+P["moderator_t"]
mod_len=P["reactor_l"]+P["moderator_over"]; mod_cx=P["reactor_cx"]
mod_outer=Part.makeCylinder(mod_outer_r,mod_len); mod_inner=Part.makeCylinder(mod_inner_r,mod_len+0.2)
mod_tube=mod_outer.cut(mod_inner)
mod_tube.Placement=App.Placement(App.Vector(mod_cx-mod_len/2.0,0,0),rot_to_x())
mod_obj=add_obj(mod_tube,"Shield_Moderator"); set_mat(mod_obj,'STEEL')

tn_ro=P["nozzle_exit_d"]/2.0+40.0; tn_ri=tn_ro-10.0; tn_len=20.0
tn_tube=Part.makeCylinder(tn_ro,tn_len); tn_hole=Part.makeCylinder(tn_ri,tn_len+0.1)
tn_ring=tn_tube.cut(tn_hole)
tn_ring.Placement=App.Placement(App.Vector(P["nozzle_cx"]+P["nozzle_l"]/2.0-tn_len/2.0,0,0),rot_to_x())
tn_obj=add_obj(tn_ring,"Tungsten_Nozzle_Rim"); set_mat(tn_obj,'STEEL')

# ========================
# Tanques laterales (sólidos)
# ========================
tank1=make_cyl_x(P["tank_d"],P["tank_l"],cx=P["tank_cx"],cy=P["tank_cy"],cz=P["tank_cz"],label="Tank_Right"); set_mat(tank1,'AL')
tank2=make_cyl_x(P["tank_d"],P["tank_l"],cx=P["tank_cx"],cy=-P["tank_cy"],cz=P["tank_cz"],label="Tank_Left"); set_mat(tank2,'AL')

# ========================
# Tren de aterrizaje (sólidos)
# ========================
def make_leg(x,y,z,L,d,label):
    shaft=Part.makeCylinder(d/4.0,L)
    foot=Part.makeCylinder(d/2.0,20.0)
    shaft.Placement=App.Placement(App.Vector(x-L/2.0,y,z),rot_to_x())
    foot.Placement=App.Placement(App.Vector(x+L/2.0-10.0,y,z-d/4.0),App.Rotation())
    return add_obj(shaft.fuse(foot),label)

leg_r = make_leg(P["leg_side_x1"], P["leg_side_y"], P["leg_front_z"], P["leg_L_fold"], P["leg_foot_d"], "Leg_Right_Front"); set_mat(leg_r,'STEEL')
leg_l = make_leg(P["leg_side_x1"],-P["leg_side_y"], P["leg_front_z"], P["leg_L_fold"], P["leg_foot_d"], "Leg_Left_Front"); set_mat(leg_l,'STEEL')
leg_r2= make_leg(P["leg_side_x2"], P["leg_side_y"], P["leg_front_z"], P["leg_L_fold"], P["leg_foot_d"], "Leg_Right_Rear"); set_mat(leg_r2,'STEEL')
leg_l2= make_leg(P["leg_side_x2"],-P["leg_side_y"], P["leg_front_z"], P["leg_L_fold"], P["leg_foot_d"], "Leg_Left_Rear"); set_mat(leg_l2,'STEEL')
leg_f = make_leg(P["leg_front_x"], P["leg_front_y"], P["leg_front_z"], P["leg_L_fold"], P["leg_foot_d"], "Leg_Nose"); set_mat(leg_f,'STEEL')

# ========================
# Alas / radiadores (alas sólidas)
# ========================
def make_trapezoid_wing(root_w,tip_w,chord,thickness=20.0,x0=1400.0,y0=0.0,z0=0.0,side=1,label="Wing"):
    x_le=x0; x_te=x0+chord; z_mid=z0
    p1=App.Vector(x_le,0,z_mid+root_w/2.0); p2=App.Vector(x_te,0,z_mid+root_w/2.0)
    p3=App.Vector(x_te,0,z_mid+tip_w/2.0); p4=App.Vector(x_le,0,z_mid+tip_w/2.0)
    wire=Part.makePolygon([p1,p2,p3,p4,p1]); face=Part.Face(wire)
    solid=face.extrude(App.Vector(0,side*(root_w-tip_w),0))
    slab=Part.makeBox(chord,thickness,(root_w+tip_w)/2.0)
    slab.Placement=App.Placement(App.Vector(x0,side*thickness/2.0,z0-(root_w+tip_w)/4.0),App.Rotation())
    return add_obj(solid.common(slab),label)

wing_r=make_trapezoid_wing(P["wing_root_w"],P["wing_tip_w"],P["wing_chord"],x0=P["nose_len"]+500.0,side= 1,label="Wing_Right"); set_mat(wing_r,'AL')
wing_l=make_trapezoid_wing(P["wing_root_w"],P["wing_tip_w"],P["wing_chord"],x0=P["nose_len"]+500.0,side=-1,label="Wing_Left");  set_mat(wing_l,'AL')

# Aleta vertical
def make_fin(h,base,thickness=20.0,x_base=None,z0=0.0,label="Fin"):
    if x_base is None: x_base=P["nose_len"]+P["mid_len"]+P["rear_len"]-300.0
    p1=App.Vector(x_base,0,z0); p2=App.Vector(x_base+base,0,z0); p3=App.Vector(x_base,0,z0+h)
    wire=Part.makePolygon([p1,p2,p3,p1]); face=Part.Face(wire)
    fin=face.extrude(App.Vector(0,thickness,0))
    fin.Placement=App.Placement(App.Vector(0,-thickness/2.0,0),App.Rotation())
    return add_obj(fin,label)
fin=make_fin(P["fin_h"],P["fin_base"],x_base=P["nose_len"]+P["mid_len"]+200.0,label="Fin_Vertical"); set_mat(fin,'AL')

# ========================
# Radiadores sólidos imprimibles (+Y / -Y)
# ========================
rads=[]
if RAD["x_start"] is None: RAD["x_start"]=P["nose_len"]+300.0
if RAD["gap_x"] is None:   RAD["gap_x"]=max(220.0, P["rad_panel_w"]*0.25)
for i in range(RAD["count_pairs"]):
    x = RAD["x_start"] + i*RAD["gap_x"]
    # +Y
    arm_r = Part.makeCylinder(RAD["arm_r"], RAD["arm_len"]); arm_r.Placement = App.Placement(App.Vector(x, P["mid_d"]/2.0, 0), rot_to_x())
    plate_r = Part.makeBox(RAD["th"], P["rad_panel_w"], P["rad_panel_h"])
    plate_r.Placement = App.Placement(App.Vector(x+RAD["arm_len"], P["mid_d"]/2.0+RAD["mount_gap_y"], -P["rad_panel_h"]/2.0), App.Rotation())
    rR = add_obj(arm_r.fuse(plate_r), f"Radiator_R_{i+1}"); set_mat(rR,'AL'); rads.append(rR)
    # -Y
    arm_l = Part.makeCylinder(RAD["arm_r"], RAD["arm_len"]); arm_l.Placement = App.Placement(App.Vector(x, -P["mid_d"]/2.0, 0), rot_to_x())
    plate_l = Part.makeBox(RAD["th"], P["rad_panel_w"], P["rad_panel_h"])
    plate_l.Placement = App.Placement(App.Vector(x+RAD["arm_len"], -(P["mid_d"]/2.0+RAD["mount_gap_y"]+P["rad_panel_w"]), -P["rad_panel_h"]/2.0), App.Rotation())
    rL = add_obj(arm_l.fuse(plate_l), f"Radiator_L_{i+1}"); set_mat(rL,'AL'); rads.append(rL)

# ========================
# Antena HGA y Panel lateral (sólidos simples)
# ========================
HGA={"arm_L":180.0,"arm_r":12.0,"dish_r":200.0,"dish_t":6.0,"x":P["nose_len"]+250.0,"y":-(P["mid_d"]/2.0+140.0),"z":120.0}
hga_arm=Part.makeCylinder(HGA["arm_r"], HGA["arm_L"]); hga_arm.Placement=App.Placement(App.Vector(HGA["x"]-HGA["arm_L"]/2.0,HGA["y"],HGA["z"]),rot_to_x())
hga_dish=Part.makeCylinder(HGA["dish_r"], HGA["dish_t"]); hga_dish.Placement=App.Placement(App.Vector(HGA["x"]-HGA["arm_L"],HGA["y"],HGA["z"]-HGA["dish_r"]/2.0),App.Rotation())
hga=add_obj(hga_arm.fuse(hga_dish),"HGA_Simple"); set_mat(hga,'STEEL')

SA={"arm_L":160.0,"arm_r":10.0,"L":700.0,"W":520.0,"H":18.0,"tilt_deg":8.0,"x":P["nose_len"]+260.0,"y":P["mid_d"]/2.0+140.0,"z":-60.0}
sa_arm=Part.makeCylinder(SA["arm_r"], SA["arm_L"]); sa_arm.Placement=App.Placement(App.Vector(SA["x"]-SA["arm_L"]/2.0,SA["y"],SA["z"]),rot_to_x())
sa_panel=Part.makeBox(SA["L"], SA["W"], SA["H"]); sa_panel.Placement=App.Placement(App.Vector(SA["x"]-SA["L"]/2.0,SA["y"]-SA["W"]/2.0,SA["z"]-SA["H"]/2.0),App.Rotation(App.Vector(1,0,0), SA["tilt_deg"]))
sa=add_obj(sa_arm.fuse(sa_panel),"Solar_Array_Simple"); set_mat(sa,'CFRP')

# ========================
# Ensamblado total fusionado (pieza única imprimible)
# ========================
to_fuse = [
    hull_cut, cockpit, TPS_fused, nose, mid, rear,
    reactor, rings_obj, coils_obj, mod_obj, tw_obj,
    (nozzle_mount if 'nozzle_mount' in globals() else noz_obj),
    tn_obj, truss_obj, tank1, tank2,
    leg_r, leg_l, leg_r2, leg_l2, leg_f,
    wing_r, wing_l, fin, hga, sa
] + rads

# Elimina posibles None y duplica protección
to_fuse = [o for o in to_fuse if o and hasattr(o,'Shape')]

fused = to_fuse[0].Shape
for o in to_fuse[1:]:
    try:
        fused = fused.fuse(o.Shape)
    except Exception:
        pass

Assembly_Fused = add_obj(fused, "Assembly_Fused")  # Sólido único imprimible
set_mat(Assembly_Fused, 'AL')  # material global visual (las subpropiedades ya están en piezas individuales)

# Opcional: compuesto no fusionado (solo visual)
compound = Part.Compound([o.Shape for o in to_fuse])
add_obj(compound, "Assembly_Compound")

doc.recompute()
print("Ensamblado completado: Assembly_Fused (única pieza) y Assembly_Compound (visual). Listo para exportar STL/STEP.")
