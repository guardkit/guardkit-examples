<script>
  import Card from '@smui/card';
  import Textfield from '@smui/textfield';
  import Button from '@smui/button';
  import { validateCompleteTemplate } from '../../schemas/packTemplate.js';
  import CategoryManager from './CategoryManager.svelte';
  import ItemManager from './ItemManager.svelte';

  export let mode = 'create';
  export let initialData = {
    name: '',
    description: '',
    categories: [],
    items: []
  };
  export let onSubmit = async () => {};
  export let isLoading = false;

  let formData = {
    name: initialData.name,
    description: initialData.description,
    categories: JSON.parse(JSON.stringify(initialData.categories || [])),
    items: JSON.parse(JSON.stringify(initialData.items || []))
  };

  let validationErrors = {};
  let submitError = '';

  const handleAddCategory = (category) => {
    formData.categories = [...formData.categories, { ...category, id: crypto.randomUUID(), order: formData.categories.length }];
  };

  const handleUpdateCategory = (categoryId, data) => {
    formData.categories = formData.categories.map(cat =>
      cat.id === categoryId ? { ...cat, ...data } : cat
    );
  };

  const handleDeleteCategory = (categoryId) => {
    formData.categories = formData.categories.filter(cat => cat.id !== categoryId);
    formData.items = formData.items.filter(item => item.categoryId !== categoryId);
  };

  const handleReorderCategories = (newCategories) => {
    formData.categories = newCategories;
  };

  const handleAddItem = (item) => {
    formData.items = [...formData.items, { ...item, id: crypto.randomUUID() }];
  };

  const handleUpdateItem = (itemId, data) => {
    formData.items = formData.items.map(item =>
      item.id === itemId ? { ...item, ...data } : item
    );
  };

  const handleDeleteItem = (itemId) => {
    formData.items = formData.items.filter(item => item.id !== itemId);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    submitError = '';

    const validation = validateCompleteTemplate(formData);
    validationErrors = validation.errors;

    if (!validation.isValid) {
      return;
    }

    try {
      isLoading = true;
      await onSubmit(formData);
    } catch (err) {
      submitError = err.message;
    } finally {
      isLoading = false;
    }
  };
</script>

<div class="form-page">
  {#if submitError}
    <div class="error-message" role="alert">{submitError}</div>
  {/if}

  {#if Object.keys(validationErrors).length > 0}
    <div class="error-message" role="alert">
      Please fix the validation errors below
    </div>
  {/if}

  <Card style="padding: 2rem;">
    <form on:submit={handleSubmit} role="form">
      <!-- Template Info Section -->
      <div class="form-section">
        <h3>Template Information</h3>

        <div class="form-group">
          <Textfield
            variant="outlined"
            bind:value={formData.name}
            label="Template Name"
            required
            disabled={isLoading}
            style="width: 100%;"
            error={!!validationErrors.template?.name}
            helperText={validationErrors.template?.name}
            aria-label="Template name"
            input$data-testid="template-name-input"
          />
        </div>

        <div class="form-group">
          <Textfield
            variant="outlined"
            bind:value={formData.description}
            label="Description"
            textarea
            disabled={isLoading}
            style="width: 100%;"
            input$rows={4}
            error={!!validationErrors.template?.description}
            helperText={validationErrors.template?.description}
            aria-label="Template description"
            input$data-testid="template-description-input"
          />
        </div>
      </div>

      <!-- Categories Section -->
      <div class="form-section">
        <h3>Categories</h3>
        <CategoryManager
          categories={formData.categories}
          onAdd={handleAddCategory}
          onUpdate={handleUpdateCategory}
          onDelete={handleDeleteCategory}
          onReorder={handleReorderCategories}
          isLoading={isLoading}
          errors={validationErrors.categories}
        />
      </div>

      <!-- Items Section -->
      <div class="form-section">
        <h3>Items</h3>
        <ItemManager
          items={formData.items}
          categories={formData.categories}
          onAdd={handleAddItem}
          onUpdate={handleUpdateItem}
          onDelete={handleDeleteItem}
          isLoading={isLoading}
          errors={validationErrors.items}
        />
      </div>

      <!-- Form Actions -->
      <div class="form-actions">
        <Button type="button" disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" variant="raised" disabled={isLoading}>
          {isLoading ? (mode === 'create' ? 'Creating...' : 'Updating...') : (mode === 'create' ? 'Create Template' : 'Update Template')}
        </Button>
      </div>
    </form>
  </Card>
</div>

<style>
  .hidden {
    visibility: hidden;
    position: absolute;
  }

  .form-page {
    max-width: 900px;
    margin: 2rem auto;
  }

  .form-section {
    margin-bottom: 2rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid #e0e0e0;
  }

  .form-section:last-of-type {
    border-bottom: none;
  }

  .form-section h3 {
    margin-top: 0;
    margin-bottom: 1.5rem;
    color: #333;
    font-size: 1.1rem;
    font-weight: 500;
  }

  .form-group {
    margin-bottom: 1.5rem;
  }

  .form-actions {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid #e0e0e0;
  }

  .error-message {
    padding: 1rem;
    margin-bottom: 1.5rem;
    background-color: #ffebee;
    border-left: 4px solid #f44336;
    color: #c62828;
    border-radius: 4px;
  }

  @media (max-width: 768px) {
    .form-page {
      margin: 1rem;
    }

    .form-section {
      padding-bottom: 1.5rem;
      margin-bottom: 1.5rem;
    }

    .form-actions {
      flex-direction: column-reverse;
    }
  }
</style>
