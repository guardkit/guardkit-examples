---
id: TASK-PL-004
title: Implement item promotion and history features
status: backlog
created: 2025-12-15T00:00:00Z
updated: 2025-12-15T00:00:00Z
priority: medium
tags: [pack-list, features, history, promotion]
complexity: 4
parent_feature: pack-list-feature
wave: 3
execution_mode: task-work
testing_mode: tdd
dependencies: [TASK-PL-002, TASK-PL-003]
blocks: []
conductor_workspace: pack-list-wave3-features
---

# Implement Item Promotion and History Features

## Description

Add the ability to promote meeting-specific items back to the master template, and implement history viewing/filtering for archived pack lists.

## Acceptance Criteria

- [ ] "Add to master template" action on meeting-added items
- [ ] Confirmation dialog before promotion
- [ ] Visual indicator that item was promoted
- [ ] Historical list viewing (read-only for archived)
- [ ] Filter pack lists by date range
- [ ] Item usage statistics (optional)
- [ ] Tests written FIRST (TDD approach)

## Technical Specification

### Item Promotion Flow

**In ViewPackList.svelte**:

```svelte
{#each items as item}
  <div class="item">
    <Checkbox checked={item.checked} on:change={() => toggleItem(item.id)} />
    <span>{item.name}</span>

    {#if item.addedToList && !item.promotedToMaster}
      <IconButton
        on:click={() => handlePromote(item)}
        title="Add to master template"
      >
        <Icon>add_circle</Icon>
      </IconButton>
    {/if}

    {#if item.promotedToMaster}
      <Chip>Added to master</Chip>
    {/if}
  </div>
{/each}
```

**Promotion Handler**:

```javascript
const handlePromote = async (item) => {
  const confirmed = confirm(
    `Add "${item.name}" to your master template "${templateName}"?`
  );

  if (confirmed) {
    await promoteItemToTemplate(listId, item.id, templateId);
    // Update local state to show promotion badge
    items = items.map(i =>
      i.id === item.id ? {...i, promotedToMaster: true} : i
    );
  }
};
```

### History Viewing

**Enhanced PackLists.svelte**:

```svelte
<script>
  let dateFilter = { from: null, to: null };
  let statusFilter = 'all'; // 'active' | 'archived' | 'all'

  $: filteredLists = lists.filter(list => {
    const matchesStatus = statusFilter === 'all' || list.status === statusFilter;
    const matchesDate = !dateFilter.from ||
      (list.meetingDate >= dateFilter.from && list.meetingDate <= dateFilter.to);
    return matchesStatus && matchesDate;
  });
</script>

<!-- Filter controls -->
<div class="filters">
  <Select bind:value={statusFilter}>
    <Option value="all">All Lists</Option>
    <Option value="active">Active</Option>
    <Option value="archived">Archived</Option>
  </Select>

  <Textfield type="date" bind:value={dateFilter.from} label="From" />
  <Textfield type="date" bind:value={dateFilter.to} label="To" />
</div>
```

### Archived List View

**ViewPackList.svelte** - Read-only mode for archived:

```svelte
{#if list.status === 'archived'}
  <Banner>
    This list is archived and read-only.
    <Button on:click={() => duplicateList()}>Duplicate for new meeting</Button>
  </Banner>
{/if}

<!-- Disable checkboxes for archived lists -->
<Checkbox
  checked={item.checked}
  disabled={list.status === 'archived'}
/>
```

### Item Usage Statistics (Optional Enhancement)

Track which items are most commonly added:

```javascript
// In packLists.js
export const getItemUsageStats = async () => {
  const lists = await getUserPackLists();
  const itemCounts = {};

  lists.forEach(list => {
    list.items.filter(i => i.addedToList).forEach(item => {
      itemCounts[item.name] = (itemCounts[item.name] || 0) + 1;
    });
  });

  return Object.entries(itemCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10); // Top 10 frequently added items
};
```

Display in template edit view:
```
Frequently added items (not in template):
- Extra brake pads (added 5 times)
- Rain cover (added 3 times)
[Add to template]
```

## Data Model Updates

Add to pack list items:
```javascript
{
  // existing fields...
  promotedToMaster: boolean,  // true after promotion
  promotedAt: Date            // timestamp of promotion
}
```

## Test Requirements (TDD)

### Promotion Tests
- Promote action only shows for `addedToList` items
- Promotion calls `promoteItemToTemplate()`
- Promoted items show badge and hide promote button
- Item appears in template after promotion

### History Tests
- Archived lists show in "archived" filter
- Date range filter works correctly
- Archived lists are read-only (checkboxes disabled)
- Duplicate creates new active list

## Files to Modify

```
src/routes/ViewPackList.svelte  (add promotion UI)
src/routes/PackLists.svelte     (add filters)
src/lib/firestore/packLists.js  (add stats function if needed)
```

## Estimated Effort

2-3 hours (including TDD test writing)

## Notes

- Can run in parallel with TASK-PL-005
- Conductor workspace: `pack-list-wave3-features`
