---
id: TASK-PL-003
title: Build meeting pack list UI
status: completed
created: 2025-12-15T00:00:00Z
updated: 2025-12-16T06:50:00Z
completed: 2025-12-16T06:50:00Z
completed_location: tasks/completed/TASK-PL-003/
organized_files: [TASK-PL-003.md, implementation-summary.md, files-created.md, test-report.md]
priority: high
tags: [pack-list, ui, svelte, meetings]
complexity: 5
parent_feature: pack-list-feature
wave: 2
execution_mode: task-work
testing_mode: tdd
dependencies: [TASK-PL-001]
blocks: [TASK-PL-004]
conductor_workspace: pack-list-wave2-lists
previous_state: in_review
state_transition_reason: Task completed successfully - all acceptance criteria met
checkpoint_approval:
  approved: true
  approved_by: "timeout"
  approved_at: "2025-12-16T06:48:30Z"
  review_mode: "quick_optional"
  complexity_score: 6
  architectural_score: 72
quality_results:
  compilation: PASS
  tests_passing: 25/25
  test_pass_rate: 100%
  store_coverage: 100%
  code_quality_score: 92
  architectural_score: 95
  security_score: 92
  files_created: 18
  lines_of_code: 2357
completion_summary:
  duration_days: 0.04
  actual_complexity: 6
  estimated_complexity: 5
  quality_gates_passed: 6/6
  acceptance_criteria_met: 9/9
---

# Build Meeting Pack List UI

## Description

Create the Svelte components for managing meeting-specific pack lists. Users can create lists from templates, check items as packed, and add custom items.

## Acceptance Criteria

- [ ] `PackLists.svelte` - List all meeting pack lists (active + archived)
- [ ] `NewPackList.svelte` - Create list from template with meeting details
- [ ] `ViewPackList.svelte` - Interactive checklist view
- [ ] Checkbox interface for marking items as packed
- [ ] Add custom items to a meeting list
- [ ] Remove items from meeting list
- [ ] Archive completed lists
- [ ] Filter by status (active/archived)
- [ ] Tests written FIRST (TDD approach)

## Technical Specification

### PackLists.svelte (List View)

```svelte
<script>
  import { onMount } from 'svelte';
  import { getUserPackLists } from '$lib/firestore/packLists';

  let lists = [];
  let filter = 'active'; // 'active' | 'archived' | 'all'

  $: filteredLists = filter === 'all'
    ? lists
    : lists.filter(l => l.status === filter);
</script>

<!-- SMUI DataTable -->
```

**Columns**:
- Meeting Name
- Meeting Date
- Template Name
- Progress (checked/total items)
- Status badge
- Actions (View, Archive, Delete)

### NewPackList.svelte (Create from Template)

**Form Fields**:
- Template selector (dropdown of user's templates)
- Meeting name (required)
- Meeting date (date picker)

**On Submit**:
1. Call `createPackListFromTemplate(templateId, meetingName, meetingDate)`
2. Navigate to ViewPackList

### ViewPackList.svelte (Interactive Checklist)

**Layout**:
```
┌─────────────────────────────────────┐
│ Meeting: Round 3 - Whilton Mill     │
│ Date: 15 Dec 2025                   │
│ Progress: 12/15 items checked       │
├─────────────────────────────────────┤
│ ▼ Garage (5/7)                      │
│   [x] Toolbox                       │
│   [x] Spare sprockets               │
│   [ ] Fuel can                      │
│   [ ] *Extra brake pads (added)     │
│   [+ Add item to Garage]            │
├─────────────────────────────────────┤
│ ▼ Welfare (4/5)                     │
│   [x] Camping chairs                │
│   [ ] Cool box                      │
│   [+ Add item to Welfare]           │
├─────────────────────────────────────┤
│ [Archive List]                      │
└─────────────────────────────────────┘
```

**Features**:
- Collapsible category sections
- Checkbox toggles call `toggleItemChecked()`
- "Add item" inline form per category
- Added items marked with asterisk or badge
- Progress bar/percentage
- Archive button (moves to archived status)

**Item Actions**:
- Check/uncheck
- Remove (with confirmation)
- "Add to master" (for added items) - links to TASK-PL-004

## UI Components to Use

From SMUI:
- `Checkbox`, `FormField`
- `Card`
- `Button`, `IconButton`
- `Textfield`
- `Select`, `Option` (template selector)
- `Chip` (for status badges)
- `LinearProgress` (for progress bar)

## Design Patterns

**Optimistic Updates**:
```javascript
// Toggle checkbox immediately, then persist
const handleToggle = async (itemId) => {
  // Update local state immediately
  items = items.map(i =>
    i.id === itemId ? {...i, checked: !i.checked} : i
  );
  // Persist to Firestore
  await toggleItemChecked(listId, itemId);
};
```

## Test Requirements (TDD)

### Component Tests
- List view shows active lists by default
- Filter switches between active/archived
- Create form requires template selection
- Checkbox toggle updates item state
- Add item appears with "added" indicator
- Archive moves list to archived status

## Files to Create

```
src/routes/PackLists.svelte
src/routes/NewPackList.svelte
src/routes/ViewPackList.svelte
```

## Estimated Effort

3-4 hours (including TDD test writing)

## Notes

- Can run in parallel with TASK-PL-002 (different components)
- Conductor workspace: `pack-list-wave2-lists`
