# Blender WFC Documentation

Welcome to the Blender WFC addon documentation! This folder contains guides and references for developing and maintaining the addon.

## 📚 Documentation Index

### For New Contributors

Start here if you're new to the project:

1. **[../PROJECT_OVERVIEW.md](../PROJECT_OVERVIEW.md)** - Start here!
   - Project vision and goals
   - Architecture overview
   - Current status and roadmap
   - Known issues and TODOs

2. **[QUICK_START_RELOADING.md](QUICK_START_RELOADING.md)** - Essential reading
   - Simple steps for adding new modules
   - Common scenarios with examples
   - Troubleshooting guide

### Deep Dives

For understanding specific systems:

3. **[MODULE_RELOADING_GUIDE.md](MODULE_RELOADING_GUIDE.md)** - Complete reference
   - How Python module reloading works under the hood
   - The correct reload pattern
   - Common pitfalls and how to avoid them
   - Testing your reload system

4. **[MODULE_DEPENDENCY_MAP.md](MODULE_DEPENDENCY_MAP.md)** - Visual reference
   - Complete dependency tree
   - Module purposes and exports
   - Dependency rules
   - When to create new modules

## 🚀 Quick Links by Task

### "I want to add a new Python file to the addon"
→ Read [QUICK_START_RELOADING.md](QUICK_START_RELOADING.md)

### "I'm getting import errors or my changes aren't showing up"
→ Check [MODULE_RELOADING_GUIDE.md](MODULE_RELOADING_GUIDE.md) → Common Pitfalls section

### "I need to understand what a module does"
→ See [MODULE_DEPENDENCY_MAP.md](MODULE_DEPENDENCY_MAP.md) → Module Purposes table

### "I want to understand the overall architecture"
→ Read [../PROJECT_OVERVIEW.md](../PROJECT_OVERVIEW.md) → Current Architecture section

### "I want to know what needs to be done"
→ Check [../PROJECT_OVERVIEW.md](../PROJECT_OVERVIEW.md) → Known Issues & TODOs section

## 🎯 Development Principles

### The Golden Rules

1. **Reload Before Import** - Always reload modules before importing from them
2. **Respect Dependencies** - Lower-level modules cannot import from higher-level ones
3. **Test Reloads** - After adding a module, test that reload works (disable/enable addon)
4. **Performance Matters** - Avoid unnecessary mesh operations
5. **Document as You Go** - Update these docs when you change architecture

### Code Organization Philosophy

```
Low Level (Foundation)
    ↓
Mid Level (Data Structures)
    ↓
High Level (Logic & Algorithms)
    ↓
Top Level (UI & Operators)
```

Each level can only import from levels below it.

## 📖 Reading Order for New Developers

**Day 1: Understanding the Project**
1. Read PROJECT_OVERVIEW.md (30 minutes)
2. Skim MODULE_DEPENDENCY_MAP.md to see the structure (10 minutes)
3. Open Blender and test the addon (30 minutes)

**Day 2: Making Your First Change**
1. Read QUICK_START_RELOADING.md (15 minutes)
2. Make a small change to an existing module (30 minutes)
3. Test the reload system works (15 minutes)

**Day 3: Adding New Features**
1. Read MODULE_RELOADING_GUIDE.md for deep understanding (30 minutes)
2. Plan your new module using MODULE_DEPENDENCY_MAP.md (20 minutes)
3. Implement and test (varies)

## 🔧 Maintenance

### Keeping Documentation Updated

When you make changes, update the relevant docs:

| You Changed... | Update This Doc... |
|----------------|-------------------|
| Added a new module | QUICK_START_RELOADING.md, MODULE_DEPENDENCY_MAP.md |
| Changed module dependencies | MODULE_DEPENDENCY_MAP.md |
| Fixed a major issue | PROJECT_OVERVIEW.md (mark TODO as done) |
| Added a new feature | PROJECT_OVERVIEW.md (Current Architecture) |
| Found a new issue | PROJECT_OVERVIEW.md (Known Issues) |

### Documentation Style

- Use clear, simple language
- Include code examples
- Use ✅ ❌ ⚠️ symbols for quick scanning
- Keep examples realistic (from actual codebase)
- Update dates when making major revisions

## 🤝 Contributing to Docs

Good documentation is as important as good code! If you:
- Find something confusing → Open an issue or improve it
- Learn something the hard way → Document it for others
- Solve a tricky problem → Add it to troubleshooting

## 📝 Document Versions

- **MODULE_RELOADING_GUIDE.md** - Created 2026-02-05
- **QUICK_START_RELOADING.md** - Created 2026-02-05
- **MODULE_DEPENDENCY_MAP.md** - Created 2026-02-05
- **README.md** (this file) - Created 2026-02-05

---

**Remember:** Good documentation saves hours of debugging and confusion. Keep it updated! 📚✨

