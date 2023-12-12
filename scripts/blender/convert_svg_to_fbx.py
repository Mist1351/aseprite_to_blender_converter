import bpy
import bmesh
import numpy as np
import math
import os
import argparse
import sys


def find_material_index(obj, material):
    for i, m in enumerate(obj.data.materials):
        if m == material:
            return i
    return -1


def combine_materials_by_color(obj):
    color_poly = []
    for i, poly in obj.data.polygons.items():
        material = obj.data.materials[poly.material_index]
        color = material.diffuse_color
        color_poly.append(color)

    obj.data.materials.clear()

    unique_materials = {}
    for i, color in enumerate(color_poly):
        color_str = f"{color[0]:.3f}_{color[1]:.3f}_{color[2]:.3f}"
        if color_str not in unique_materials:
            material = bpy.data.materials.new(name=f"Color_{color_str}")
            material.diffuse_color = color
            unique_materials[color_str] = material
            obj.data.materials.append(material)
        else:
            material = unique_materials[color_str]
        obj.data.polygons[i].material_index = find_material_index(obj, material)


def reduce_polygons(obj):
    bm = bmesh.from_edit_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    bmesh.update_edit_mesh(obj.data)


def merge_triangles(obj):
    bm = bmesh.from_edit_mesh(obj.data)
    for face in bm.faces:
        if len(face.edges) == 3:
            for edge in face.edges:
                coords1 = np.array(edge.verts[0].co)
                coords2 = np.array(edge.verts[1].co)
                diff = np.setxor1d(coords1, coords2)
                if len(diff) > 2:
                    bmesh.ops.dissolve_edges(bm, edges=[edge])
                    break
    bmesh.update_edit_mesh(obj.data)


# Get input arguments
double_dash_index = sys.argv.index('--') if '--' in sys.argv else -1
if double_dash_index != -1 and double_dash_index + 1 < len(sys.argv):
    additional_args = sys.argv[double_dash_index + 1:]
else:
    additional_args = []

parser = argparse.ArgumentParser(prog=f'{os.path.basename(sys.argv[0])} -b -P {os.path.basename(__file__)}',
                                 usage='%(prog)s -- [options]',
                                 add_help=False)
parser.add_argument('-i', '--input', help='svg file', required=True)
parser.add_argument('-o', '--output', help='output directory', required=True)
parser.add_argument('--scale', help='scale', default=1, type=float)
parser.add_argument('--extrude', help='extrude factor', default=1, type=float)
parser.add_argument('--pivot', help='model pivot', default='center', choices=['center', 'bottom'])
args = parser.parse_args(additional_args)

try:
    # Cleanup scene
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()

    # Import svg
    svg_file_path = args.input
    output_file_path = os.path.join(args.output, os.path.splitext(os.path.basename(svg_file_path))[0] + '.fbx')
    scale_float = args.scale
    extrude_float = args.extrude
    pivot = args.pivot
    bpy.ops.import_curve.svg(filepath=svg_file_path)

    # Select CURVE objects
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='CURVE')

    # Convert CURVE to MESH
    for obj in bpy.context.selected_objects:
        if obj.type == 'CURVE':
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.convert(target='MESH')

    # Select converted objects
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')

    if bpy.context.selected_objects:
        # Bound Box
        #  z
        #  | y
        #  |/__x
        #   [2]------[6]
        #   /|       /|
        # [1]+-----[5]|
        #  | |      | |
        #  |[3]-----+[7]
        #  |/       |/
        # [0]------[4]

        bounding_box = bpy.context.selected_objects[0].bound_box
        width = (bounding_box[6][0] - bounding_box[0][0])

        bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
        bpy.ops.object.join()

        obj = bpy.context.view_layer.objects.active

        bpy.ops.object.mode_set(mode='EDIT')
        reduce_polygons(obj)
        merge_triangles(obj)

        bpy.ops.mesh.select_all(action='SELECT')
        for _ in range(math.floor(extrude_float)):
            bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={'value': (0, 0, width)})
        fractional_part = extrude_float % 1
        if fractional_part > 0:
            bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={'value': (0, 0, width * fractional_part)})
        bpy.ops.object.mode_set(mode='OBJECT')

        obj.scale.x *= scale_float
        obj.scale.y *= scale_float
        obj.scale.z *= scale_float

        obj.rotation_euler.x = math.radians(90)

        apply_rotation = False
        apply_scale = True
        bpy.ops.object.transform_apply(location=False, rotation=apply_rotation, scale=apply_scale)

        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        obj.location = (0, 0, 0)
        if pivot == 'bottom':
            scale = 1 if apply_scale else scale_float
            if apply_rotation:
                offset = bounding_box[1][2] - bounding_box[0][2]
            else:
                offset = bounding_box[3][1] - bounding_box[0][1]
            bpy.context.scene.cursor.location = (0, 0, -offset * scale / 2)
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            obj.location = (0, 0, 0)

        combine_materials_by_color(obj)

        bpy.ops.export_scene.fbx(filepath=output_file_path, use_selection=True, add_leaf_bones=False)
    else:
        print('No objects of type MESH')
except Exception as e:
    print(f"{e}", file=sys.stderr)
    sys.exit(1)
