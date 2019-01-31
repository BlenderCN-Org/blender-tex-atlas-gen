bl_info = {
    "name" : "UV slicer",
    "author" : "ChieVFX",
    "description" : "",
    "blender" : (2, 80, 0),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

import bpy
import bmesh
import math

def is_uv_on_border(uv):
    return abs(.5 - uv%1) >= 0.499999

class OpCutToUvRects(bpy.types.Operator):
    bl_idname = "uvs.cut_to_uv_rects"
    bl_label = "Cut into pieces using UV"
    bl_description = "Cut into pieces accoring to uv squares: 0 to 1, 1 to 2, etc."
    bl_options = {'REGISTER', 'UNDO'}

    steps : bpy.props.IntProperty(name="Edges", default=3, min=3, soft_max=100)

    def execute(self, context:bpy.types.Context):
        objects:bpy.types.Object = context.selected_objects

        for obj in objects:
            bm:bmesh.types.BMesh = bmesh.new()
            bm.from_mesh(obj.data)

            uv_lay = bm.loops.layers.uv.active

            i = 0
            while True:
                i += 1
                if (i > 5000):
                    return {'CANCELLED'}

                #FIRST FIND A FACE WITH UVS SPLATTERED OVER MORE THAN ONE UV SQUARE
                border_axis = -1
                border_value = -9999999
                border_face = None
                for axis in range(0, 2):
                    for face in bm.faces: #type: bmesh.types.BMFace
                        min_maxes = []
                        for loop in face.loops: #type: bmesh.types.BMLoop
                            uv = loop[uv_lay].uv[axis]
                            for min_max in min_maxes:
                                if uv < min_max[0] or uv > min_max[1]:
                                    border_face = face
                                    border_axis = axis
                                    if uv < min_max[0]:
                                        border_value = min_max[0]
                                    else:
                                        border_value = min_max[1]
                                    break
                                    
                            if border_face:
                                break
                            
                            if is_uv_on_border(uv):
                                min_maxes.append((round(uv-1), round(uv+1)))
                            else:
                                min_maxes.append((math.floor(uv), math.ceil(uv)))

                        if border_face:
                            break

                if not border_face:
                    bm.to_mesh(obj.data)
                    region:bpy.types.Region = context.region
                    region.tag_redraw() 
                    return {'FINISHED'}

                verts_to_connect = []
                edges = {}
                for edge in border_face.edges: #type: bmesh.types.BMEdge
                    relevant_loops = []
                    for vert in edge.verts: #type: bmesh.types.BMVert
                        for loop in vert.link_loops: #type: bmesh.types.BMLoop
                            if loop.face != border_face:
                                continue
                            relevant_loops.append(loop)

                    uvs = (
                        relevant_loops[0][uv_lay].uv[border_axis],
                        relevant_loops[1][uv_lay].uv[border_axis])
                    
                    subdivision_value:int
                    if uvs[0] == border_value:
                        subdivision_value = 1
                        if edge.verts[0] not in verts_to_connect:
                            verts_to_connect.append(edge.verts[0])
                        continue
                    elif uvs[1] == border_value:
                        subdivision_value = 0
                        if edge.verts[1] not in verts_to_connect:
                            verts_to_connect.append(edge.verts[1])
                        continue
                    elif uvs[0] < border_value and uvs[1] > border_value:
                        subdivision_value = abs((border_value-uvs[1])/(uvs[0]-uvs[1]))
                    elif uvs[1] < border_value and uvs[0] > border_value:
                        subdivision_value = abs((border_value-uvs[1])/(uvs[0]-uvs[1]))
                    else:
                        continue
                    
                    edges[edge] = [vert, subdivision_value]

                for edge, values in edges.items():
                    edge_vert_pair = bmesh.utils.edge_split(edge, values[0], values[1])
                    verts_to_connect.append(edge_vert_pair[1])
                
                bmesh.ops.connect_verts(bm, verts=verts_to_connect)

classes = [
    OpCutToUvRects,
]

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)