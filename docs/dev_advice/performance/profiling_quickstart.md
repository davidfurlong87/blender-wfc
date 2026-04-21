# Quick Start: Profiling and Optimizing Performance

## The Simple Steps

When you suspect a performance issue, follow these steps:

### 1. Measure the Baseline

**Before changing anything, measure current performance.**

```python
import time

# Add to __init__.py or run in Blender console
def measure_collapse_performance():
    # Clear existing grid
    clear_all_cells()
    
    # Build test grid
    build_wfc_grid(all_modules, all_grid_cells, uncollapsed_grid_cells)
    
    # Time the collapse
    start = time.time()
    collapse_process()
    end = time.time()
    
    elapsed = end - start
    grid_size = len(all_grid_cells)
    cells_per_second = grid_size / elapsed if elapsed > 0 else 0
    
    print(f"\n{'='*50}")
    print(f"PERFORMANCE BASELINE")
    print(f"{'='*50}")
    print(f"Grid size: {grid_size} cells")
    print(f"Total time: {elapsed:.2f} seconds")
    print(f"Speed: {cells_per_second:.1f} cells/second")
    print(f"{'='*50}\n")
    
    return elapsed

# Run it
measure_collapse_performance()
```

**Record these numbers!** You need them to know if optimizations help.

### 2. Profile to Find Bottlenecks

**Use Python's profiler to see where time is spent.**

```python
import cProfile
import pstats
import io

def profile_collapse():
    # Clear and rebuild grid
    clear_all_cells()
    build_wfc_grid(all_modules, all_grid_cells, uncollapsed_grid_cells)
    
    # Profile the collapse
    profiler = cProfile.Profile()
    profiler.enable()
    
    collapse_process()
    
    profiler.disable()
    
    # Print results
    s = io.StringIO()
    stats = pstats.Stats(profiler, stream=s)
    stats.sort_stats('cumulative')
    stats.print_stats(30)  # Top 30 functions
    
    print(s.getvalue())

# Run it
profile_collapse()
```

**Look for:**
- Functions with high `cumtime` (cumulative time)
- Functions called many times (`ncalls`)
- Blender operations (`bpy.ops.*`, `bpy.data.*`)

### 3. Add Detailed Timing

**Instrument specific sections to understand the breakdown.**

```python
import time

# Add this helper to __init__.py
class PerformanceTimer:
    def __init__(self):
        self.timings = {}
    
    def start(self, name):
        self.timings[name] = {'start': time.time(), 'total': 0, 'count': 0}
    
    def end(self, name):
        if name in self.timings:
            elapsed = time.time() - self.timings[name]['start']
            self.timings[name]['total'] += elapsed
            self.timings[name]['count'] += 1
    
    def report(self):
        print(f"\n{'='*60}")
        print(f"PERFORMANCE BREAKDOWN")
        print(f"{'='*60}")
        sorted_timings = sorted(self.timings.items(), 
                               key=lambda x: x[1]['total'], 
                               reverse=True)
        for name, data in sorted_timings:
            total = data['total']
            count = data['count']
            avg = total / count if count > 0 else 0
            print(f"{name:30s}: {total:6.2f}s total, {count:5d} calls, {avg*1000:6.2f}ms avg")
        print(f"{'='*60}\n")

# Global timer
perf_timer = PerformanceTimer()

# Instrument collapse_cell function
def collapse_cell(cell):
    perf_timer.start("collapse_cell")
    
    perf_timer.start("select_module")
    scored_modules = [(build_module_score(module.module_weight), module) 
                      for module in cell.possibleModules]
    module_to_return = scored_modules[0]
    for scored_module in scored_modules:
        if scored_module[0] > module_to_return[0]:
            module_to_return = scored_module
    perf_timer.end("select_module")
    
    cell.possibleModules = [module_to_return[1]]
    cell.isCollapsed = True
    module_obj = module_to_return[1].obj_source
    placement_location = (cell.posX * (module_size), cell.posY * (module_size), 0)
    
    perf_timer.start("mesh_duplication")
    collapsed_cell_obj = duplicate_and_move_and_return(module_obj, placement_location)
    perf_timer.end("mesh_duplication")
    
    collapsed_cell_obj.name = f"{cell.posX:02d}_{cell.posY:02d}-{module_obj.name}"
    
    perf_timer.start("mesh_replacement")
    cell.replace_mesh_obj(new_obj=collapsed_cell_obj)
    perf_timer.end("mesh_replacement")
    
    perf_timer.start("collection_linking")
    link_object_to_single_collection(collapsed_cell_obj, 
                                     get_collection_by_name(CollectionNames.Grid.value))
    perf_timer.end("collection_linking")
    
    perf_timer.end("collapse_cell")

# After collapse, print report
collapse_process()
perf_timer.report()
```

### 4. Optimize the Bottleneck

**Focus on the slowest operation first.**

Common bottlenecks and fixes:

#### Bottleneck: Mesh Duplication

```python
# BEFORE (Slow)
def duplicate_and_move_and_return(target_obj, target_location):
    duplicate = target_obj.copy()
    duplicate.data = target_obj.data.copy()  # Deep copy!
    duplicate.location = target_location
    return duplicate

# AFTER (Fast - shared mesh data)
def duplicate_and_move_and_return(target_obj, target_location):
    duplicate = target_obj.copy()  # Shallow copy (shares mesh)
    duplicate.location = target_location
    return duplicate
```

#### Bottleneck: Collection Lookups

```python
# BEFORE (Slow - lookup every time)
def collapse_cell(cell):
    # ... collapse logic ...
    link_object_to_single_collection(obj, get_collection_by_name(CollectionNames.Grid.value))

# AFTER (Fast - cache collection)
# At module level
_grid_collection_cache = None

def get_grid_collection():
    global _grid_collection_cache
    if _grid_collection_cache is None:
        _grid_collection_cache = get_collection_by_name(CollectionNames.Grid.value)
    return _grid_collection_cache

def collapse_cell(cell):
    # ... collapse logic ...
    link_object_to_single_collection(obj, get_grid_collection())
```

#### Bottleneck: Propagation

```python
# BEFORE (Slow - creates lists repeatedly)
def propagate(collapsed_cell):
    affected_cells = [collapsed_cell]
    all_cell_keys = [key for key in all_grid_cells.keys()]  # Unnecessary list
    # ...

# AFTER (Fast - use dict directly)
def propagate(collapsed_cell):
    affected_cells = [collapsed_cell]
    # Use all_grid_cells.keys() directly, no list conversion
    # ...
```

### 5. Measure Again

**Verify your optimization worked.**

```python
# Run the same baseline measurement
measure_collapse_performance()

# Compare to your recorded baseline
# Did time decrease?
# Did cells/second increase?
```

## Common Scenarios

### Scenario 1: Collapse is slow on large grids

**Symptoms:** 10x10 grid is fine, 50x50 grid takes minutes

**Likely cause:** Mesh duplication (O(n) where n = grid size)

**Solution:** Use shared mesh data (see Strategy 1 in main guide)

### Scenario 2: Propagation takes forever

**Symptoms:** Each collapse step gets slower

**Likely cause:** Inefficient neighbor checking or list operations

**Solution:** Pre-calculate neighbor maps, use sets instead of lists

### Scenario 3: Memory usage explodes

**Symptoms:** Blender uses gigabytes of RAM for small grids

**Likely cause:** Deep copying mesh data for every cell

**Solution:** Share mesh data between instances

### Scenario 4: UI freezes during collapse

**Symptoms:** Blender becomes unresponsive

**Likely cause:** No progress updates, blocking main thread

**Solution:** Add progress reporting, consider modal operator

## Quick Profiling Checklist

When investigating performance:

- [ ] Measure baseline (time, cells/second)
- [ ] Run profiler to find bottleneck
- [ ] Add detailed timing to bottleneck
- [ ] Identify root cause
- [ ] Apply optimization
- [ ] Measure again to verify improvement
- [ ] Repeat for next bottleneck

## Troubleshooting

### Problem: Profiler output is overwhelming

**Solution:** Focus on `cumtime` column, ignore functions < 0.1s

### Problem: Can't find the bottleneck

**Solution:** Add manual timing to every major function

### Problem: Optimization made it slower

**Solution:** Revert change, re-profile, try different approach

### Problem: Optimization broke functionality

**Solution:** Write tests before optimizing, verify behavior unchanged

## Remember

✅ **DO:** Profile before optimizing
✅ **DO:** Measure baseline first
✅ **DO:** Focus on biggest bottleneck
✅ **DO:** Verify improvements

❌ **DON'T:** Guess where the problem is
❌ **DON'T:** Optimize without measuring
❌ **DON'T:** Optimize everything at once
❌ **DON'T:** Sacrifice correctness for speed

