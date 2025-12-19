<script>
  import Button from '@smui/button';
  import Textfield from '@smui/textfield';
  import Select, { Option } from '@smui/select';
  import { validateItem } from '../../schemas/packTemplate.js';

  export let items = [];
  export let categories = [];
  export let onAdd = () => {};
  export let onUpdate = () => {};
  export let onDelete = () => {};
  export let isLoading = false;
  export let errors = {};

  let showAddForm = false;
  let newItemName = '';
  let newItemCategoryId = '';
  let addError = '';
  let editingId = null;
  let editingName = '';
  let editingCategoryId = '';
  let editError = '';

  const handleAddClick = () => {
    showAddForm = true;
    newItemName = '';
    newItemCategoryId = '';
    addError = '';
  };

  const handleAddConfirm = () => {
    addError = '';
    const validation = validateItem({ name: newItemName, categoryId: newItemCategoryId });

    if (validation.name || validation.categoryId) {
      addError = validation.name || validation.categoryId;
      return;
    }

    onAdd({ name: newItemName.trim(), categoryId: newItemCategoryId });
    showAddForm = false;
    newItemName = '';
    newItemCategoryId = '';
  };

  const handleAddCancel = () => {
    showAddForm = false;
    newItemName = '';
    newItemCategoryId = '';
    addError = '';
  };

  const handleEditStart = (item) => {
    editingId = item.id;
    editingName = item.name;
    editingCategoryId = item.categoryId;
    editError = '';
  };

  const handleEditConfirm = () => {
    editError = '';
    const validation = validateItem({ name: editingName, categoryId: editingCategoryId });

    if (validation.name || validation.categoryId) {
      editError = validation.name || validation.categoryId;
      return;
    }

    onUpdate(editingId, { name: editingName.trim(), categoryId: editingCategoryId });
    editingId = null;
  };

  const handleEditCancel = () => {
    editingId = null;
    editError = '';
  };

  const handleDelete = (itemId) => {
    if (confirm('Are you sure you want to delete this item?')) {
      onDelete(itemId);
    }
  };

  const itemsByCategory = categories.map(category => ({
    category,
    items: items.filter(item => item.categoryId === category.id)
  }));
</script>

<div class="item-manager">
  {#if items.length === 0 && !showAddForm}
    <div class="empty-state">
      <p>No items yet. Add one to get started.</p>
    </div>
  {/if}

  <div class="add-form" class:hidden={!showAddForm}>
    {#if addError}
      <div class="error-message" role="alert">{addError}</div>
    {/if}
    <div class="form-grid">
      <Textfield
        variant="outlined"
        bind:value={newItemName}
        label="Item Name"
        placeholder="Enter item name"
        disabled={isLoading}
        error={!!addError}
        aria-label="Item name"
        input$data-testid="item-add-name-input"
      />
      <Select bind:value={newItemCategoryId} label="Category" disabled={isLoading} required aria-label="Item category" data-testid="item-add-category-select">
        <Option value="">Select category</Option>
        {#each categories as category (category.id)}
          <Option value={category.id}>{category.name}</Option>
        {/each}
      </Select>
      <div class="button-group">
        <Button on:click={handleAddConfirm} disabled={isLoading} variant="raised">
          Add
        </Button>
        <Button on:click={handleAddCancel} disabled={isLoading}>
          Cancel
        </Button>
      </div>
    </div>
  </div>

  {#if items.length > 0}
    <div class="items-by-category">
      {#each itemsByCategory as group (group.category.id)}
        <div class="category-group">
          <h4 class="category-header">{group.category.name}</h4>
          {#if group.items.length === 0}
            <div class="category-empty">No items in this category</div>
          {:else}
            <div class="items-list" role="list">
              {#each group.items as item (item.id)}
                <div class="item-row" role="listitem">
                  <div class="edit-form" class:hidden={editingId !== item.id}>
                    {#if editError}
                      <div class="error-message" role="alert">{editError}</div>
                    {/if}
                    <div class="form-grid">
                      <Textfield
                        variant="outlined"
                        bind:value={editingName}
                        placeholder="Enter item name"
                        disabled={isLoading}
                        error={!!editError}
                        aria-label="Item name"
                        input$data-testid="item-edit-name-input"
                      />
                      <Select bind:value={editingCategoryId} disabled={isLoading} required aria-label="Item category" data-testid="item-edit-category-select">
                        <Option value="">Select category</Option>
                        {#each categories as category (category.id)}
                          <Option value={category.id}>{category.name}</Option>
                        {/each}
                      </Select>
                      <div class="button-group">
                        <Button on:click={handleEditConfirm} disabled={isLoading} variant="raised">
                          Save
                        </Button>
                        <Button on:click={handleEditCancel} disabled={isLoading}>
                          Cancel
                        </Button>
                      </div>
                    </div>
                  </div>
                  <div class="item-content" class:hidden={editingId === item.id}>
                    <span class="item-name">• {item.name}</span>
                    <div class="item-actions">
                      <Button
                        on:click={() => handleEditStart(item)}
                        disabled={isLoading}
                        class="text-button"
                        aria-label="Edit {item.name}"
                      >
                        Edit
                      </Button>
                      <Button
                        on:click={() => handleDelete(item.id)}
                        disabled={isLoading}
                        class="text-button delete-button"
                        aria-label="Delete {item.name}"
                      >
                        Delete
                      </Button>
                    </div>
                  </div>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}

  <div class="add-button-container" class:hidden={showAddForm}>
    <Button on:click={handleAddClick} disabled={isLoading} variant="outlined">
      + Add Item
    </Button>
  </div>
</div>

<style>
  .hidden {
    visibility: hidden;
    position: absolute;
  }

  .item-manager {
    margin-top: 1rem;
  }

  .empty-state {
    padding: 2rem;
    text-align: center;
    background-color: #f5f5f5;
    border-radius: 4px;
    color: #666;
  }

  .add-form,
  .edit-form {
    padding: 1rem;
    margin-bottom: 1rem;
    background-color: #f9f9f9;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
  }

  .form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    align-items: flex-start;
  }

  .button-group {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    grid-column: 1 / -1;
  }

  .items-by-category {
    margin: 1rem 0;
  }

  .category-group {
    margin-bottom: 2rem;
  }

  .category-header {
    margin: 0 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #2196f3;
    color: #1976d2;
    font-size: 1rem;
    font-weight: 600;
  }

  .category-empty {
    padding: 1rem;
    color: #999;
    font-style: italic;
  }

  .items-list {
    list-style: none;
    padding: 0;
  }

  .item-row {
    padding: 0.75rem 0;
    border-bottom: 1px solid #f0f0f0;
  }

  .item-row:last-child {
    border-bottom: none;
  }

  .item-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .item-name {
    color: #333;
    font-size: 0.95rem;
  }

  .item-actions {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }

  .text-button {
    padding: 0.25rem 0.75rem;
    font-size: 0.875rem;
  }

  .delete-button {
    color: #dc3545;
  }

  .add-button-container {
    margin-top: 1rem;
  }

  .error-message {
    padding: 0.75rem;
    margin-bottom: 1rem;
    background-color: #ffebee;
    border-left: 3px solid #f44336;
    color: #c62828;
    border-radius: 2px;
    font-size: 0.875rem;
  }

  @media (max-width: 768px) {
    .form-grid {
      grid-template-columns: 1fr;
    }

    .item-content {
      flex-direction: column;
      align-items: flex-start;
      gap: 0.5rem;
    }

    .item-actions {
      width: 100%;
      justify-content: flex-end;
    }
  }
</style>
