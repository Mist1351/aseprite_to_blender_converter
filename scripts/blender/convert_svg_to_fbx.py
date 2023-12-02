import bpy
import math
import os
import argparse
import sys

double_dash_index = sys.argv.index('--') if '--' in sys.argv else -1
if double_dash_index != -1 and double_dash_index + 1 < len(sys.argv):
    additional_args = sys.argv[double_dash_index + 1:]
else:
    additional_args = []

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', help='svg file', required=True)
parser.add_argument('-o', '--output', help='output directory', required=True)
parser.add_argument('-s', '--scale', help='scale', required=True)
args = parser.parse_args(additional_args)

# Cleanup scene
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_by_type(type='MESH')
bpy.ops.object.delete()

# Import svg
svg_file_path = args.input
output_file_path = os.path.join(args.output, os.path.splitext(os.path.basename(svg_file_path))[0] + '.fbx')
scale_float = float(args.scale)
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
selected_objects = bpy.context.selected_objects

if selected_objects:
    bounding_box = bpy.context.selected_objects[0].bound_box
    width = bounding_box[6][0] - bounding_box[0][0]

    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    bpy.ops.object.join()

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, 0, width)})
    bpy.ops.object.mode_set(mode='OBJECT')

    obj = bpy.context.view_layer.objects.active
    obj.scale.x *= scale_float
    obj.scale.y *= scale_float
    obj.scale.z *= scale_float
    obj.rotation_euler.x = math.radians(90)

    bpy.ops.export_scene.fbx(filepath=output_file_path, use_selection=True, add_leaf_bones=False)
else:
    print("No objects of type MESH to merge.")
