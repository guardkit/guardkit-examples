---
id: TASK-PL-E2E-001
title: Add Playwright E2E tests for pack template interactive workflows
status: pending
created: 2025-12-17T00:00:00Z
updated: 2025-12-17T00:00:00Z
priority: medium
tags: [pack-list, e2e, testing, playwright, templates]
complexity: 3
parent_feature: pack-list-feature
wave: 2
execution_mode: task-work
testing_mode: tdd
dependencies: [TASK-PL-002]
blocks: []
---

# Add Playwright E2E Tests for Pack Template Interactive Workflows

## Description

Create Playwright E2E tests to cover interactive workflows in the pack template management UI that cannot be tested with unit tests due to SMUI+Svelte 5+jsdom incompatibility.

## Background

During TASK-PL-002 implementation, we discovered that SMUI components with conditional rendering do not properly update the DOM in jsdom test environment. After evaluation, we accepted partial unit test coverage (35 passing static/rendering tests) and deferred interactive workflow testing to E2E tests.

**Reference**: See TASK-PL-002 blocked issue analysis for technical details.

## Acceptance Criteria

### Category Management Workflows
- [ ] Add new category workflow
  - Click "Add Category" button
  - Enter category name
  - Submit and verify category appears in list
  - Verify empty state message disappears

- [ ] Edit category workflow
  - Click edit button on existing category
  - Modify category name
  - Submit and verify updated name
  - Cancel edit and verify no changes

- [ ] Delete category workflow
  - Click delete button
  - Verify confirmation dialog appears
  - Confirm deletion and verify category removed
  - Cancel deletion and verify category remains

- [ ] Reorder categories workflow
  - Click "Move Up" button
  - Verify category moves up in list
  - Click "Move Down" button
  - Verify category moves down in list
  - Verify first item cannot move up
  - Verify last item cannot move down

### Item Management Workflows
- [ ] Add new item workflow
  - Select category
  - Click "Add Item" button
  - Enter item name
  - Submit and verify item appears under correct category

- [ ] Edit item workflow
  - Click edit button on existing item
  - Modify item name
  - Submit and verify updated name
  - Cancel edit and verify no changes

- [ ] Delete item workflow
  - Click delete button on item
  - Verify confirmation dialog appears
  - Confirm deletion and verify item removed
  - Cancel deletion and verify item remains

### Template Form Workflows
- [ ] Create template workflow
  - Navigate to /templates/new
  - Enter template name (required field)
  - Enter description (optional)
  - Add categories and items
  - Submit form
  - Verify redirect to template list
  - Verify new template appears in list

- [ ] Edit template workflow
  - Navigate to /templates/:id/edit
  - Verify existing data loads
  - Modify template details
  - Submit form
  - Verify changes saved

- [ ] Validation error messages
  - Submit empty template name
  - Verify error message appears
  - Submit duplicate category name
  - Verify error message appears

### List View Workflows
- [ ] Templates list displays correctly
  - Verify template name, category count, item count
  - Verify "Last updated" date

- [ ] Navigation workflows
  - Click template name to edit
  - Click "New Template" button to create
  - Click delete button with confirmation

## Technical Specification

### Test File Structure
```
tests/e2e/pack-templates/
  ├── category-management.spec.js
  ├── item-management.spec.js
  ├── template-crud.spec.js
  └── validation.spec.js
```

### Test Environment Setup
- Use Playwright with Firebase Test Database
- Seed test data before each test suite
- Clean up test data after each test
- Use data-testid attributes for element selection

### Example Test Pattern
```javascript
import { test, expect } from '@playwright/test';

test.describe('Category Management', () => {
  test.beforeEach(async ({ page }) => {
    // Seed test user and navigate to templates
    await page.goto('/templates/new');
  });

  test('should add new category', async ({ page }) => {
    await page.click('[data-testid="add-category-button"]');
    await page.fill('[data-testid="category-add-input"]', 'Camping Gear');
    await page.click('[data-testid="category-add-submit"]');

    await expect(page.locator('text=Camping Gear')).toBeVisible();
    await expect(page.locator('text=No categories yet')).not.toBeVisible();
  });

  test('should edit category name', async ({ page }) => {
    // First add a category
    await page.click('[data-testid="add-category-button"]');
    await page.fill('[data-testid="category-add-input"]', 'Food');
    await page.click('[data-testid="category-add-submit"]');

    // Then edit it
    await page.click('[data-testid="category-edit-button-0"]');
    await page.fill('[data-testid="category-edit-input-0"]', 'Food & Snacks');
    await page.click('[data-testid="category-edit-submit-0"]');

    await expect(page.locator('text=Food & Snacks')).toBeVisible();
    await expect(page.locator('text=Food')).not.toBeVisible();
  });
});
```

## Test Data Requirements

### Fixtures
- Test user account (authenticated)
- Sample templates with various category/item structures
- Empty template (for testing add workflows)
- Template with max categories (for testing limits)

### Cleanup Strategy
- Delete all test data after each test run
- Use unique template names with timestamps to avoid conflicts

## Success Metrics

- ✅ All interactive workflows covered (15+ test scenarios)
- ✅ Tests run in CI/CD pipeline
- ✅ Tests pass on Chromium, Firefox, WebKit
- ✅ Average test execution time < 5 minutes
- ✅ No flaky tests (100% pass rate on 3 consecutive runs)

## Estimated Effort

**Total**: 3-4 hours

Breakdown:
- Setup Playwright config + Firebase test DB: 1 hour
- Write category management tests: 1 hour
- Write item management tests: 45 min
- Write template CRUD tests: 45 min
- Write validation tests: 30 min
- CI/CD integration: 30 min

## Dependencies on Other Tasks

**Requires**:
- TASK-PL-002: Template management UI ✅ (implementation complete)

**Blocks**: None

## Notes

- This task complements TASK-PL-002 by providing E2E coverage for interactive workflows that couldn't be unit tested
- Unit tests in TASK-PL-002 cover static rendering, accessibility, and prop handling (35 tests)
- E2E tests in this task cover user interactions and state changes
- Together, these provide comprehensive test coverage for the pack template feature

## References

- TASK-PL-002 blocked issue analysis: `/kartlog/tasks/blocked/TASK-PL-002-template-management-ui.md`
- SMUI+Svelte 5+jsdom incompatibility: See TASK-PL-002 lines 154-178
- Existing component patterns: `src/routes/Tyres.svelte`, `src/routes/NewTyre.svelte`
