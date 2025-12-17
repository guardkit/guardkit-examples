<script>
  import Button from '@smui/button';
  import Textfield from '@smui/textfield';
  import IconButton from '@smui/icon-button';
  import { validateCategory } from '../../schemas/packTemplate.js';

  export let categories = [];
  export let onAdd = () => {};
  export let onUpdate = () => {};
  export let onDelete = () => {};
  export let onReorder = () => {};
  export let isLoading = false;
  export let errors = {};

  let showAddForm = false;
  let newCategoryName = '';
  let addError = '';
  let editingId = null;
  let editingName = '';
  let editError = '';

  const handleAddClick = () => {
    showAddForm = true;
    newCategoryName = '';
    addError = '';
  };

  const handleAddConfirm = () => {
    addError = '';
    const validation = validateCategory({ name: newCategoryName });

    if (validation.name) {
      addError = validation.name;
      return;
    }

    // Check for duplicates
    if (categories.some(cat => cat.name.toLowerCase() === newCategoryName.trim().toLowerCase())) {
      addError = 'Category name already exists';
      return;
    }

    onAdd({ name: newCategoryName.trim() });
    showAddForm = false;
    newCategoryName = '';
  };

  const handleAddCancel = () => {
    showAddForm = false;
    newCategoryName = '';
    addError = '';
  };

  const handleEditStart = (category) => {
    editingId = category.id;
    editingName = category.name;
    editError = '';
  };

  const handleEditConfirm = () => {
    editError = '';
    const validation = validateCategory({ name: editingName });

    if (validation.name) {
      editError = validation.name;
      return;
    }

    // Check for duplicates (excluding self)
    if (categories.some(cat => cat.id !== editingId && cat.name.toLowerCase() === editingName.trim().toLowerCase())) {
      editError = 'Category name already exists';
      return;
    }

    onUpdate(editingId, { name: editingName.trim() });
    editingId = null;
  };

  const handleEditCancel = () => {
    editingId = null;
    editError = '';
  };

  const handleDelete = (categoryId) => {
    if (confirm('Are you sure you want to delete this category and all its items?')) {
      onDelete(categoryId);
    }
  };

  const handleMoveUp = (index) => {
    if (index === 0) return;
    const newCategories = [...categories];
    const [item] = newCategories.splice(index, 1);
    newCategories.splice(index - 1, 0, item);
    newCategories.forEach((cat, i) => {
      cat.order = i;
    });
    onReorder(newCategories);
  };

  const handleMoveDown = (index) => {
    if (index === categories.length - 1) return;
    const newCategories = [...categories];
    const [item] = newCategories.splice(index, 1);
    newCategories.splice(index + 1, 0, item);
    newCategories.forEach((cat, i) => {
      cat.order = i;
    });
    onReorder(newCategories);
  };
</script>

<div class="category-manager">
  {#if categories.length === 0 && !showAddForm}
    <div class="empty-state">
      <p>No categories yet. Add one to get started.</p>
    </div>
  {/if}

  <div class="add-form" class:hidden={!showAddForm}>
    {#if addError}
      <div class="error-message" role="alert">{addError}</div>
    {/if}
    <div class="form-row">
      <Textfield
        variant="outlined"
        bind:value={newCategoryName}
        label="Category Name"
        placeholder="Enter category name"
        disabled={isLoading}
        error={!!addError}
        aria-label="Category name"
        input$data-testid="category-add-input"
      />
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

  {#if categories.length > 0}
    <div class="category-list" role="list">
      {#each categories as category, index (category.id)}
        <div class="category-item" role="listitem">
          <div class="edit-form" class:hidden={editingId !== category.id}>
            {#if editError}
              <div class="error-message" role="alert">{editError}</div>
            {/if}
            <div class="form-row">
              <Textfield
                variant="outlined"
                bind:value={editingName}
                placeholder="Enter category name"
                disabled={isLoading}
                error={!!editError}
                aria-label="Category name"
                input$data-testid="category-edit-input"
              />
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
          <div class="category-content" class:hidden={editingId === category.id}>
            <span class="category-name">{category.name}</span>
            <div class="category-actions">
              <IconButton
                on:click={() => handleMoveUp(index)}
                disabled={isLoading || index === 0}
                title="Move up"
                aria-label="Move {category.name} up"
              >
                ▲
              </IconButton>
              <IconButton
                on:click={() => handleMoveDown(index)}
                disabled={isLoading || index === categories.length - 1}
                title="Move down"
                aria-label="Move {category.name} down"
              >
                ▼
              </IconButton>
              <Button
                on:click={() => handleEditStart(category)}
                disabled={isLoading}
                class="text-button"
                aria-label="Edit {category.name}"
              >
                Edit
              </Button>
              <Button
                on:click={() => handleDelete(category.id)}
                disabled={isLoading}
                class="text-button delete-button"
                aria-label="Delete {category.name}"
              >
                Delete
              </Button>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}

  <div class="add-button-container" class:hidden={showAddForm}>
    <Button on:click={handleAddClick} disabled={isLoading} variant="outlined">
      + Add Category
    </Button>
  </div>
</div>

<style>
  .hidden {
    visibility: hidden;
    position: absolute;
  }

  .category-manager {
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

  .form-row {
    display: flex;
    gap: 1rem;
    align-items: flex-start;
  }

  .button-group {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }

  .category-list {
    list-style: none;
    padding: 0;
    margin: 1rem 0;
  }

  .category-item {
    padding: 1rem;
    margin-bottom: 0.75rem;
    background-color: #fafafa;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    transition: background-color 0.2s;
  }

  .category-item:hover {
    background-color: #f5f5f5;
  }

  .category-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .category-name {
    font-weight: 500;
    color: #333;
  }

  .category-actions {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }

  .delete-button {
    color: #dc3545;
  }

  .text-button {
    padding: 0.25rem 0.75rem;
    font-size: 0.875rem;
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

  @media (max-width: 640px) {
    .form-row {
      flex-direction: column;
    }

    .category-content {
      flex-direction: column;
      align-items: flex-start;
      gap: 0.75rem;
    }

    .category-actions {
      width: 100%;
      flex-wrap: wrap;
    }
  }
</style>
