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

class OpCutToUvRects(bpy.types.Operator):
    bl_idname = "uvs.cut_to_uv_rects"
    bl_label = "Cut into pieces using UV"
    bl_description = "Cut into pieces accoring to uv squares: 0 to 1, 1 to 2, etc."
    bl_options = {'REGISTER', 'UNDO'}

    steps : bpy.props.IntProperty(name="Edges", default=3, min=3, soft_max=100)

    def execute(self, context:bpy.types.Context):
        objects:bpy.types.Object = context.selected_objects

        # bpy.context.tool_settings.use_uv_select_sync = False
        # bpy.ops.mesh.select_all(action='DESELECT')
        # bpy.ops.uv.select_all(action='DESELECT')

        #first of all, let's make sure all the faces are concave:
        # bmesh.ops.connect_verts_concave(bm, bm.faces[:])

        for obj in objects:
            bm:bmesh.types.BMesh = bmesh.new()
            bm.from_mesh(obj.data)

            #TO CONNECT VERTS:
            # bmesh.ops.connect_verts
            # bmesh.ops.split_edges
            # bmesh.ops.subdivide_edges
            # bmesh.ops.weld_verts
            # bmesh.ops.uv

            uv_lay = bm.loops.layers.uv.active

            i = 0
            while True:
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
                            
                            #IF RIGHT ON THE BORDER
                            if abs(.5 - uv%1)*2 <= 0.0000001:
                                min_maxes.append((round(uv-1), round(uv+1)))
                            else:
                                min_maxes.append((math.floor(uv), math.ceil(uv)))

                        if border_face:
                            break
                
                #>>>NEED TO CHECK IF THIS WORKS FIRST
                if border_face:
                    bmesh.ops.delete(bm, border_face, 'FACES')
                #CHECK END<<<

                if not border_face:
                    bm.to_mesh(obj.data)
                    return {'FINISHED'}

                #>>>------------------
                # relevant_edges = []
                # for edge in border_face.edges: #type: bmesh.types.BMEdge
                #     relevant_loops = []
                #     for loop in edge.link_loops: #type: bmesh.types.BMLoop
                #         if loop.face != border_face:
                #             continue
                #         relevant_loops.append(loop)

                #         #IF RIGHT ON THE BORDER
                #         if abs(.5 - uv%1)*2 <= 0.0000001:
                            

                #     uvs = (
                #         relevant_loops[0][uv_lay].uv[axis],
                #         relevant_loops[1][uv_lay].uv[axis])
                        
                #     for

                #     uv_b = 

                #         #IF ON EDGE OF SQUARE
                #         if 
                #------------------<<<

                # j = 0
                # sqr = 
                # #loop is basically a corner of a face
                # for loop in face.loops:
                #     uv = loop[uv_lay].uv
                #     print("Loop UV: %f, %f" % uv[:])
                #     vert = loop.vert
                #     print("Loop Vert: (%f,%f,%f)" % vert.co[:])

                #     y = 0
                #     if j==2 or j==3:
                #         y = 1

                #     x = 0
                #     if j==1 or j==2:
                #         x = 1

                #     loop[uv_lay].uv = (i*2+x, i*2+y)
                #     j += 1
                # i += 1

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