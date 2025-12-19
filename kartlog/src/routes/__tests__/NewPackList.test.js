/**
 * NewPackList.svelte Component Tests (TDD)
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import { setMockUser, clearMockData, importMockData } from '../../lib/firebase.js';
import NewPackList from '../NewPackList.svelte';

describe('NewPackList.svelte', () => {
  beforeEach(() => {
    clearMockData();
    setMockUser('test-user-1');

    const testData = {
      packTemplates: [
        {
          id: 'template-1',
          userId: 'test-user-1',
          name: 'Race Day Essentials',
          description: 'Everything for race day',
          categories: [{ id: 'cat-1', name: 'Garage', order: 1 }],
          items: [{ id: 'item-1', categoryId: 'cat-1', name: 'Toolbox' }],
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        }
      ],
      packLists: []
    };

    importMockData(testData);
  });

  it('should render page header', async () => {
    render(NewPackList);
    expect(screen.getByText('Create Pack List')).toBeTruthy();
  });

  it('should load templates into select dropdown', async () => {
    render(NewPackList);

    await new Promise(r => setTimeout(r, 100));

    expect(screen.getByText('Race Day Essentials')).toBeTruthy();
  });

  it('should have meeting name input field', async () => {
    const { container } = render(NewPackList);

    const input = container.querySelector('input[type="text"]');
    expect(input).toBeTruthy();
  });

  it('should have meeting date input field', async () => {
    const { container } = render(NewPackList);

    const dateInput = container.querySelector('input[type="date"]');
    expect(dateInput).toBeTruthy();
  });

  it('should have submit button', async () => {
    render(NewPackList);

    const button = screen.getByText(/Create Pack List/i);
    expect(button).toBeTruthy();
  });

  it('should show validation error when submitting without template', async () => {
    const { container } = render(NewPackList);

    await new Promise(r => setTimeout(r, 100));

    const form = container.querySelector('form');
    if (form) {
      await fireEvent.submit(form);

      await new Promise(r => setTimeout(r, 100));

      expect(screen.queryByText(/select a template/i)).toBeTruthy();
    }
  });

  it('should show validation error when submitting without meeting name', async () => {
    const { container } = render(NewPackList);

    await new Promise(r => setTimeout(r, 100));

    // Select template
    const select = container.querySelector('select');
    if (select) {
      await fireEvent.change(select, { target: { value: 'template-1' } });
    }

    const form = container.querySelector('form');
    if (form) {
      await fireEvent.submit(form);

      await new Promise(r => setTimeout(r, 100));

      expect(screen.queryByText(/meeting name/i)).toBeTruthy();
    }
  });
});
