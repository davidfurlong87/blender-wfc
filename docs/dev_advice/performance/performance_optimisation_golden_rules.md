# Blender WFC Performance Optimization Guide

## The Golden Rule

**When in doubt, always remember: Profile first, optimize second. Never guess where the bottleneck is—measure it.**

## Why Performance Matters

In procedural generation, performance issues compound quickly:
- A 10x10 grid = 100 cells = 100 mesh duplications
- A 50x50 grid = 2,500 cells = 2,500 mesh duplications
- Each duplication copies vertices, faces, materials, vertex groups
- Blender operations can be slow when done repeatedly

**The goal:** Generate large grids (100x100+) in seconds, not minutes.

## How Blender Mesh Operations Work Under the Hood

### Object vs Mesh Data

```python
# Object: The "instance" in the scene
obj = bpy.data.objects.new("MyObject", mesh_data)

# Mesh Data: The actual geometry (shared between objects)
mesh_data = bpy.data.meshes.new("MyMesh")
```

**Key Insight:** Multiple objects can share the same mesh data!

### Shallow Copy vs Deep Copy

```python
# Shallow copy - shares mesh data (FAST)
duplicate = obj.copy()
# duplicate.data points to SAME mesh as obj.data

# Deep copy - duplicates mesh data (SLOW)
duplicate = obj.copy()
duplicate.data = obj.data.copy()
# duplicate.data is a NEW mesh with copied geometry
```

### Current Duplication Pattern (Slow)

```python
# From collection_creation.py
def duplicate_and_move_and_return(target_obj, target_location):
    duplicate = target_obj.copy()
    duplicate.data = target_obj.data.copy()  # ⚠️ DEEP COPY EVERY TIME
    duplicate.location = target_location
    return duplicate
```

**Problem:** For a 10x10 grid, this creates 100 separate mesh data blocks, even though they're identical!

### Why This Is Slow

1. **Memory allocation** - Each mesh data block allocates new memory
2. **Vertex copying** - All vertices, edges, faces copied
3. **Material copying** - Material slots duplicated
4. **Vertex group copying** - All vertex groups duplicated
5. **Blender overhead** - Internal bookkeeping for each mesh

## Performance Optimization Strategies

### Strategy 1: Shared Mesh Data (Instancing)

**Concept:** All collapsed cells with the same module share one mesh data block.

```python
# BEFORE (Slow - 100 mesh data blocks for 10x10 grid)
for cell in grid:
    duplicate = module.obj_source.copy()
    duplicate.data = module.obj_source.data.copy()  # New mesh each time!
    
# AFTER (Fast - ~12 mesh data blocks for 10x10 grid with 12 module types)
for cell in grid:
    duplicate = module.obj_source.copy()
    # duplicate.data already points to module.obj_source.data (shared!)
```

**Savings:** 
- 10x10 grid: 100 meshes → 12 meshes = **88% reduction**
- 50x50 grid: 2,500 meshes → 12 meshes = **99.5% reduction**

### Strategy 2: Lazy Mesh Generation

**Concept:** Don't create visual meshes until needed.

```python
# Store only the data
cell.collapsed_module = selected_module  # Just a reference
cell.position = (x, y)

# Create mesh only when:
# - User requests visualization
# - Exporting to file
# - Building plots need geometry
```

**Savings:** Collapse algorithm runs in pure Python (very fast), mesh creation is separate.

### Strategy 3: Batch Operations

**Concept:** Blender is faster when you batch operations.

```python
# SLOW - Individual operations
for cell in cells:
    bpy.ops.object.select_all(action='DESELECT')
    cell.mesh_obj.select_set(True)
    bpy.ops.object.delete()

# FAST - Batch operation
for cell in cells:
    cell.mesh_obj.select_set(True)
bpy.ops.object.delete()  # Delete all at once
```

### Strategy 4: Avoid Operators When Possible

**Concept:** `bpy.ops` operators are slow. Use `bpy.data` directly.

```python
# SLOW - Uses operator
bpy.ops.object.delete()

# FAST - Direct data manipulation
bpy.data.objects.remove(obj, do_unlink=True)
```

### Strategy 5: Cache Expensive Calculations

**Concept:** Calculate once, reuse many times.

```python
# SLOW - Recalculate for every cell
for cell in grid:
    valid_neighbors = calculate_valid_neighbors(cell, all_modules)

# FAST - Calculate once per module type
module_neighbor_cache = {}
for module in all_modules:
    module_neighbor_cache[module] = calculate_valid_neighbors(module)

for cell in grid:
    valid_neighbors = module_neighbor_cache[cell.module]
```

## Profiling Tools & Techniques

### Built-in Python Profiler

```python
import cProfile
import pstats

def profile_collapse():
    profiler = cProfile.Profile()
    profiler.enable()
    
    collapse_process()  # Your function
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 slowest functions

# Run from Blender's Python console
profile_collapse()
```

### Manual Timing

```python
import time

start = time.time()
collapse_process()
end = time.time()
print(f"Collapse took {end - start:.2f} seconds")
```

### Detailed Timing

```python
import time

timings = {}

def timed_section(name):
    """Context manager for timing code sections"""
    class Timer:
        def __enter__(self):
            self.start = time.time()
            return self
        def __exit__(self, *args):
            elapsed = time.time() - self.start
            timings[name] = timings.get(name, 0) + elapsed
    return Timer()

# Usage
with timed_section("mesh_duplication"):
    duplicate_and_move_and_return(obj, location)

with timed_section("propagation"):
    propagate(cell)

# Print results
for name, total_time in sorted(timings.items(), key=lambda x: x[1], reverse=True):
    print(f"{name}: {total_time:.3f}s")
```

## Common Performance Pitfalls

### ❌ Pitfall 1: Deep copying when shallow copy suffices

```python
# WRONG - Unnecessary deep copy
duplicate.data = obj.data.copy()

# RIGHT - Share mesh data
duplicate = obj.copy()  # Shares mesh data automatically
```

### ❌ Pitfall 2: Repeated collection lookups

```python
# WRONG - Looks up collection every iteration
for cell in cells:
    collection = get_collection_by_name("WFC_Grid")
    collection.objects.link(cell.mesh_obj)

# RIGHT - Look up once
collection = get_collection_by_name("WFC_Grid")
for cell in cells:
    collection.objects.link(cell.mesh_obj)
```

### ❌ Pitfall 3: Unnecessary mesh updates

```python
# WRONG - Updates mesh after every vertex
for vert in vertices:
    mesh.vertices[i].co = vert
    mesh.update()  # Expensive!

# RIGHT - Update once at the end
for vert in vertices:
    mesh.vertices[i].co = vert
mesh.update()  # Once
```

### ❌ Pitfall 4: Creating objects in loops

```python
# WRONG - Creates list every iteration
for cell in cells:
    neighbors = [n for n in all_cells if is_neighbor(n, cell)]

# RIGHT - Pre-calculate or use generator
neighbor_map = build_neighbor_map(all_cells)
for cell in cells:
    neighbors = neighbor_map[cell]
```

## Measuring Success

### Baseline Metrics

Before optimizing, measure:
- Time to collapse 10x10 grid
- Time to collapse 50x50 grid
- Memory usage (Blender's System Console)
- Number of mesh data blocks created

### Target Metrics

After optimizing:
- 10x10 grid: < 1 second
- 50x50 grid: < 10 seconds
- 100x100 grid: < 60 seconds
- Mesh data blocks: ≈ number of unique modules (not number of cells)

### Profiling Checklist

- [ ] Profile the full collapse process
- [ ] Identify the slowest function
- [ ] Profile that function in detail
- [ ] Optimize the bottleneck
- [ ] Re-profile to verify improvement
- [ ] Repeat until performance is acceptable

