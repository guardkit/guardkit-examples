---
id: TASK-PL-005
title: Add navigation and integration
status: backlog
created: 2025-12-15T00:00:00Z
updated: 2025-12-15T00:00:00Z
priority: medium
tags: [pack-list, navigation, integration, routing]
complexity: 3
parent_feature: pack-list-feature
wave: 3
execution_mode: direct
testing_mode: tdd
dependencies: [TASK-PL-002, TASK-PL-003]
blocks: []
conductor_workspace: pack-list-wave3-nav
---

# Add Navigation and Integration

## Description

Integrate the pack list feature into the kartlog application by adding routes, navigation menu items, and optional dashboard widgets.

## Acceptance Criteria

- [ ] All pack list routes added to `App.svelte`
- [ ] Navigation menu updated with pack list links
- [ ] Routes work correctly (no 404s)
- [ ] Navigation icons appropriate
- [ ] Optional: Dashboard widget for active pack lists
- [ ] Tests for route configuration

## Technical Specification

### Routes to Add (`src/App.svelte`)

```javascript
import PackTemplates from './routes/PackTemplates.svelte';
import NewPackTemplate from './routes/NewPackTemplate.svelte';
import EditPackTemplate from './routes/EditPackTemplate.svelte';
import PackLists from './routes/PackLists.svelte';
import NewPackList from './routes/NewPackList.svelte';
import ViewPackList from './routes/ViewPackList.svelte';

const routes = {
  // ... existing routes ...

  // Pack Templates (master lists)
  '/pack-templates': PackTemplates,
  '/pack-templates/new': NewPackTemplate,
  '/pack-templates/:id': EditPackTemplate,

  // Pack Lists (meeting-specific)
  '/pack-lists': PackLists,
  '/pack-lists/new': NewPackList,
  '/pack-lists/:id': ViewPackList,
};
```

### Navigation Menu

**Location**: Sidebar or header navigation (check existing pattern)

```svelte
<!-- Add to navigation component -->
<ListItem href="/pack-templates">
  <Icon slot="graphic">checklist</Icon>
  <Text>Pack Templates</Text>
</ListItem>

<ListItem href="/pack-lists">
  <Icon slot="graphic">inventory_2</Icon>
  <Text>Pack Lists</Text>
</ListItem>
```

**Icon Suggestions**:
- Pack Templates: `checklist`, `playlist_add_check`, `fact_check`
- Pack Lists: `inventory_2`, `luggage`, `backpack`

### Dashboard Widget (Optional)

**In Dashboard.svelte**:

```svelte
<script>
  import { getUserPackLists } from '$lib/firestore/packLists';

  let activeLists = [];

  onMount(async () => {
    const lists = await getUserPackLists('active');
    activeLists = lists.slice(0, 3); // Show top 3
  });
</script>

{#if activeLists.length > 0}
  <Card>
    <h3>Active Pack Lists</h3>
    {#each activeLists as list}
      <a href="/pack-lists/{list.id}">
        <div class="pack-list-widget">
          <span>{list.meetingName}</span>
          <span>{list.checkedCount}/{list.totalItems}</span>
          <LinearProgress progress={list.checkedCount / list.totalItems} />
        </div>
      </a>
    {/each}
    <Button href="/pack-lists">View All</Button>
  </Card>
{/if}
```

### Mobile Navigation

Ensure pack list items appear in mobile hamburger menu:

```svelte
<!-- Mobile menu items -->
<Item on:click={() => { push('/pack-templates'); closeMenu(); }}>
  <Icon>checklist</Icon>
  <span>Pack Templates</span>
</Item>
<Item on:click={() => { push('/pack-lists'); closeMenu(); }}>
  <Icon>inventory_2</Icon>
  <span>Pack Lists</span>
</Item>
```

## Files to Modify

```
src/App.svelte                    # Add routes
src/routes/Dashboard.svelte       # Optional widget
src/components/Navigation.svelte  # If exists, add menu items
```

## Test Requirements

### Route Tests
- All routes resolve to correct components
- Route parameters (`:id`) work correctly
- Authenticated routes require login

### Navigation Tests
- Menu items visible when logged in
- Links navigate to correct pages
- Mobile menu includes new items

## Estimated Effort

1-2 hours

## Notes

- Can run in parallel with TASK-PL-004
- Conductor workspace: `pack-list-wave3-nav`
- This is marked as `direct` execution mode (simpler task)
