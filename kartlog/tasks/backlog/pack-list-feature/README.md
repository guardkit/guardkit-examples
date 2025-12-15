# Pack List Feature for Race Meetings

## Problem Statement

Kart racers need to manage equipment and supplies for race meetings. Currently there's no way to:
- Maintain a master checklist of items to pack
- Organize items by category (garage, welfare, shopping)
- Create meeting-specific lists derived from a template
- Track what was packed for historical meetings
- Learn from past meetings by promoting items to the master template

## Solution Approach

**Selected: Hybrid Copy-on-Create with Template References**

This approach creates independent meeting lists from master templates:
- Master templates define reusable pack lists with categories and items
- Meeting lists are created by copying from a template
- Meeting lists can be customized (add/remove items) without affecting the master
- Historical lists are preserved for reference
- Items can be promoted from meeting lists back to the master template

### Why This Approach

1. **Matches User Mental Model**: "Create from template, customize, keep history"
2. **Aligns with Existing Patterns**: Follows kartlog's repository pattern
3. **Simple Implementation**: No complex merge logic or live references
4. **History Preservation**: Archived lists remain unchanged

## Data Model

### Pack Templates Collection
```javascript
{
  id: string,
  userId: string,
  name: string,                    // "Standard Race Weekend"
  description: string,
  categories: [
    { id: "cat-1", name: "Garage", order: 0 },
    { id: "cat-2", name: "Welfare", order: 1 }
  ],
  items: [
    { id: "item-1", categoryId: "cat-1", name: "Toolbox" },
    { id: "item-2", categoryId: "cat-2", name: "Camping chairs" }
  ],
  createdAt: Date,
  updatedAt: Date
}
```

### Pack Lists Collection (Meeting-Specific)
```javascript
{
  id: string,
  userId: string,
  templateId: string,              // Reference to source template
  meetingName: string,             // "Round 3 - Whilton Mill"
  meetingDate: Date,
  categories: [...],               // Copied from template
  items: [
    { id: "item-1", categoryId: "cat-1", name: "Toolbox", checked: true },
    { id: "item-4", categoryId: "cat-1", name: "Extra fuel", checked: false, addedToList: true }
  ],
  status: "active" | "archived",
  createdAt: Date,
  updatedAt: Date
}
```

## Subtasks

| ID | Title | Complexity | Mode | Wave |
|----|-------|------------|------|------|
| TASK-PL-001 | Create data model and repository layer | 6/10 | task-work | 1 |
| TASK-PL-002 | Build master template management UI | 5/10 | task-work | 2 |
| TASK-PL-003 | Build meeting pack list UI | 5/10 | task-work | 2 |
| TASK-PL-004 | Implement item promotion and history features | 4/10 | task-work | 3 |
| TASK-PL-005 | Add navigation and integration | 3/10 | direct | 3 |

## Execution Strategy

### Wave 1 (Sequential - Foundation)
- TASK-PL-001: Repository layer must complete first

### Wave 2 (Parallel - UI Components)
- TASK-PL-002 and TASK-PL-003 can run in parallel
- Both depend on Wave 1 completion

### Wave 3 (Parallel - Features & Integration)
- TASK-PL-004 and TASK-PL-005 can run in parallel
- Both depend on Wave 2 completion

## Estimated Effort

- **Total**: 12-17 hours
- **Testing**: Full TDD approach (test-first)

## Review Source

- Review Task: TASK-REV-47E0
- Review Date: 2025-12-15
- Decision: Implement Option 1 (Hybrid Copy-on-Create)
