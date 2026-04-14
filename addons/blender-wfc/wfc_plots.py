import bpy
from mathutils import Vector
from .wfc_classes import WFCCell, WFCPlot, BuildingPlot, WFCPlotGroup, BuildingPlotGroup
def extract_building_plots_from_cell(cell):
    """Extract building plot data from a collapsed WFC cell"""
    module = cell.return_collapsed_module()
    plots = []

    # Read physical cell size from the module (Task 2B.2)
    cell_size = module.physical_size if module else 8.0

    # Define building plot areas for each primitive type
    # These would be based on your primitive designs
    building_plot_definitions = {
        'BUILDING': [
            # Example: entire module is a building plot
            [(0, 0), (cell_size, 0), (cell_size, cell_size), (0, cell_size)]
        ],
        'ROAD_STRAIGHT': [
            # Example: no building plots on roads
        ],
        'PAVEMENT': [
            # Example: part of pavement might have building plots
            [(2, 2), (6, 2), (6, 6), (2, 6)]  # 4x4m plot in center
        ],
        'CORNER': [
            # Example: L-shaped building plot
            [(0, 0), (4, 0), (4, 4), (0, 4)]
        ]
    }
    
    # Get the primitive type (you'll need to store this in your module data)
    primitive_type = getattr(module.obj_source, 'primitive_type', 'BUILDING')
    
    if primitive_type in building_plot_definitions:
        for plot_bounds in building_plot_definitions[primitive_type]:
            world_pos = Vector((cell.posX * cell_size, cell.posY * cell_size, 0))
            plot = BuildingPlot(world_pos, plot_bounds, cell)
            plots.append(plot)
    
    return plots

def group_adjacent_building_plots(all_building_plots):
    """Group adjacent building plots together"""
    plot_groups = []
    current_group_id = 0
    
    for plot in all_building_plots:
        if plot.is_processed:
            continue
        
        # Start a new group with flood fill
        current_group = []
        plots_to_process = [plot]
        
        while plots_to_process:
            current_plot = plots_to_process.pop(0)
            if current_plot.is_processed:
                continue
            
            current_plot.is_processed = True
            current_plot.building_group_id = current_group_id
            current_group.append(current_plot)
            
            # Find adjacent plots
            adjacent_plots = find_adjacent_plots(current_plot, all_building_plots)
            for adjacent_plot in adjacent_plots:
                if not adjacent_plot.is_processed:
                    plots_to_process.append(adjacent_plot)
        
        if current_group:
            plot_groups.append(BuildingPlotGroup(current_group_id, current_group))
            current_group_id += 1
    
    return plot_groups

def find_adjacent_plots(target_plot, all_plots):
    """Find plots that are adjacent to the target plot"""
    adjacent = []
    target_bounds = target_plot.get_world_bounds()
    
    for plot in all_plots:
        if plot == target_plot or plot.is_processed:
            continue
        
        plot_bounds = plot.get_world_bounds()
        
        # Check if plots share an edge (simplified check)
        if plots_share_edge(target_bounds, plot_bounds):
            adjacent.append(plot)
    
    return adjacent

def plots_share_edge(bounds1, bounds2, tolerance=0.1):
    """Check if two rectangular plots share an edge"""
    # Convert bounds to min/max format
    min_x1, min_y1 = min(b[0] for b in bounds1), min(b[1] for b in bounds1)
    max_x1, max_y1 = max(b[0] for b in bounds1), max(b[1] for b in bounds1)
    
    min_x2, min_y2 = min(b[0] for b in bounds2), min(b[1] for b in bounds2)
    max_x2, max_y2 = max(b[0] for b in bounds2), max(b[1] for b in bounds2)
    
    # Check for shared vertical edge
    if (abs(max_x1 - min_x2) < tolerance or abs(max_x2 - min_x1) < tolerance):
        # Check if y-ranges overlap
        if not (max_y1 < min_y2 or max_y2 < min_y1):
            return True
    
    # Check for shared horizontal edge
    if (abs(max_y1 - min_y2) < tolerance or abs(max_y2 - min_y1) < tolerance):
        # Check if x-ranges overlap
        if not (max_x1 < min_x2 or max_x2 < min_x1):
            return True
    
    return False

# ...existing code...

def process_building_plots_after_collapse():
    """Process building plots after WFC grid is fully collapsed"""
    from .wfc_building_plots import extract_building_plots_from_cell, group_adjacent_building_plots
    
    all_building_plots = []
    
    # Extract building plots from all collapsed cells
    for cell in all_grid_cells.values():
        if cell.isCollapsed:
            plots = extract_building_plots_from_cell(cell)
            all_building_plots.extend(plots)
    
    # Group adjacent plots
    plot_groups = group_adjacent_building_plots(all_building_plots)
    
    print(f"Found {len(plot_groups)} building plot groups")
    
    # TODO: Generate buildings on each plot group
    for group in plot_groups:
        generate_building_on_plot_group(group)

def generate_building_on_plot_group(plot_group):
    """Generate a building on the given plot group"""
    # This is where you'd implement your building generation logic
    # Could be another WFC system, or simple extrusion, etc.
    print(f"Generating building on plot group {plot_group.group_id}")
    print(f"  Plot group bounds: {plot_group.combined_bounds}")
    print(f"  Suggested building grid size: {plot_group.building_grid_size}")
    
    # Example: Create a simple box building for now
    bounds = plot_group.combined_bounds
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    center_x = (bounds[0] + bounds[2]) / 2
    center_y = (bounds[1] + bounds[3]) / 2
    
    bpy.ops.mesh.primitive_cube_add(
        size=2, 
        location=(center_x, center_y, 1), 
        scale=(width/2, height/2, 2)
    )
    building_obj = bpy.context.active_object
    building_obj.name = f"Building_Group_{plot_group.group_id}"
    
    # Link to buildings collection
    buildings_collection = get_collection_by_name("Buildings")  # You'll need to create this
    link_object_to_single_collection(building_obj, buildings_collection)