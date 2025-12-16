# ADR 002: Pack List Data Model and Repository Layer

**Status**: Accepted
**Date**: 2025-12-15
**Task**: TASK-PL-001

## Context

KartLog needs a pack list feature to help users manage equipment and supplies for race meetings. Users should be able to create reusable templates and generate specific pack lists for individual meetings.

## Decision

We implement a **copy-on-create** pattern with two Firestore collections:

### Collections

1. **packTemplates** - Reusable templates
2. **packLists** - Meeting-specific lists created from templates

### Data Structures

**Pack Template**:
```javascript
{
  id: string,              // Firestore document ID
  userId: string,          // User scope
  name: string,            // "Race Day Essentials"
  description: string,     // "Items for race weekends"
  categories: [            // Nested array
    {
      id: string,          // UUID (crypto.randomUUID())
      name: string,        // "Garage", "Welfare"
      order: number        // Sort order
    }
  ],
  items: [                 // Nested array
    {
      id: string,          // UUID
      categoryId: string,  // References category.id
      name: string         // "Toolbox", "First Aid Kit"
    }
  ],
  createdAt: Date,
  updatedAt: Date
}
```

**Pack List**:
```javascript
{
  id: string,              // Firestore document ID
  userId: string,          // User scope
  templateId: string,      // Reference to source template
  meetingName: string,     // "Silverstone GP"
  meetingDate: Date,       // Meeting date
  status: string,          // "active" | "archived"
  categories: [...],       // Copied from template
  items: [                 // Copied from template
    {
      id: string,
      categoryId: string,
      name: string,
      checked: boolean,         // Pack list only
      addedToList: boolean      // true if user-added (not from template)
    }
  ],
  createdAt: Date,
  updatedAt: Date
}
```

### Repository Pattern

Following existing kartlog patterns (tyres.js):

**packTemplates.js**:
- `addPackTemplate(name, description, categories, items)`
- `getUserPackTemplates()`
- `getPackTemplate(templateId)`
- `updatePackTemplate(templateId, data)`
- `deletePackTemplate(templateId)`
- `addCategoryToTemplate(templateId, category)`
- `addItemToTemplate(templateId, item)`
- `removeItemFromTemplate(templateId, itemId)`

**packLists.js**:
- `createPackListFromTemplate(templateId, meetingName, meetingDate)`
- `getUserPackLists(status = null)`
- `getPackList(listId)`
- `updatePackList(listId, data)`
- `deletePackList(listId)`
- `toggleItemChecked(listId, itemId)`
- `addItemToList(listId, item)`
- `removeItemFromList(listId, itemId)`
- `archivePackList(listId)`
- `promoteItemToTemplate(listId, itemId, templateId)`

## Rationale

### Copy-on-Create vs. Reference

**Decision**: Copy template data to pack lists (denormalization)

**Pros**:
- Pack lists remain valid if template is modified/deleted
- Faster reads (no joins needed)
- Users can customize individual lists without affecting templates
- Simpler query patterns

**Cons**:
- Data duplication
- Larger storage footprint

**Alternative Considered**: Reference-based (normalized)
- Would require complex joins
- Template changes would affect all lists
- Not suitable for "snapshots" of specific meetings

### UUIDs for Categories/Items

**Decision**: Use `crypto.randomUUID()` for nested array elements

**Rationale**:
- Enables immutable array operations (filter by id)
- Client-side generation (no Firestore auto-ID)
- Simplifies item tracking across template/list copies

### User Scoping

All operations enforce `userId` filtering:
- Auth check on every operation
- Firestore Security Rules will enforce this server-side
- Prevents cross-user data access

### Immutable Array Operations

All item updates use immutable patterns:
```javascript
// ✅ Correct
const updated = items.map(item =>
  item.id === targetId ? { ...item, checked: !item.checked } : item
);

// ❌ Wrong
items.find(item => item.id === targetId).checked = true;
```

## Consequences

### Positive

- Clean separation between templates and lists
- Users can experiment with lists without affecting templates
- Historical lists remain accurate snapshots
- Simple, predictable data model

### Negative

- Storage overhead from data duplication
- Need to manage consistency when promoting items back to templates

### Future Considerations

- Consider template versioning if needed
- May add batch operations for multiple items
- Could add template sharing between users
- May add import/export for templates

## Implementation Notes

- TDD approach used (tests written first)
- 49 unit tests covering all CRUD operations
- Mock Firebase implementation for testing
- All tests passing ✅

## References

- [Firebase Repository Pattern](../patterns/repository-firestore.md)
- [Mock Firebase Abstraction](../patterns/mock-firebase.md)
- Existing implementation: `src/lib/firestore/tyres.js`
