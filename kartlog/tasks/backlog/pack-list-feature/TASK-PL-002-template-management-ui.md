---
id: TASK-PL-002
title: Build master template management UI
status: backlog
created: 2025-12-15T00:00:00Z
updated: 2025-12-15T00:00:00Z
priority: high
tags: [pack-list, ui, svelte, templates]
complexity: 5
parent_feature: pack-list-feature
wave: 2
execution_mode: task-work
testing_mode: tdd
dependencies: [TASK-PL-001]
blocks: [TASK-PL-004]
conductor_workspace: pack-list-wave2-templates
---

# Build Master Template Management UI

## Description

Create the Svelte components for managing pack list templates (master lists). Users can create, edit, and delete templates with categories and items.

## Acceptance Criteria

- [ ] `PackTemplates.svelte` - List all user's templates
- [ ] `NewPackTemplate.svelte` - Create new template with categories/items
- [ ] `EditPackTemplate.svelte` - Edit existing template
- [ ] Category management (add, rename, reorder, delete)
- [ ] Item management within categories (add, edit, delete)
- [ ] SMUI components used consistently with existing app
- [ ] Responsive design (mobile-friendly)
- [ ] Tests written FIRST (TDD approach)

## Technical Specification

### PackTemplates.svelte (List View)

```svelte
<!-- Pattern: Follow Tyres.svelte exactly -->
<script>
  import { onMount } from 'svelte';
  import { push } from 'svelte-spa-router';
  import { getUserPackTemplates, deletePackTemplate } from '$lib/firestore/packTemplates';

  let templates = [];
  let loading = true;

  onMount(async () => {
    templates = await getUserPackTemplates();
    loading = false;
  });
</script>

<!-- SMUI DataTable with columns: Name, Categories, Items, Actions -->
```

**Columns**:
- Name (clickable to edit)
- Categories count
- Items count
- Last updated
- Actions (Edit, Delete)

### NewPackTemplate.svelte (Create)

**Form Fields**:
- Name (required)
- Description (optional)
- Categories section (dynamic list)
- Items section (grouped by category)

**Category Management**:
- Add category button
- Inline rename
- Drag to reorder (or up/down buttons)
- Delete with confirmation

**Item Management**:
- Add item to category
- Edit item name
- Delete item
- Move item between categories (optional)

### EditPackTemplate.svelte (Edit)

Same as NewPackTemplate but:
- Load existing data in `onMount`
- Update instead of create on submit
- Show item count statistics

## UI Components to Use

From SMUI (already in project):
- `DataTable`, `Head`, `Body`, `Row`, `Cell`
- `Button`, `IconButton`
- `Textfield`
- `Card`
- `List`, `Item`
- `Menu` (for actions)

## Design Patterns

Follow existing patterns from:
- `src/routes/Tyres.svelte` - List view pattern
- `src/routes/NewTyre.svelte` - Create form pattern
- `src/routes/EditTyre.svelte` - Edit form pattern

## Test Requirements (TDD)

### Component Tests
- Template list renders correctly with mock data
- Create form validates required fields
- Category add/remove updates state
- Item add/remove updates state
- Form submission calls repository functions

## Files to Create

```
src/routes/PackTemplates.svelte
src/routes/NewPackTemplate.svelte
src/routes/EditPackTemplate.svelte
```

## Estimated Effort

3-4 hours (including TDD test writing)

## Notes

- Can run in parallel with TASK-PL-003 (different components)
- Conductor workspace: `pack-list-wave2-templates`
