<script>
  import { createEventDispatcher } from 'svelte';
  import Card from '@smui/card';
  import Checkbox from '@smui/checkbox';
  import FormField from '@smui/form-field';
  import IconButton from '@smui/icon-button';
  import Textfield from '@smui/textfield';
  import Button from '@smui/button';

  export let category;
  export let items = [];

  const dispatch = createEventDispatcher();

  let collapsed = false;
  let addingItem = false;
  let newItemName = '';

  $: checkedCount = items.filter(item => item.checked).length;
  $: totalCount = items.length;

  const toggleCollapse = () => {
    collapsed = !collapsed;
  };

  const handleToggle = (itemId) => {
    dispatch('toggleItem', itemId);
  };

  const handleAddItem = () => {
    if (newItemName.trim()) {
      dispatch('addItem', newItemName.trim());
      newItemName = '';
      addingItem = false;
    }
  };

  const handleRemoveItem = (itemId) => {
    dispatch('removeItem', itemId);
  };

  const startAdding = () => {
    addingItem = true;
  };

  const cancelAdding = () => {
    addingItem = false;
    newItemName = '';
  };
</script>

<Card class="category-section">
  <div class="category-header" on:click={toggleCollapse} role="button" tabindex="0">
    <div class="category-title">
      <span class="collapse-icon">{collapsed ? '▶' : '▼'}</span>
      <h3>{category.name}</h3>
      <span class="category-count">({checkedCount}/{totalCount})</span>
    </div>
  </div>

  {#if !collapsed}
    <div class="category-content">
      <div class="items-list">
        {#each items as item (item.id)}
          <div class="item-row" class:checked={item.checked}>
            <FormField>
              <Checkbox
                checked={item.checked}
                on:click={() => handleToggle(item.id)}
              />
              <span slot="label" class="item-name" class:added={item.addedToList}>
                {item.name}
                {#if item.addedToList}
                  <span class="added-badge">added</span>
                {/if}
              </span>
            </FormField>

            {#if item.addedToList}
              <IconButton
                class="delete"
                on:click={() => handleRemoveItem(item.id)}
                title="Remove item"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
              </IconButton>
            {/if}
          </div>
        {/each}
      </div>

      {#if addingItem}
        <div class="add-item-form">
          <Textfield
            bind:value={newItemName}
            label="Item name"
            style="flex: 1;"
            on:keydown={(e) => e.key === 'Enter' && handleAddItem()}
          />
          <Button on:click={handleAddItem} variant="raised" style="background-color: #007bff;">
            Add
          </Button>
          <Button on:click={cancelAdding} variant="outlined">
            Cancel
          </Button>
        </div>
      {:else}
        <Button on:click={startAdding} variant="outlined" style="width: 100%; margin-top: 0.5rem;">
          + Add Item to {category.name}
        </Button>
      {/if}
    </div>
  {/if}
</Card>

<style>
  :global(.category-section) {
    margin-bottom: 1rem;
  }

  .category-header {
    padding: 1rem 1.5rem;
    cursor: pointer;
    user-select: none;
    border-bottom: 1px solid #e0e0e0;
  }

  .category-header:hover {
    background-color: #f5f5f5;
  }

  .category-title {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .collapse-icon {
    color: #666;
    font-size: 0.9rem;
  }

  .category-title h3 {
    margin: 0;
    font-size: 1.1rem;
    color: #333;
    flex: 1;
  }

  .category-count {
    color: #666;
    font-size: 0.9rem;
    font-weight: 500;
  }

  .category-content {
    padding: 1rem 1.5rem;
  }

  .items-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .item-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.5rem;
    border-radius: 4px;
    transition: background-color 0.2s;
  }

  .item-row:hover {
    background-color: #f8f9fa;
  }

  .item-row.checked {
    opacity: 0.6;
  }

  .item-name {
    font-size: 1rem;
    color: #333;
  }

  .item-name.added {
    font-style: italic;
  }

  .added-badge {
    display: inline-block;
    margin-left: 0.5rem;
    padding: 0.1rem 0.4rem;
    background-color: #e3f2fd;
    color: #1976d2;
    font-size: 0.7rem;
    font-weight: 600;
    border-radius: 8px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .add-item-form {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #e0e0e0;
  }

  @media (max-width: 768px) {
    .category-header {
      padding: 0.75rem 1rem;
    }

    .category-content {
      padding: 0.75rem 1rem;
    }

    .add-item-form {
      flex-direction: column;
      align-items: stretch;
    }
  }
</style>
