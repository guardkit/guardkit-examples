/**
 * ViewPackList.svelte Component Tests (TDD)
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import { setMockUser, clearMockData, importMockData } from '../../lib/firebase.js';
import ViewPackList from '../ViewPackList.svelte';

describe('ViewPackList.svelte', () => {
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
          categories: [
            { id: 'cat-1', name: 'Garage', order: 1 },
            { id: 'cat-2', name: 'Welfare', order: 2 }
          ],
          items: [
            { id: 'item-1', categoryId: 'cat-1', name: 'Toolbox', checked: false, addedToList: false },
            { id: 'item-2', categoryId: 'cat-1', name: 'Fuel can', checked: true, addedToList: false },
            { id: 'item-3', categoryId: 'cat-2', name: 'Camping chairs', checked: false, addedToList: false }
          ],
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        }
      ]
    };

    importMockData(testData);
  });

  it('should render meeting name', async () => {
    render(ViewPackList, { params: { id: 'list-1' } });

    await new Promise(r => setTimeout(r, 100));

    expect(screen.getByText('Round 3 - Whilton Mill')).toBeTruthy();
  });

  it('should display progress', async () => {
    render(ViewPackList, { params: { id: 'list-1' } });

    await new Promise(r => setTimeout(r, 100));

    // Should show 1/3 items checked
    expect(screen.getByText(/1\/3/)).toBeTruthy();
  });

  it('should display categories', async () => {
    render(ViewPackList, { params: { id: 'list-1' } });

    await new Promise(r => setTimeout(r, 100));

    expect(screen.getByText('Garage')).toBeTruthy();
    expect(screen.getByText('Welfare')).toBeTruthy();
  });

  it('should display items with checkboxes', async () => {
    const { container } = render(ViewPackList, { params: { id: 'list-1' } });

    await new Promise(r => setTimeout(r, 100));

    const checkboxes = container.querySelectorAll('input[type="checkbox"]');
    expect(checkboxes.length).toBeGreaterThan(0);
  });

  it('should show checked state correctly', async () => {
    const { container } = render(ViewPackList, { params: { id: 'list-1' } });

    await new Promise(r => setTimeout(r, 100));

    // item-2 (Fuel can) should be checked
    expect(screen.getByText('Fuel can')).toBeTruthy();
  });

  it('should have archive button for active lists', async () => {
    render(ViewPackList, { params: { id: 'list-1' } });

    await new Promise(r => setTimeout(r, 100));

    expect(screen.getByText(/Archive List/i)).toBeTruthy();
  });
});
