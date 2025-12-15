---
id: TASK-PL-001
title: Create data model and repository layer for pack lists
status: backlog
created: 2025-12-15T00:00:00Z
updated: 2025-12-15T00:00:00Z
priority: high
tags: [pack-list, data-model, firestore, repository]
complexity: 6
parent_feature: pack-list-feature
wave: 1
execution_mode: task-work
testing_mode: tdd
dependencies: []
blocks: [TASK-PL-002, TASK-PL-003]
---

# Create Data Model and Repository Layer

## Description

Implement the Firestore repository layer for pack templates and pack lists, following the existing kartlog patterns (tyres, engines, chassis).

## Acceptance Criteria

- [ ] `packTemplates.js` repository with full CRUD operations
- [ ] `packLists.js` repository with full CRUD operations
- [ ] `createFromTemplate()` function that copies template to new list
- [ ] All functions filter by `userId` (user-scoped)
- [ ] Timestamps managed correctly (`createdAt`, `updatedAt`)
- [ ] Unit tests written FIRST (TDD approach)
- [ ] All tests passing

## Technical Specification

### Pack Templates Repository (`src/lib/firestore/packTemplates.js`)

```javascript
// Functions to implement:
export const addPackTemplate = async (name, description, categories, items) => {...}
export const getUserPackTemplates = async () => {...}
export const getPackTemplate = async (templateId) => {...}
export const updatePackTemplate = async (templateId, data) => {...}
export const deletePackTemplate = async (templateId) => {...}
export const addCategoryToTemplate = async (templateId, category) => {...}
export const addItemToTemplate = async (templateId, item) => {...}
export const removeItemFromTemplate = async (templateId, itemId) => {...}
```

### Pack Lists Repository (`src/lib/firestore/packLists.js`)

```javascript
// Functions to implement:
export const createPackListFromTemplate = async (templateId, meetingName, meetingDate) => {...}
export const getUserPackLists = async (status = null) => {...}  // filter by status
export const getPackList = async (listId) => {...}
export const updatePackList = async (listId, data) => {...}
export const deletePackList = async (listId) => {...}
export const toggleItemChecked = async (listId, itemId) => {...}
export const addItemToList = async (listId, item) => {...}  // sets addedToList: true
export const removeItemFromList = async (listId, itemId) => {...}
export const archivePackList = async (listId) => {...}
export const promoteItemToTemplate = async (listId, itemId, templateId) => {...}
```

### Data Structures

**Category**:
```javascript
{
  id: string,        // UUID
  name: string,      // "Garage", "Welfare", "Shopping"
  order: number      // For sorting
}
```

**Item**:
```javascript
{
  id: string,        // UUID
  categoryId: string,
  name: string,
  checked: boolean,      // Only in pack lists
  addedToList: boolean   // Only in pack lists, true if not from template
}
```

## Test Requirements (TDD)

Write tests BEFORE implementation:

### packTemplates.test.js
- `addPackTemplate` creates template with correct structure
- `getUserPackTemplates` returns only current user's templates
- `updatePackTemplate` updates fields and sets `updatedAt`
- `deletePackTemplate` removes template
- `addItemToTemplate` adds item to correct category

### packLists.test.js
- `createPackListFromTemplate` copies all categories and items
- `createPackListFromTemplate` sets `templateId` reference
- `createPackListFromTemplate` initializes all items as unchecked
- `toggleItemChecked` updates single item's checked state
- `addItemToList` adds item with `addedToList: true`
- `archivePackList` sets status to "archived"
- `promoteItemToTemplate` copies item to template

## Implementation Notes

- Use existing Firebase abstraction from `src/lib/firebase.js`
- Follow exact pattern from `src/lib/firestore/tyres.js`
- Generate UUIDs for categories and items (use `crypto.randomUUID()`)
- User scoping: always filter by `auth.currentUser.uid`

## Files to Create

```
src/lib/firestore/packTemplates.js
src/lib/firestore/packLists.js
src/lib/firestore/__tests__/packTemplates.test.js  (if test dir exists)
src/lib/firestore/__tests__/packLists.test.js      (if test dir exists)
```

## Estimated Effort

3-4 hours (including TDD test writing)
