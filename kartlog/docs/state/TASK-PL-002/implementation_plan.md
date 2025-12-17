# Implementation Plan: TASK-PL-002

**Task**: Build master template management UI
**Stack**: kartlog (Svelte + SvelteKit + SMUI + Firebase)
**Complexity**: 5/10
**Testing Mode**: TDD
**Generated**: 2025-12-16

## Architecture Overview

**Pattern**: Page-based SPA routing with repository integration
**Testing**: Vitest + TDD (tests written first)
**State**: Svelte stores (global) + component props (local)
**Components**: SMUI Material Design throughout

## Component Architecture

### Route Structure
```
/templates                → PackTemplates.svelte (list view)
/templates/new           → NewPackTemplate.svelte (create)
/templates/:id/edit      → EditPackTemplate.svelte (update)
```

## Files to Create

### Implementation Files (7 files)
1. `src/routes/PackTemplates.svelte` - List all templates (DataTable)
2. `src/routes/NewPackTemplate.svelte` - Create template form
3. `src/routes/EditPackTemplate.svelte` - Edit template form
4. `src/routes/pack-templates.css` - Shared responsive styles
5. `src/lib/stores.js` - Global state (if not exists)
6. `src/lib/schemas/packTemplate.js` - Validation schema (DRY)
7. `src/lib/components/pack-templates/PackTemplateEditor.svelte` - Shared form component

### Test Files (6 files - TDD)
1. `src/routes/__tests__/PackTemplates.test.js`
2. `src/routes/__tests__/NewPackTemplate.test.js`
3. `src/routes/__tests__/EditPackTemplate.test.js`
4. `src/lib/components/pack-templates/__tests__/PackTemplateEditor.test.js`
5. `src/lib/components/pack-templates/__tests__/CategoryManager.test.js`
6. `src/lib/components/pack-templates/__tests__/ItemManager.test.js`

**Total Files**: 13 files

## External Dependencies

Dependencies already in project (from package.json):
- `svelte` - Component framework
- `svelte-spa-router` - Routing
- `smui` - Material Design components
- `firebase` - Backend services
- `vitest` - Testing framework
- `@testing-library/svelte` - Component testing

**No new dependencies required** ✅

## Key Technical Decisions

### 1. Component Architecture
- **Decision**: Separate route pages under `/templates/*`
- **Rationale**: SvelteKit conventions, better SEO, easier testing (TDD)

### 2. State Management
- **Decision**: Svelte stores (global user/auth) + props (local form data)
- **Rationale**: Balances reactivity with simplicity, makes testing easier

### 3. TDD Test Coverage
- **Decision**: Component + Integration tests
- **Rationale**: Appropriate for complexity 5, focus on behavior and API integration

### 4. Category/Item Management UI
- **Decision**: Mixed inline/dialog editing
- **Rationale**: Mobile-friendly, reduces cognitive load

### 5. Firebase Integration
- **Decision**: Repository pattern (from TASK-PL-001)
- **Rationale**: Consistency with existing codebase, 49 passing tests

### 6. Reordering Pattern
- **Decision**: Up/down buttons (NOT drag-and-drop)
- **Rationale**: Mobile-friendly, more reliable on touch, easier to test

### 7. Validation Strategy
- **Decision**: Client-side (reactive) + Server-side (Firebase rules)
- **Rationale**: Immediate feedback + security enforcement

## Implementation Phases

### Phase 1: Setup & Shared Components (45 min)
- Create validation schema (`lib/schemas/packTemplate.js`)
- Create shared form component (`lib/components/pack-templates/PackTemplateEditor.svelte`)
- Extract category/item managers
- Configure Vitest environment
- Write test fixtures

### Phase 2: PackTemplates.svelte (List View - 60 min)
- **TDD**: Write tests first (loading, empty, data, delete)
- Implement DataTable with SMUI components
- Add responsive styles (mobile/tablet/desktop breakpoints)
- Wire up repository layer (getUserPackTemplates, deletePackTemplate)
- Add navigation to create/edit routes

### Phase 3: NewPackTemplate.svelte (Create - 75 min)
- **TDD**: Write tests (validation, category/item CRUD, submission)
- Implement form using shared PackTemplateEditor
- Category management (add, rename, reorder, delete)
- Item management (add, edit, delete)
- Form submission + navigation
- Client-side validation

### Phase 4: EditPackTemplate.svelte (Edit - 45 min)
- **TDD**: Write tests (load, update, error states)
- Implement data loading (onMount)
- Reuse PackTemplateEditor (DRY)
- Update instead of create on submit
- Add statistics display

### Phase 5: Integration & Testing (30 min)
- Update App.svelte routes
- Update Navigation.svelte (add Templates link)
- End-to-end flow testing
- Mobile responsive testing (real devices)
- Cross-browser validation

## Risks & Mitigations

### Risk 1: Complex nested state management
**Impact**: Medium
**Mitigation**: Use immutable array operations, test state updates thoroughly

### Risk 2: Mobile UX issues
**Impact**: Low
**Mitigation**: Mobile-first CSS, test on real devices, up/down buttons

### Risk 3: Form duplication between New/Edit
**Impact**: Medium (addressed by architectural review)
**Mitigation**: Extract shared PackTemplateEditor component

## Success Metrics

- ✅ All components render without errors
- ✅ 100% test coverage (component + integration)
- ✅ Mobile responsive (tested <480px, 640px, 768px)
- ✅ TDD approach (tests written first)
- ✅ Consistent SMUI usage
- ✅ Repository pattern integration working
- ✅ Form validation (client + server)

## Estimated Effort

**Total**: 3.5-4 hours (with architectural recommendations applied)

Breakdown:
- Phase 1 (Setup): 45 min
- Phase 2 (List): 60 min
- Phase 3 (Create): 75 min
- Phase 4 (Edit): 45 min
- Phase 5 (Integration): 30 min

**Lines of Code**: ~450 lines (excluding tests)

## Architectural Review Results

**Score**: 73/100 (Approved with recommendations)
- SOLID: 38/50
- DRY: 18/25
- YAGNI: 17/25

**Key Recommendations Incorporated**:
1. ✅ Shared PackTemplateEditor component (eliminates form duplication)
2. ✅ Validation schema module (DRY compliance)
3. ✅ Component breakdown (CategoryManager, ItemManager)

## Dependencies on Other Tasks

**Requires**:
- TASK-PL-001: Pack list repository layer ✅ (Completed - 49 passing tests)

**Blocks**:
- TASK-PL-004: Actual pack list creation from templates
