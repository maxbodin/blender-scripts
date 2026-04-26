import bpy
import bmesh
from mathutils.bvhtree import BVHTree

WALL_COLLECTION_NAME = "WALLS"
FURNITURE_COLLECTION_NAME = "FURNITURE"

last_valid_transforms = {}
_guard = False


def bvh_from_object(obj, depsgraph):
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.to_mesh()

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.transform(obj_eval.matrix_world)

    bvh = BVHTree.FromBMesh(bm)

    bm.free()
    obj_eval.to_mesh_clear()

    return bvh


def objects_intersect(obj1, obj2, depsgraph):
    bvh1 = bvh_from_object(obj1, depsgraph)
    bvh2 = bvh_from_object(obj2, depsgraph)
    return len(bvh1.overlap(bvh2)) > 0


def check_collisions(scene, depsgraph):
    global _guard
    if _guard:
        return

    walls = bpy.data.collections.get(WALL_COLLECTION_NAME)
    furnitures = bpy.data.collections.get(FURNITURE_COLLECTION_NAME)
    if not walls or not furnitures:
        return

    reverts = {}

    for obj in furnitures.objects:
        if obj.name not in last_valid_transforms:
            last_valid_transforms[obj.name] = (
                obj.location.copy(),
                obj.rotation_euler.copy(),
                obj.scale.copy(),
            )

        collided = any(
            objects_intersect(obj, wall, depsgraph) for wall in walls.objects
        )

        if collided:
            reverts[obj.name] = obj
        else:
            last_valid_transforms[obj.name] = (
                obj.location.copy(),
                obj.rotation_euler.copy(),
                obj.scale.copy(),
            )

    if reverts:
        _guard = True
        for name, obj in reverts.items():
            loc, rot, sc = last_valid_transforms[name]
            obj.location = loc
            obj.rotation_euler = rot
            obj.scale = sc

        def release_guard():
            global _guard
            _guard = False
            return None

        bpy.app.timers.register(release_guard, first_interval=0.0)


# Clean up any previous registration to allow re-running the script.
for h in list(bpy.app.handlers.depsgraph_update_post):
    if h.__name__ == "check_collisions":
        bpy.app.handlers.depsgraph_update_post.remove(h)

bpy.app.handlers.depsgraph_update_post.append(check_collisions)

print("Collisions blocker active in object mode.")