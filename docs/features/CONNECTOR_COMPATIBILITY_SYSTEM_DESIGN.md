# Connector Compatibility System - Metadata-Driven Design

**Goal:** Replace hardcoded `sockets_match()` function with a persisted, user-configurable connector compatibility system.

**Date:** 2026-04-08  
**Status:** 📋 Design Phase

---

## 🔴 Current Problem: Hardcoded Socket Matching

### **The Hardcoded Function**

```python
# wfc_classes.py lines 452-472
def sockets_match(socket_a, socket_b):
    if (socket_a == 'ROAD'):
        if (socket_b == 'ROAD'):
            return True
        else:
            return False
    if (socket_a == 'BUILDING'):
        if (socket_b == 'BUILDING'):
            return True
        else:
            return False
    if (socket_a == 'PAVEMENTPOS'):
        if (socket_b == 'PAVEMENTNEG'):
            return True
        else:
            return False
    if (socket_a == 'PAVEMENTNEG'):
        if (socket_b == 'PAVEMENTPOS'):
            return True
        else:
            return False
```

**Problems:**
- ❌ Hardcoded connector types (`ROAD`, `BUILDING`, etc.)
- ❌ Hardcoded compatibility rules
- ❌ Can't add new connectors without editing code
- ❌ Different rules for different grid types not supported
- ❌ No persistence - rules lost between sessions

---

## ✅ Solution: Connector Definition System

### **Core Concept**

**Connectors are data, not code.** Each connector knows who it matches with.

```python
@dataclass
class ConnectorDefinition:
    """Defines a connector type and its compatibility rules"""
    name: str                      # "ROAD", "WALL", "DOOR", etc.
    description: str = ""          # Human-readable description
    compatible_with: List[str] = field(default_factory=list)  # List of compatible connector names
    grid_category: str = "outer_grid"  # Which grid this applies to
    is_symmetric: bool = True      # True = matches self, False = only matches others
```

**Example Connectors:**

```python
# Outer grid connectors
ROAD_CONNECTOR = ConnectorDefinition(
    name="ROAD",
    description="Road connector - matches roads",
    compatible_with=["ROAD"],  # Only matches itself
    grid_category="outer_grid",
    is_symmetric=True
)

BUILDING_CONNECTOR = ConnectorDefinition(
    name="BUILDING",
    description="Building connector - matches buildings",
    compatible_with=["BUILDING"],  # Only matches itself
    grid_category="outer_grid",
    is_symmetric=True
)

PAVEMENT_POS_CONNECTOR = ConnectorDefinition(
    name="PAVEMENTPOS",
    description="Pavement positive edge",
    compatible_with=["PAVEMENTNEG"],  # Only matches its opposite
    grid_category="outer_grid",
    is_symmetric=False  # Asymmetric - only matches the other type
)

PAVEMENT_NEG_CONNECTOR = ConnectorDefinition(
    name="PAVEMENTNEG",
    description="Pavement negative edge",
    compatible_with=["PAVEMENTPOS"],  # Only matches its opposite
    grid_category="outer_grid",
    is_symmetric=False
)

# Building grid connectors (NEW - for inner grids!)
WALL_CONNECTOR = ConnectorDefinition(
    name="WALL",
    description="Solid wall - matches walls or doors",
    compatible_with=["WALL", "DOOR", "WINDOW"],
    grid_category="building",
    is_symmetric=True
)

DOOR_CONNECTOR = ConnectorDefinition(
    name="DOOR",
    description="Door opening",
    compatible_with=["WALL", "DOOR", "HALLWAY"],
    grid_category="building",
    is_symmetric=True
)

WINDOW_CONNECTOR = ConnectorDefinition(
    name="WINDOW",
    description="Window opening",
    compatible_with=["WALL", "WINDOW"],
    grid_category="building",
    is_symmetric=True
)
```

---

## 📋 Connector Registry System

### **ConnectorRegistry Class**

```python
class ConnectorRegistry:
    """Global registry of all connector definitions"""
    
    def __init__(self):
        self.connectors: Dict[str, ConnectorDefinition] = {}
        self._load_defaults()
    
    def _load_defaults(self):
        """Load default connector definitions"""
        # Outer grid connectors
        self.register(ConnectorDefinition(
            name="ROAD",
            compatible_with=["ROAD"],
            grid_category="outer_grid"
        ))
        self.register(ConnectorDefinition(
            name="BUILDING",
            compatible_with=["BUILDING"],
            grid_category="outer_grid"
        ))
        self.register(ConnectorDefinition(
            name="PAVEMENTPOS",
            compatible_with=["PAVEMENTNEG"],
            grid_category="outer_grid",
            is_symmetric=False
        ))
        self.register(ConnectorDefinition(
            name="PAVEMENTNEG",
            compatible_with=["PAVEMENTPOS"],
            grid_category="outer_grid",
            is_symmetric=False
        ))
    
    def register(self, connector: ConnectorDefinition):
        """Register a new connector type"""
        self.connectors[connector.name] = connector
    
    def get(self, name: str) -> ConnectorDefinition:
        """Get connector definition by name"""
        return self.connectors.get(name)
    
    def matches(self, connector_a: str, connector_b: str) -> bool:
        """
        Check if two connectors are compatible
        
        Replaces hardcoded sockets_match() function!
        """
        conn_a = self.get(connector_a)
        if not conn_a:
            return False
        
        return connector_b in conn_a.compatible_with
    
    def get_all_for_category(self, grid_category: str) -> List[ConnectorDefinition]:
        """Get all connectors for a specific grid category"""
        return [c for c in self.connectors.values() 
                if c.grid_category == grid_category]
    
    def to_dict(self) -> dict:
        """Export all connectors to dict for JSON persistence"""
        return {
            "connectors": [
                {
                    "name": c.name,
                    "description": c.description,
                    "compatible_with": c.compatible_with,
                    "grid_category": c.grid_category,
                    "is_symmetric": c.is_symmetric
                }
                for c in self.connectors.values()
            ]
        }
    
    def from_dict(self, data: dict):
        """Load connectors from dict (JSON)"""
        self.connectors.clear()
        for connector_data in data.get("connectors", []):
            self.register(ConnectorDefinition(
                name=connector_data["name"],
                description=connector_data.get("description", ""),
                compatible_with=connector_data.get("compatible_with", []),
                grid_category=connector_data.get("grid_category", "outer_grid"),
                is_symmetric=connector_data.get("is_symmetric", True)
            ))
    
    def save_to_file(self, filepath: str):
        """Save connector registry to JSON file"""
        import json
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def load_from_file(self, filepath: str):
        """Load connector registry from JSON file"""
        import json
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.from_dict(data)

# Global instance
connector_registry = ConnectorRegistry()
```

---

## 📄 JSON Persistence Format

### **Connector Library File**

```json
{
  "format_version": "1.0",
  "connectors": [
    {
      "name": "ROAD",
      "description": "Road connector - matches roads",
      "compatible_with": ["ROAD"],
      "grid_category": "outer_grid",
      "is_symmetric": true
    },
    {
      "name": "BUILDING",
      "description": "Building connector - matches buildings",
      "compatible_with": ["BUILDING"],
      "grid_category": "outer_grid",
      "is_symmetric": true
    },
    {
      "name": "PAVEMENTPOS",
      "description": "Pavement positive edge",
      "compatible_with": ["PAVEMENTNEG"],
      "grid_category": "outer_grid",
      "is_symmetric": false
    },
    {
      "name": "PAVEMENTNEG",
      "description": "Pavement negative edge",
      "compatible_with": ["PAVEMENTPOS"],
      "grid_category": "outer_grid",
      "is_symmetric": false
    },
    {
      "name": "WALL",
      "description": "Solid wall",
      "compatible_with": ["WALL", "DOOR", "WINDOW"],
      "grid_category": "building",
      "is_symmetric": true
    },
    {
      "name": "DOOR",
      "description": "Door opening",
      "compatible_with": ["WALL", "DOOR", "HALLWAY"],
      "grid_category": "building",
      "is_symmetric": true
    }
  ]
}
```

**File Location:** `addons/blender-wfc/data/connectors.json`

---

## 🔧 Code Refactoring

### **1. Replace `sockets_match()` Function**

```python
# OLD (wfc_classes.py)
def sockets_match(socket_a, socket_b):
    if (socket_a == 'ROAD'):
        if (socket_b == 'ROAD'):
            return True
        else:
            return False
    # ... 20+ lines of hardcoded rules

# NEW (use connector registry)
def sockets_match(socket_a, socket_b):
    """Compatibility check using connector registry"""
    from .connector_registry import connector_registry
    return connector_registry.matches(socket_a, socket_b)
```

### **2. Update BlenderWFCAdapter**

```python
# wfc_blender_adapter.py

def _sockets_match(self, socket_a, socket_b):
    """Use connector registry instead of hardcoded rules"""
    from .connector_registry import connector_registry
    return connector_registry.matches(socket_a, socket_b)
```

### **3. Update wfc_enums.py - Generate from Registry**

```python
# wfc_enums.py

# OLD: Hardcoded list
CONNECTORS = [
    ('ROAD', "Road", ""),
    ('BUILDING', "Building", ""),
    ('PAVEMENTPOS', "PavementPos", ""),
    ('PAVEMENTNEG', "PavementNeg", "")
]

# NEW: Generated from registry
def get_connector_enum_items():
    """Generate Blender enum items from connector registry"""
    from .connector_registry import connector_registry

    items = []
    for connector in connector_registry.connectors.values():
        items.append((
            connector.name,
            connector.name.replace('_', ' ').title(),
            connector.description
        ))
    return items

# For backward compatibility, create default list
CONNECTORS = get_connector_enum_items()

# For dynamic contexts (operators)
def get_connector_items_for_category(grid_category: str):
    """Get connector enum items filtered by grid category"""
    from .connector_registry import connector_registry

    items = []
    for connector in connector_registry.get_all_for_category(grid_category):
        items.append((
            connector.name,
            connector.name.replace('_', ' ').title(),
            connector.description
        ))
    return items
```

---

## 🎨 UI Integration

### **Connector Management Panel (Optional)**

```python
class OBJECT_PT_WFCConnectorManagerPanel(bpy.types.Panel):
    """Panel for managing connector definitions"""
    bl_label = "Connector Manager"
    bl_idname = "OBJECT_PT_WFCConnectorManagerPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = bl_category_name

    def draw(self, context):
        layout = self.layout

        # List all connectors by category
        box = layout.box()
        box.label(text="Outer Grid Connectors:", icon='LINKED')
        for conn in connector_registry.get_all_for_category("outer_grid"):
            row = box.row()
            row.label(text=f"{conn.name} → {', '.join(conn.compatible_with)}")

        box = layout.box()
        box.label(text="Building Connectors:", icon='HOME')
        for conn in connector_registry.get_all_for_category("building"):
            row = box.row()
            row.label(text=f"{conn.name} → {', '.join(conn.compatible_with)}")

        layout.separator()

        # Management operators
        layout.operator("object.wfc_reload_connectors", text="Reload from File", icon='FILE_REFRESH')
        layout.operator("object.wfc_save_connectors", text="Save to File", icon='FILE_TICK')
```

### **Update Primitive UI - Filter Connectors by Category**

```python
class OBJECT_OT_WFCAssignConnectors(bpy.types.Operator):
    """Assign connectors with category-filtered options"""

    # ... existing code ...

    def invoke(self, context, event):
        obj = context.object

        # Get grid category from object
        grid_category = obj.get("grid_category", "outer_grid")

        # Dynamically get connectors for this category
        # (This requires updating enum properties to support dynamic callbacks)

        return context.window_manager.invoke_props_dialog(self, width=400)
```

---

## 📦 File Structure

### **New Files to Create**

```
addons/blender-wfc/
├── connector_registry.py          # NEW: ConnectorRegistry class
├── data/
│   └── connectors.json            # NEW: Default connector definitions
└── (existing files...)
```

---

## 🔄 Migration Strategy

### **Phase 1: Create Registry System** (1-2 hours)
1. Create `connector_registry.py` with `ConnectorDefinition` and `ConnectorRegistry`
2. Create default `data/connectors.json` with current connectors
3. Load registry on addon startup

### **Phase 2: Update Code to Use Registry** (1 hour)
1. Replace `sockets_match()` to call `connector_registry.matches()`
2. Update `BlenderWFCAdapter._sockets_match()`
3. Test that existing primitives still work

### **Phase 3: Make Enums Dynamic** (1 hour)
1. Update `wfc_enums.py` to generate from registry
2. Update `__init__.py` property registration to use dynamic enums
3. Test UI still shows correct connectors

### **Phase 4: Add Building Connectors** (30 min)
1. Add building connector definitions to `connectors.json`
2. Test that they load correctly
3. Verify inner grid can use them

---

## ✅ Benefits

| Before | After |
|--------|-------|
| ❌ Hardcoded in `sockets_match()` | ✅ Loaded from `connectors.json` |
| ❌ Can't add connectors without code | ✅ Edit JSON file, reload |
| ❌ One set of connectors for all grids | ✅ Different connectors per grid category |
| ❌ Rules lost between sessions | ✅ Persisted and version-controlled |
| ❌ Difficult to understand matching | ✅ Self-documenting JSON |

---

## 🎯 Complete Example Workflow

### **Old Workflow (Hardcoded)**
```python
# User wants to add "WINDOW" connector
# 1. Edit wfc_enums.py → add ('WINDOW', "Window", "")
# 2. Edit wfc_classes.py → add if statement in sockets_match()
# 3. Edit __init__.py → register property
# 4. Reload addon
# ❌ Error-prone, requires code editing
```

### **New Workflow (Metadata)**
```json
// Edit data/connectors.json
{
  "connectors": [
    // ... existing connectors ...
    {
      "name": "WINDOW",
      "description": "Window opening",
      "compatible_with": ["WALL", "WINDOW"],
      "grid_category": "building",
      "is_symmetric": true
    }
  ]
}
```
```python
# In Blender:
# 1. Click "Reload Connectors" button
# ✅ Done! WINDOW connector now available
```

---

## 🚀 Implementation Plan

### **Combined with Primitive Sizing**

**Total Effort: ~10-12 hours**

| Phase | Task | Time |
|-------|------|------|
| **1A** | Add sizing fields to PrimitiveData | 1h |
| **1B** | Create ConnectorRegistry system | 2h |
| **2** | Update code to use metadata (sizing + connectors) | 2h |
| **3** | Create default connectors.json | 1h |
| **4** | Update UI for sizing + categories | 2h |
| **5** | Test: Create primitive with all metadata | 1h |
| **6** | Refactor module generation | 2h |
| **7** | Full integration testing | 2h |

---

## 📝 Default Connector Definitions

### **For Outer Grid**
- `ROAD` → matches `ROAD`
- `BUILDING` → matches `BUILDING`
- `PAVEMENTPOS` → matches `PAVEMENTNEG`
- `PAVEMENTNEG` → matches `PAVEMENTPOS`

### **For Building Inner Grid (NEW)**
- `WALL` → matches `WALL`, `DOOR`, `WINDOW`
- `DOOR` → matches `WALL`, `DOOR`, `HALLWAY`
- `WINDOW` → matches `WALL`, `WINDOW`
- `HALLWAY` → matches `HALLWAY`, `DOOR`
- `EMPTY` → matches `EMPTY` (empty rooms)

### **For Park Inner Grid (Future)**
- `GRASS` → matches `GRASS`, `PATH`
- `PATH` → matches `PATH`, `GRASS`, `FOUNTAIN`
- `FOUNTAIN` → matches `PATH`
- `TREE` → matches `GRASS`

---

**Ready to implement this system alongside the primitive sizing metadata?** This gives you a **complete metadata-driven system** with zero hardcoded values!
```
