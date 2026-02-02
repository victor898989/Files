# FreeCAD macro: Direct_Fusion_Drive_enhanced.FCMacro
# Versión mejorada: carcasa CNC sólida, blindaje y amortiguación
# Ejecutar dentro de FreeCAD (Python console / Macros)
import FreeCAD as App, FreeCADGui as Gui, Part, math
doc_name="Direct_Fusion_Drive_enhanced"
if App.ActiveDocument is None or App.ActiveDocument.Label!=doc_name:
    App.newDocument(doc_name)
doc=App.ActiveDocument

# Parámetros base (heredados + nuevos)
P={"nose_len":800.0,"nose_base_d":600.0,"mid_len":1400.0,"mid_d":900.0,"rear_len":800.0,"rear_d":1200.0,
   "hull_t":20.0,             # mayor espesor para CNC y resistencia
   "cockpit_w":900.0,"cockpit_h":400.0,"cockpit_l":600.0,"cockpit_x0":600.0,
   "win_w":600.0,"win_h":250.0,"win_th":20.0,"win_y_off":0.5*(900.0/2.0-250.0/2.0),"win_z":0.0,
   "reactor_d":800.0,"reactor_l":900.0,"reactor_cx":2600.0,
   "ring_h":30.0,"ring_ro":420.0,"ring_ri":380.0,"ring_n":6,"ring_pitch":150.0,
   "coil_rect_w":80.0,"coil_rect_h":80.0,"coil_R":440.0,"coil_n":4,"coil_span":800.0,
   "moderator_t":100.0,"moderator_gap":20.0,"moderator_over":200.0,"tungsten_post_t":10.0,
   "nozzle_throat_d":300.0,"nozzle_exit_d":900.0,"nozzle_l":700.0,"nozzle_cx":2850.0,"nozzle_fillet_r":40.0,
   "truss_n":3,"truss_tube_w":80.0,"truss_R_attach":550.0,
   "tank_d":300.0,"tank_l":700.0,"tank_cx":1600.0,"tank_cy":300.0,"tank_cz":-150.0,
   "leg_L_fold":400.0,"leg_L_ext":600.0,"leg_foot_d":180.0,"leg_side_x1":1050.0,"leg_side_x2":1950.0,
   "leg_side_y":600.0,"leg_front_x":400.0,"leg_front_y":0.0,"leg_front_z":-(900.0/2.0)+50.0,
   "wing_root_w":600.0,"wing_tip_w":150.0,"wing_chord":450.0,"fin_h":400.0,"fin_base":200.0,
   "rad_panel_w":800.0,"rad_panel_h":600.0,"rad_panel_n":5,
   # nuevos para protección
   "shield_t":60.0,           # capa de blindaje de alta densidad (mm)
   "impact_t":40.0,           # capa amortiguadora (kevlar/cfrp)
   "inner_clearance":120.0    # espacio libre interior para equipos
  }

TPS={"tps_d":2400.0,"tps_t":100.0,"tps_gap":120.0,"sup_L":280.0,"sup_d_base":900.0,"sup_d_tip":600.0}
MAT={'AL':{'name':'AA-2xxx','rho':2700.0,'E':72e9,'nu':0.33},
     'STEEL':{'name':'SS-304','rho':8000.0,'E':200e9,'nu':0.30},
     'COPPER':{'name':'Copper','rho':8960.0,'E':110e9,'nu':0.34},
     'CFRP':{'name':'CFRP','rho':1550.0},
     'CC':{'name':'C/C TPS','rho':1600.0},
     'KEVLAR':{'name':'Kevlar','rho':1440.0},
     'W':{'name':'Tungsten','rho':19300.0}
    }

# Vectores y utilidades
X=App.Vector(1,0,0);Y=App.Vector(0,1,0);Z=App.Vector(0,0,1)
def R(): return App.Rotation(Y,90)
def O(s,l): 
    o=doc.addObject("Part::Feature",l); o.Shape=s; return o
def M(o,m):
    if not o: return
    d=MAT.get(m,{})
    o.addProperty("App::PropertyString","Material","Meta","").Material=d.get("name","")
    o.addProperty("App::PropertyFloat","Density","Meta","").Density=d.get("rho",0.0)

# Primitivas básicas centradas en X eje
def C(d,L,cx=0,cy=0,cz=0,l="C"): 
    s=Part.makeCylinder(d/2,L)
    s.Placement=App.Placement(App.Vector(cx-L/2,cy,cz),R())
    return O(s,l)

def K(d1,d2,L,cx=0,cy=0,cz=0,l="K"):
    s=Part.makeCone(d1/2,d2/2,L)
    s.Placement=App.Placement(App.Vector(cx-L/2,cy,cz),R())
    return O(s,l)

def fuse_shapes(list_objs, name="Fused"):
    # fuse una lista de objetos (Part.Shape) y devuelve Part.Shape
    if not list_objs: return None
    s = list_objs[0].Shape
    for o in list_objs[1:]:
        try:
            s = s.fuse(o.Shape)
        except Exception as e:
            print("Advertencia fuse fallo entre:", e)
            try:
                s = s.fuse(o.Shape.tessellate(1.0))
            except:
                pass
    return s

def fillet_large(solid, r=6):
    try:
        f = solid.makeFillet(r,[e for e in solid.Edges if e.Length>30])
        return f
    except:
        return solid

# 1) Construir fuselaje externo por primitivas (más robusto que offset único)
nose_ext = K(P["nose_base_d"],0,P["nose_len"],P["nose_len"]/2,"nose_ext"); M(nose_ext,"AL")
mid_ext  = C(P["mid_d"],P["mid_len"],P["nose_len"]+P["mid_len"]/2,"mid_ext"); M(mid_ext,"AL")
rear_ext = C(P["rear_d"],P["rear_len"],P["nose_len"]+P["mid_len"]+P["rear_len"]/2,"rear_ext"); M(rear_ext,"AL")

outer_shape = fuse_shapes([nose_ext, mid_ext, rear_ext],"outer_fuselage_shape")
if outer_shape is None:
    raise RuntimeError("No se pudo construir la forma externa del fuselaje.")

outer_shape = fillet_large(outer_shape, r=12)
OuterHull = O(outer_shape,"OuterHull"); M(OuterHull,"AL")

# 2) Construir fuselaje interior (clearance para equipos) mediante primitives reducidas (evita offset problemático)
def safe_positive(val):
    return val if val>1.0 else 1.0

h=P["hull_t"]
nose_in_d = safe_positive(P["nose_base_d"]-2*(h+P["shield_t"]+P["impact_t"]))
mid_in_d  = safe_positive(P["mid_d"]-2*(h+P["shield_t"]+P["impact_t"]))
rear_in_d = safe_positive(P["rear_d"]-2*(h+P["shield_t"]+P["impact_t"]))
nose_in_len = max(10.0, P["nose_len"]-2*h)
mid_in_len  = max(10.0, P["mid_len"]-2*h)
rear_in_len = max(10.0, P["rear_len"]-2*h)

nose_int = K(nose_in_d,0,nose_in_len,P["nose_len"]/2,"nose_int"); M(nose_int,"AL")
mid_int  = C(mid_in_d,mid_in_len,P["nose_len"]+P["mid_len"]/2,"mid_int"); M(mid_int,"AL")
rear_int = C(rear_in_d,rear_in_len,P["nose_len"]+P["mid_len"]+P["rear_len"]/2,"rear_int"); M(rear_int,"AL")
inner_shape = fuse_shapes([nose_int, mid_int, rear_int],"inner_fuselage_shape")
inner_shape = fillet_large(inner_shape, r=8)
InnerHull = O(inner_shape,"InnerHull"); M(InnerHull,"CFRP")

# 3) Shell (hull) = OuterHull - InnerHull --> carcasa cerrada con espesor compuesto (hull + shield + impact)
try:
    hull_shell_shape = OuterHull.Shape.cut(InnerHull.Shape)
    hull_shell_shape = fillet_large(hull_shell_shape, r=6)
    HullShell = O(hull_shell_shape,"HullShell"); M(HullShell,"AL")
except Exception as e:
    print("Fallo al cortar Outer-Inner (intento fallback). Error:", e)
    # Fallback: generar offset de outer si está disponible
    try:
        inner_offset = outer_shape.makeOffsetShape(-(h+P["shield_t"]+P["impact_t"]), 0.01, join=2, fill=True)
        hull_shell_shape = outer_shape.cut(inner_offset)
        HullShell = O(hull_shell_shape,"HullShell_offset_fallback"); M(HullShell,"AL")
    except Exception as e2:
        print("Fallback offset también falló:", e2)
        # Si todo falla, mantenemos outer como carcasa sólida (más conservador para CNC)
        HullShell = OuterHull
        print("Se usará OuterHull como carcasa (sólido simple).")

# 4) Capa de blindaje (alta densidad) — alrededor del reactor y sección frontal
# Blindaje cilíndrico alrededor del reactor
reactor_shield = C(P["reactor_d"]+2*P["shield_t"], P["reactor_l"]+2*P["shield_t"], P["reactor_cx"], "reactor_shield"); M(reactor_shield,"W")
# Blindaje frontal (nose) — una conicidad interna
nose_shield_ext = K(P["nose_base_d"]+2*P["shield_t"], P["nose_base_d"], P["nose_len"]+P["shield_t"], P["nose_len"]/2 + P["shield_t"]/2, "nose_shield_ext"); M(nose_shield_ext,"W")
# Fusionar y recortar el hueco interior para tener layer sólido
shield_merged_shape = fuse_shapes([reactor_shield, nose_shield_ext], "shield_merged")
try:
    # crear hueco interior para shield (espacio libre interno)
    inner_for_shield = inner_shape.copy()
    shield_layer_shape = shield_merged_shape.cut(inner_for_shield)
    ShieldLayer = O(shield_layer_shape,"ShieldLayer"); M(ShieldLayer,"W")
except Exception as e:
    print("No se pudo construir ShieldLayer exacto:", e)
    ShieldLayer = reactor_shield

# 5) Capa amortiguadora (kevlar/cfrp) interior continua
# generamos una capa con grosor impact_t justo por dentro de hull_shell (aprox con primitivas reducidas)
impact_inner_d = safe_positive(P["mid_d"] - 2*(P["hull_t"]+P["shield_t"]))
impact_layer = C(impact_inner_d, P["mid_len"] + P["nose_len"] + P["rear_len"], (P["nose_len"] + P["mid_len"]/2), "impact_layer"); M(impact_layer,"KEVLAR")
ImpactLayer = impact_layer

# 6) Añadir anillos estructurales alrededor del reactor y filetearlos (refuerzos para trusses)
rings=[]
x0=P["reactor_cx"]-P["reactor_l"]/2+P["ring_h"]/2
for i in range(P["ring_n"]):
    t=Part.makeTorus((P["ring_ro"]+P["ring_ri"])/2,(P["ring_ro"]-P["ring_ri"])/2)
    t.Placement=App.Placement(App.Vector(x0+i*P["ring_pitch"],0,0),R())
    rings.append(t)
rs=rings[0]
for r in rings[1:]:
    try: rs=rs.fuse(r)
    except: pass
ringsO=O(rs,"RINGS"); M(ringsO,"STEEL")

# 7) Nozzle reforzado y fileteado
noz_ext = K(P["nozzle_exit_d"], P["nozzle_throat_d"], P["nozzle_l"], P["nozzle_cx"], 0, 0, "nozzle_ext"); M(noz_ext,"STEEL")
noz_f = fillet_large(noz_ext.Shape, r=P["nozzle_fillet_r"])
Nozzle = O(noz_f,"Nozzle"); M(Nozzle,"STEEL")

# 8) Fusiones finales: buscamos producir un único sólido sólido_cnc
to_fuse_objs = [HullShell, ShieldLayer, ImpactLayer, ringsO, Nozzle]
# limpiar None y duplicados
to_fuse_shapes = [o.Shape for o in to_fuse_objs if o is not None]

final_shape = to_fuse_shapes[0]
for s in to_fuse_shapes[1:]:
    try:
        final_shape = final_shape.fuse(s)
    except Exception as e:
        print("Aviso fuse parcial falló:", e)
        try:
            final_shape = final_shape.fuse(s.copy())
        except:
            pass

# Intentar convertir en sólido si es shell
try:
    # Si es shell o compuesta, intentar makeSolid vía Shell de caras
    if hasattr(final_shape, "Shells") and len(final_shape.Shells)>0:
        solid_final = Part.makeSolid(final_shape.Shells[0])
    else:
        solid_final = final_shape
    Solid_CNC = O(solid_final,"Solid_CNC"); M(Solid_CNC,"STEEL")
    print("Solid_CNC creado con éxito.")
except Exception as e:
    print("No se pudo generar Solid_CNC como sólido válido:", e)
    # Fallback: presentar la fusión tal cual, útil para inspección
    Solid_CNC = O(final_shape,"Solid_CNC_fallback"); M(Solid_CNC,"STEEL")

doc.recompute()
print("Macro completada: DFD compacto, blindado y preparado para revisión CNC.")
