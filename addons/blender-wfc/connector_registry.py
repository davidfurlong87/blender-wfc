"""
Connector Registry System

Defines connector types and their compatibility rules using persisted metadata
instead of hardcoded logic.

This replaces the hardcoded sockets_match() function with a flexible,
JSON-based system that can be extended without code changes.

Task 1B.1 - Part of Milestone 1: Core Metadata System
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import json
from pathlib import Path


@dataclass
class ConnectorDefinition:
    """
    Defines a connector type and its compatibility rules
    
    Attributes:
        name: Connector identifier (e.g., 'ROAD', 'WALL', 'DOOR')
        description: Human-readable description
        compatible_with: List of connector names this can connect to
        grid_category: Which grid system this belongs to ('outer_grid', 'building', etc.)
        is_symmetric: If True, matches with itself. If False, only matches others in list
    
    Example:
        ROAD = ConnectorDefinition(
            name="ROAD",
            description="Road connector",
            compatible_with=["ROAD"],  # Matches itself
            grid_category="outer_grid",
            is_symmetric=True
        )
    """
    name: str
    description: str = ""
    compatible_with: List[str] = field(default_factory=list)
    grid_category: str = "outer_grid"
    is_symmetric: bool = True
    
    def matches(self, other_connector_name: str) -> bool:
        """Check if this connector is compatible with another"""
        return other_connector_name in self.compatible_with
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'description': self.description,
            'compatible_with': self.compatible_with,
            'grid_category': self.grid_category,
            'is_symmetric': self.is_symmetric
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ConnectorDefinition':
        """Create from dictionary (JSON deserialization)"""
        return cls(
            name=data['name'],
            description=data.get('description', ''),
            compatible_with=data.get('compatible_with', []),
            grid_category=data.get('grid_category', 'outer_grid'),
            is_symmetric=data.get('is_symmetric', True)
        )


class ConnectorRegistry:
    """
    Global registry of all connector definitions
    
    This class manages connector types and provides the core matching logic
    that replaces the hardcoded sockets_match() function.
    
    Usage:
        registry = ConnectorRegistry()
        
        # Register a connector
        registry.register(ConnectorDefinition(
            name="ROAD",
            compatible_with=["ROAD"]
        ))
        
        # Check compatibility
        if registry.matches("ROAD", "ROAD"):
            print("Compatible!")
        
        # Save/load to JSON
        registry.save_to_file("connectors.json")
        registry.load_from_file("connectors.json")
    """
    
    def __init__(self):
        self.connectors: Dict[str, ConnectorDefinition] = {}
        self._load_defaults()
    
    def _load_defaults(self):
        """Load default connector definitions for outer grid"""
        # Outer grid connectors (from existing hardcoded system)
        self.register(ConnectorDefinition(
            name="ROAD",
            description="Road connector - matches roads",
            compatible_with=["ROAD"],
            grid_category="outer_grid",
            is_symmetric=True
        ))
        
        self.register(ConnectorDefinition(
            name="BUILDING",
            description="Building connector - matches buildings",
            compatible_with=["BUILDING"],
            grid_category="outer_grid",
            is_symmetric=True
        ))
        
        self.register(ConnectorDefinition(
            name="PAVEMENTPOS",
            description="Pavement positive edge",
            compatible_with=["PAVEMENTNEG"],
            grid_category="outer_grid",
            is_symmetric=False
        ))
        
        self.register(ConnectorDefinition(
            name="PAVEMENTNEG",
            description="Pavement negative edge",
            compatible_with=["PAVEMENTPOS"],
            grid_category="outer_grid",
            is_symmetric=False
        ))
    
    def register(self, connector: ConnectorDefinition):
        """
        Register a new connector type
        
        Args:
            connector: ConnectorDefinition to register
        """
        self.connectors[connector.name] = connector
    
    def get(self, name: str) -> Optional[ConnectorDefinition]:
        """
        Get connector definition by name

        Args:
            name: Connector name

        Returns:
            ConnectorDefinition or None if not found
        """
        return self.connectors.get(name)

    def matches(self, connector_a: str, connector_b: str) -> bool:
        """
        Check if two connectors are compatible

        This is the KEY METHOD that replaces the hardcoded sockets_match() function!

        Args:
            connector_a: First connector name
            connector_b: Second connector name

        Returns:
            True if connectors are compatible, False otherwise

        Example:
            >>> registry.matches("ROAD", "ROAD")
            True
            >>> registry.matches("ROAD", "BUILDING")
            False
            >>> registry.matches("PAVEMENTPOS", "PAVEMENTNEG")
            True
        """
        conn_a = self.get(connector_a)
        if not conn_a:
            # Unknown connector - return False
            return False

        return conn_a.matches(connector_b)

    def get_all_for_category(self, grid_category: str) -> List[ConnectorDefinition]:
        """
        Get all connectors for a specific grid category

        Args:
            grid_category: Grid category name ('outer_grid', 'building', etc.)

        Returns:
            List of ConnectorDefinitions for that category
        """
        return [c for c in self.connectors.values()
                if c.grid_category == grid_category]

    def get_all_names(self) -> List[str]:
        """Get list of all registered connector names"""
        return list(self.connectors.keys())

    def to_dict(self) -> dict:
        """
        Export all connectors to dictionary for JSON persistence

        Returns:
            Dictionary with format version and connector list
        """
        return {
            'format_version': '1.0',
            'connectors': [c.to_dict() for c in self.connectors.values()]
        }

    def from_dict(self, data: dict):
        """
        Load connectors from dictionary (JSON)

        Args:
            data: Dictionary from JSON file
        """
        # Clear existing connectors
        self.connectors.clear()

        # Load connectors from data
        for connector_data in data.get('connectors', []):
            connector = ConnectorDefinition.from_dict(connector_data)
            self.register(connector)

    def save_to_file(self, filepath: str):
        """
        Save connector registry to JSON file

        Args:
            filepath: Path to JSON file
        """
        import json
        from pathlib import Path

        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    def load_from_file(self, filepath: str) -> bool:
        """
        Load connector registry from JSON file

        Args:
            filepath: Path to JSON file

        Returns:
            True if loaded successfully, False if file not found
        """
        import json
        from pathlib import Path

        path = Path(filepath)
        if not path.exists():
            return False

        try:
            with open(path, 'r') as f:
                data = json.load(f)
                self.from_dict(data)
            return True
        except Exception as e:
            print(f"Error loading connector registry: {e}")
            return False

    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"ConnectorRegistry({len(self.connectors)} connectors: {', '.join(self.get_all_names())})"


# Global singleton instance
# This is the main instance used throughout the codebase
connector_registry = ConnectorRegistry()
