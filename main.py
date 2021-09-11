import sys
import bpy
import bmesh
import numpy as np
import random
from scipy import signal
import time
import mathutils

# globals
color_turn = True
mask = None
new_living = None
to_kill = None
add_new = None

# remove exixting objects
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.delete()

# set of active objects
active_objects = set()

#set the grid size
grid_size = 20
grid = np.zeros((grid_size,)*3, dtype=int)

# randomly place some 'n' 1s
#n = 6
#for i in range(n):
#    grid[random.randint(0, (grid_size-1)//2),
#        random.randint(0, (grid_size-1)//2),
#        random.randint(0, (grid_size-1)//2)] = 1

for i in range(6,9):
    grid[10, 6, i] = 1
    grid[10, 10, i] = 1
for i in range(7,10):
    grid[10, i, 5] = 1
    grid[10, i, 9] = 1

# red material
mat = bpy.data.materials.new("PKHG")
mat.diffuse_color = (1.0,0.0,0.0,1.0)
        
# now place the cubes
for cor in zip(*np.where(grid == 1)):
    bpy.ops.mesh.primitive_cube_add(size=1,
                                    calc_uvs=False,
                                    location=cor)
    obj = bpy.context.object
    obj.name = str(cor)
    active_objects.add(cor)
    
    
# now in next step we will calculate Conway's conditions
kernel = np.ones((3,3,3), dtype=int)
kernel[1,1,1] = 0

def create_cube(name, loc):
    bpyscene = bpy.context.scene

    # Create an empty mesh and the object.
    mesh = bpy.data.meshes.new(name)
    basic_cube = bpy.data.objects.new(name, mesh)

    # Add the object into the scene.
    bpyscene.collection.objects.link(basic_cube)

    # Construct the bmesh cube and assign it to the blender mesh.
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0, matrix=mathutils.Matrix.Translation(loc))
    bm.to_mesh(mesh)
    bm.free()

def loop_generation(delay = 1):
    
    global active_objects, color_turn, mask, to_kill, add_new, new_living
    
    # calculating the mask
    if mask is None:
        convolution = signal.convolve(grid, kernel, mode='same')
        
        # Any live cell with 5-6 live neighbors survives
        mask_1 = ((convolution == 5) | (convolution == 6)) & (grid == 1)
        # Any dead cell with 4 live neighbors becomes a live cell
        mask_2 = (convolution == 4) & (grid == 0)
        mask = mask_1 | mask_2
    
        # extract the living cells
        new_living = set()
        for cord in zip(*np.where(mask)):
            new_living.add(cord)
            
        to_kill = active_objects.difference(new_living)
        add_new = new_living.difference(active_objects)
    
    if color_turn:
        for del_cor in to_kill:
            bpy.data.objects[str(del_cor)].active_material = mat
        color_turn = not color_turn
            
        return delay
    
    # update the grid
    grid[:] = 0
    grid[mask] = 1
    
    
    for del_cor in to_kill:
        bpy.data.objects.remove(bpy.data.objects[str(del_cor)])
    
    for new_cor in add_new:
        create_cube(str(new_cor), new_cor)
      
    active_objects = new_living
    color_turn = not color_turn
    mask = None
    return delay
        


if __name__ == '__main__':
    bpy.app.timers.register(loop_generation)
