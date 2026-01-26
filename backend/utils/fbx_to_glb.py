import bpy
import sys

fbx_path = sys.argv[-2]
glb_path = sys.argv[-1]

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import FBX
bpy.ops.import_scene.fbx(filepath=fbx_path)

# Export GLB
bpy.ops.export_scene.gltf(
    filepath=glb_path,
    export_format='GLB',
    export_animations=True,
    export_apply=True
)
