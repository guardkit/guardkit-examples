<script>
  import { onMount } from 'svelte';
  import { link, push } from 'svelte-spa-router';
  import Button from '@smui/button';
  import CircularProgress from '@smui/circular-progress';
  import Card from '@smui/card';
  import {
    packLists,
    fetchPackLists,
    toggleItemInList,
    addItemToPackList,
    removeItemFromPackList,
    archiveList,
    deletePackList,
    getListProgress
  } from '../lib/stores/packListStore.js';
  import PackListProgress from '../components/PackListProgress.svelte';
  import CategorySection from '../components/CategorySection.svelte';

  export let params = {};

  let list = null;
  let loading = true;
  let error = '';

  $: if ($packLists.length > 0 && params.id) {
    list = $packLists.find(l => l.id === params.id);
  }

  $: progress = list ? getListProgress(list) : { total: 0, checked: 0, percentage: 0 };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };

  const handleToggleItem = async (itemId) => {
    try {
      await toggleItemInList(params.id, itemId);
    } catch (err) {
      error = err.message;
    }
  };

  const handleAddItem = async (categoryId, itemName) => {
    try {
      await addItemToPackList(params.id, { categoryId, name: itemName });
    } catch (err) {
      error = err.message;
    }
  };

  const handleRemoveItem = async (itemId) => {
    if (!confirm('Are you sure you want to remove this item?')) {
      return;
    }

    try {
      await removeItemFromPackList(params.id, itemId);
    } catch (err) {
      error = err.message;
    }
  };

  const handleArchive = async () => {
    if (!confirm('Archive this pack list? You can still view it in the archived section.')) {
      return;
    }

    try {
      await archiveList(params.id);
      push('/pack-lists');
    } catch (err) {
      error = err.message;
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this pack list? This action cannot be undone.')) {
      return;
    }

    try {
      await deletePackList(params.id);
      push('/pack-lists');
    } catch (err) {
      error = err.message;
    }
  };

  onMount(async () => {
    loading = true;
    await fetchPackLists();
    loading = false;
  });
</script>

<div class="view-pack-list-page">
  <div class="header">
    <h1>{list?.meetingName || 'Pack List'}</h1>
    <Button href="/pack-lists" tag="a" use={[link]} variant="outlined">
      ← Back to Pack Lists
    </Button>
  </div>

  {#if error}
    <div class="error">{error}</div>
  {/if}

  {#if loading}
    <div class="loading">
      <CircularProgress style="height: 48px; width: 48px;" indeterminate />
      <p>Loading pack list...</p>
    </div>
  {:else if list}
    <Card style="padding: 2rem; margin-bottom: 2rem;">
      <div class="list-header">
        <div class="meeting-info">
          <h2>{list.meetingName}</h2>
          <p class="meeting-date">{formatDate(list.meetingDate)}</p>
          <span class="status-badge" class:active={list.status === 'active'} class:archived={list.status === 'archived'}>
            {list.status}
          </span>
        </div>

        <PackListProgress {progress} />
      </div>
    </Card>

    <div class="categories">
      {#each list.categories as category (category.id)}
        {@const categoryItems = list.items.filter(item => item.categoryId === category.id)}
        <CategorySection
          {category}
          items={categoryItems}
          on:toggleItem={(e) => handleToggleItem(e.detail)}
          on:addItem={(e) => handleAddItem(category.id, e.detail)}
          on:removeItem={(e) => handleRemoveItem(e.detail)}
        />
      {/each}
    </div>

    <div class="action-buttons">
      {#if list.status === 'active'}
        <Button on:click={handleArchive} variant="outlined">
          Archive List
        </Button>
      {/if}
      <Button on:click={handleDelete} variant="outlined" style="color: #dc3545; border-color: #dc3545;">
        Delete List
      </Button>
    </div>
  {:else}
    <div class="empty-state">
      <h2>Pack List Not Found</h2>
      <p>The pack list you're looking for doesn't exist or you don't have access to it.</p>
      <Button href="/pack-lists" tag="a" use={[link]} variant="outlined">
        Back to Pack Lists
      </Button>
    </div>
  {/if}
</div>

<style>
  .view-pack-list-page {
    padding: 2rem;
    max-width: 900px;
    margin: 0 auto;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }

  .header h1 {
    margin: 0;
    color: #333;
  }

  .loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem;
  }

  .loading p {
    margin-top: 1rem;
    color: #666;
  }

  .error {
    padding: 1rem;
    background-color: #fee;
    border: 1px solid #fcc;
    border-radius: 4px;
    color: #c00;
    margin-bottom: 1rem;
  }

  .list-header {
    margin-bottom: 1.5rem;
  }

  .meeting-info h2 {
    margin: 0 0 0.5rem 0;
    color: #333;
  }

  .meeting-date {
    margin: 0 0 1rem 0;
    color: #666;
    font-size: 1.1rem;
  }

  .status-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .status-badge.active {
    background-color: #e3f2fd;
    color: #1976d2;
  }

  .status-badge.archived {
    background-color: #f5f5f5;
    color: #757575;
  }

  .categories {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    margin-bottom: 2rem;
  }

  .action-buttons {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
    padding: 1.5rem 0;
  }

  .empty-state {
    text-align: center;
    padding: 4rem 2rem;
    background-color: #f8f9fa;
    border-radius: 10px;
  }

  .empty-state h2 {
    color: #666;
    margin-bottom: 1rem;
  }

  .empty-state p {
    color: #888;
    margin-bottom: 2rem;
  }

  @media (max-width: 768px) {
    .view-pack-list-page {
      padding: 1rem;
    }

    .header {
      flex-direction: column;
      gap: 1rem;
      align-items: stretch;
    }

    .action-buttons {
      flex-direction: column;
    }
  }
</style>
