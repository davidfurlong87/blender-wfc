## Creating packs
- 'Save to JSON' only saves a single primitive, there is no way of grouping a bunch of my primitives together and forming a pack.
- I would like the idea of a "pack" to be the default working unit. I should be able to create a new pack, and then create primitives within that pack. If I've imported a pack, I should be able to see all the primitives in that pack, and be able to create new primitives within that pack.
- There is no way of renaming/deleting a primitive once it has been created. The only way is to delete the JSON file manually.
- There is no way of knowing which primitives are in which pack. You have to open the JSON file to see.
- When creating a custom type, the name is auto-capitalised 
- Physical size isn’t updated when updating the resolution multiplier metadata. Also, there seems to be no way of setting a "pack-wide" physical size. I.e. if I want by base outer-grid primitives to be 2m, I seem to have no way of doing this

## Connector system
- Need system for adding new connectors. Current system is tightly bound to the connector_registry.py file
- No interaction between primitive creation and connector_registry. The design should be that a connector registry is specific to a particular pack
- Add feature to update primitive/connector names. Spelling mistakes become permanent  at the moment
- Quick-copy system for connectors. “Copy Type/Connectors from active”
- Alphabetise connectors. Or categorise them. Or allow the user to define both which inner grid system they connect to, plus which outer grid cell. Code already identifies where inner grid buildings would be, could use this to “tell” a building plot what it’s surrounded by


