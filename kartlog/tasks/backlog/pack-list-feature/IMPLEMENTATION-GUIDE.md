# Implementation Guide: Pack List Feature

## Overview

This guide provides the execution strategy for implementing the pack list feature across 5 subtasks organized into 3 waves.

## Architecture Decisions

### Approach: Hybrid Copy-on-Create
- Templates and meeting lists are separate collections
- Meeting lists copy template data at creation time
- No live references (changes to template don't affect existing lists)
- Meeting-specific items tracked with `addedToList: true` flag

### Testing: Full TDD
- Write tests before implementation
- Each subtask includes test requirements
- Quality gates enforced at completion

## Execution Waves

### Wave 1: Foundation (Sequential)

**Must complete before Wave 2**

#### TASK-PL-001: Data Model & Repository Layer
- Create `src/lib/firestore/packTemplates.js`
- Create `src/lib/firestore/packLists.js`
- Implement CRUD operations following existing patterns
- Add `createFromTemplate()` function for list creation

**Key Files**:
```
src/lib/firestore/packTemplates.js
src/lib/firestore/packLists.js
```

---

### Wave 2: UI Components (Parallel)

**Can execute TASK-PL-002 and TASK-PL-003 simultaneously**

#### TASK-PL-002: Master Template Management UI

**Components**:
```
src/routes/PackTemplates.svelte      # List all templates
src/routes/NewPackTemplate.svelte    # Create template
src/routes/EditPackTemplate.svelte   # Edit template
```

**Features**:
- SMUI DataTable for template list
- Category management (add/remove/reorder)
- Item management within categories
- Edit/Delete actions

#### TASK-PL-003: Meeting Pack List UI

**Components**:
```
src/routes/PackLists.svelte          # List all meeting lists
src/routes/NewPackList.svelte        # Create from template
src/routes/ViewPackList.svelte       # Check items, manage list
```

**Features**:
- Template selection when creating new list
- Meeting name and date assignment
- Checkbox interface for packing items
- Add custom items to list
- Archive completed lists

---

### Wave 3: Features & Integration (Parallel)

**Can execute TASK-PL-004 and TASK-PL-005 simultaneously**

#### TASK-PL-004: Item Promotion & History

**Features**:
- "Add to master template" action on meeting-specific items
- View archived/historical lists
- Filter lists by date range
- Statistics on item usage

#### TASK-PL-005: Navigation & Integration

**Changes**:
```
src/App.svelte                       # Add routes
src/routes/Dashboard.svelte          # Optional widgets
```

**Routes to add**:
```javascript
'/pack-templates': PackTemplates,
'/pack-templates/new': NewPackTemplate,
'/pack-templates/:id': EditPackTemplate,
'/pack-lists': PackLists,
'/pack-lists/new': NewPackList,
'/pack-lists/:id': ViewPackList,
```

---

## Conductor Workspace Assignments

For parallel execution with Conductor:

| Wave | Task | Workspace Name |
|------|------|----------------|
| 2 | TASK-PL-002 | pack-list-wave2-templates |
| 2 | TASK-PL-003 | pack-list-wave2-lists |
| 3 | TASK-PL-004 | pack-list-wave3-features |
| 3 | TASK-PL-005 | pack-list-wave3-nav |

## Testing Requirements (TDD)

### Repository Layer Tests
- Test CRUD operations for templates
- Test CRUD operations for pack lists
- Test `createFromTemplate()` copies correctly
- Test user scoping (userId filter)

### UI Component Tests
- Test template list rendering
- Test category/item management
- Test checkbox state persistence
- Test item promotion flow

### Integration Tests
- Test full flow: create template -> create list -> check items -> archive
- Test promotion: add item to list -> promote to master

## Dependencies

### External
- Firebase/Firestore (existing)
- SMUI components (existing)

### Internal
- Wave 2 depends on Wave 1
- Wave 3 depends on Wave 2

## File Conflict Analysis

**No conflicts detected** - all new files:
- Wave 2 tasks create different component sets
- Wave 3 tasks modify different areas (features vs navigation)

## Quality Gates

Each subtask must pass:
1. All tests passing (TDD - tests written first)
2. No TypeScript/linting errors
3. Code review checklist
4. Manual verification of feature

## Next Steps

1. Start with TASK-PL-001 (repository layer)
2. After completion, run TASK-PL-002 and TASK-PL-003 in parallel
3. After both complete, run TASK-PL-004 and TASK-PL-005 in parallel
4. Final integration testing
