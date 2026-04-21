# Import/Export System

## Export Format
### Outer layer (suggestions)
Information regarding the pack as a whole. The theme, the number of layers/resolutions to the grid. Materials etc...
Anything which all these primitives would have in common

- Description of the primitive pack as whole (metadata?)
- Resolutions/layers included in the pack
- Corresponding dimensions for each resolution/layer, to be passed to the algorithm.
- Material names 
- (stretch goal) A material import/export system already exists somewhere, I believe
- All possible connectors and their pairs (see ### Potential Issues issues below)

### Inner layer (suggestions)
- Sections for different resolutions (i.e. a 16 x 16 primitive section, a 32 x 32 section etc)?
- The resolution scale for each primitive hardcoded.
- Faces, edges, verts, materials, vertex groups etc...
- Connectors

### Potential Issues
- Users could pass incorrect data if they overwrite the hardcoded data which was exported. When importing, this addon should loop through all the information imported, and for any failed segment display informative errors regarding what exactly didn't load and why.
- At the moment connectors and their pairs are hardcoded, and the addon won't accept anything outside of this. This is a more complicated step to solve as it requires multiple code changes. Leave this for a later step in the import/export system.

