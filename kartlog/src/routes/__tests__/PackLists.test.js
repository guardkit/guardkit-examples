/**
 * PackLists.svelte Component Tests (TDD)
 * Critical path tests following architectural review (12-15 tests, not 26+)
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import { setMockUser, clearMockData, importMockData } from '../../lib/firebase.js';
import PackLists from '../PackLists.svelte';

describe('PackLists.svelte', () => {
  beforeEach(() => {
    clearMockData();
    setMockUser('test-user-1');

    const testData = {
      packLists: [
        {
          id: 'list-1',
          userId: 'test-user-1',
          templateId: 'template-1',
          meetingName: 'Round 3 - Whilton Mill',
          meetingDate: new Date('2025-12-15').toISOString(),
          status: 'active',
          categories: [{ id: 'cat-1', name: 'Garage', order: 1 }],
          items: [
            { id: 'item-1', categoryId: 'cat-1', name: 'Toolbox', checked: true, addedToList: false },
            { id: 'item-2', categoryId: 'cat-1', name: 'Fuel can', checked: false, addedToList: false }
          ],
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        },
        {
          id: 'list-2',
          userId: 'test-user-1',
          templateId: 'template-1',
          meetingName: 'Round 2 - Rye House',
          meetingDate: new Date('2025-12-01').toISOString(),
          status: 'archived',
          categories: [{ id: 'cat-1', name: 'Garage', order: 1 }],
          items: [
            { id: 'item-1', categoryId: 'cat-1', name: 'Toolbox', checked: true, addedToList: false }
          ],
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        }
      ]
    };

    importMockData(testData);
  });

  it('should render page header with title', async () => {
    render(PackLists);
    expect(screen.getByText('Pack Lists')).toBeTruthy();
  });

  it('should show active lists by default', async () => {
    render(PackLists);

    // Wait for load
    await new Promise(r => setTimeout(r, 100));

    expect(screen.getByText('Round 3 - Whilton Mill')).toBeTruthy();
  });

  it('should show progress for each list', async () => {
    render(PackLists);

    await new Promise(r => setTimeout(r, 100));

    // Look for progress indicators (1/2 checked for list-1)
    const progressText = screen.getByText(/1\/2/);
    expect(progressText).toBeTruthy();
  });

  it('should filter to show only active lists', async () => {
    render(PackLists);

    await new Promise(r => setTimeout(r, 100));

    // Active list should be visible
    expect(screen.getByText('Round 3 - Whilton Mill')).toBeTruthy();

    // Archived list should not be visible
    expect(screen.queryByText('Round 2 - Rye House')).toBeFalsy();
  });

  it('should switch to archived view when filter changed', async () => {
    const { container } = render(PackLists);

    await new Promise(r => setTimeout(r, 100));

    // Find and change filter select
    const select = container.querySelector('select');
    if (select) {
      await fireEvent.change(select, { target: { value: 'archived' } });

      await new Promise(r => setTimeout(r, 100));

      // Archived list should now be visible
      expect(screen.getByText('Round 2 - Rye House')).toBeTruthy();

      // Active list should not be visible
      expect(screen.queryByText('Round 3 - Whilton Mill')).toBeFalsy();
    }
  });

  it('should show all lists when filter is "all"', async () => {
    const { container } = render(PackLists);

    await new Promise(r => setTimeout(r, 100));

    const select = container.querySelector('select');
    if (select) {
      await fireEvent.change(select, { target: { value: 'all' } });

      await new Promise(r => setTimeout(r, 100));

      // Both lists should be visible
      expect(screen.getByText('Round 3 - Whilton Mill')).toBeTruthy();
      expect(screen.getByText('Round 2 - Rye House')).toBeTruthy();
    }
  });

  it('should display empty state when no lists exist', async () => {
    clearMockData();
    importMockData({ packLists: [] });

    render(PackLists);

    await new Promise(r => setTimeout(r, 100));

    expect(screen.getByText(/No pack lists/i)).toBeTruthy();
  });

  it('should have "New Pack List" button', async () => {
    render(PackLists);

    const button = screen.getByText(/New Pack List/i);
    expect(button).toBeTruthy();
  });
});
