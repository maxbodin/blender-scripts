import bpy

TARGET_MATERIAL_NAME = "TargetMaterial"

def replace_materials(obj, target_material):
    if obj.data and hasattr(obj.data, "materials"):

        for i in range(len(obj.data.materials)):
            obj.data.materials[i] = target_material

        if not obj.data.materials:
            obj.data.materials.append(target_material)

    for child in obj.children:
        replace_materials(child, target_material)

target_material = bpy.data.materials.get(TARGET_MATERIAL_NAME)

if target_material is None:
    print(f"Missing material with name '{TARGET_MATERIAL_NAME}', creating new material.")
    target_material = bpy.data.materials.new(name=TARGET_MATERIAL_NAME)

obj = bpy.context.active_object

if obj:
    replace_materials(obj, target_material)
    print(f"Replaced materials on '{obj.name}' and all descendants with '{TARGET_MATERIAL_NAME}'")
else:
    print("No active object selected")
