<script>
  import { onMount } from 'svelte';
  import { link, push } from 'svelte-spa-router';
  import Button from '@smui/button';
  import CircularProgress from '@smui/circular-progress';
  import {
    packLists,
    activePackLists,
    archivedPackLists,
    loadingPackLists,
    errorPackLists,
    fetchPackLists,
    getListProgress
  } from '../lib/stores/packListStore.js';
  import PackListCard from '../components/PackListCard.svelte';

  let filter = 'active'; // 'active' | 'archived' | 'all'

  // Compute filtered lists based on selected filter
  $: filteredLists = filter === 'active'
    ? $activePackLists
    : filter === 'archived'
      ? $archivedPackLists
      : $packLists;

  const handleRowClick = (listId) => {
    push(`/pack-lists/view/${listId}`);
  };

  onMount(() => {
    fetchPackLists();
  });
</script>

<div class="pack-lists-page">
  <div class="page-header">
    <h1>Pack Lists</h1>
    <Button href="/pack-lists/new" tag="a" use={[link]} variant="raised" color="primary">
      + New Pack List
    </Button>
  </div>

  {#if $errorPackLists}
    <div class="error">{$errorPackLists}</div>
  {/if}

  {#if $loadingPackLists}
    <div class="loading">
      <CircularProgress style="height: 48px; width: 48px;" indeterminate />
      <p>Loading pack lists...</p>
    </div>
  {:else if $packLists.length === 0}
    <div class="empty-state">
      <h2>No Pack Lists Yet</h2>
      <p>Create your first pack list from a template to get started!</p>
      <Button href="/pack-lists/new" tag="a" use={[link]} variant="raised" color="primary">
        Create Your First Pack List
      </Button>
    </div>
  {:else}
    <div class="table-toolbar">
      <label for="status-filter">Show:</label>
      <select id="status-filter" bind:value={filter}>
        <option value="active">Active Lists</option>
        <option value="archived">Archived Lists</option>
        <option value="all">All Lists</option>
      </select>
    </div>

    <div class="pack-lists-grid">
      {#each filteredLists as list (list.id)}
        <PackListCard
          {list}
          progress={getListProgress(list)}
          on:click={() => handleRowClick(list.id)}
        />
      {/each}
    </div>

    {#if filteredLists.length === 0}
      <div class="empty-filter-state">
        <p>No {filter} pack lists found.</p>
      </div>
    {/if}
  {/if}
</div>

<style>
  .pack-lists-page {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
  }

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }

  .page-header h1 {
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

  .empty-state {
    text-align: center;
    padding: 4rem 2rem;
    background-color: #f8f9fa;
    border-radius: 10px;
    margin-top: 2rem;
  }

  .empty-state h2 {
    color: #666;
    margin-bottom: 1rem;
  }

  .empty-state p {
    color: #888;
    margin-bottom: 2rem;
  }

  .table-toolbar {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
    padding: 1rem;
    background-color: #f8f9fa;
    border-radius: 4px;
  }

  .table-toolbar label {
    font-weight: 500;
    color: #666;
  }

  .table-toolbar select {
    padding: 0.5rem 1rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    background-color: white;
    cursor: pointer;
  }

  .pack-lists-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
  }

  .empty-filter-state {
    text-align: center;
    padding: 3rem;
    color: #888;
  }

  @media (max-width: 768px) {
    .pack-lists-page {
      padding: 1rem;
    }

    .page-header {
      flex-direction: column;
      gap: 1rem;
      align-items: stretch;
    }

    .pack-lists-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
