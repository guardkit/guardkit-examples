<script>
  import { createEventDispatcher } from 'svelte';
  import Card from '@smui/card';
  import Chip from '@smui/chips';
  import PackListProgress from './PackListProgress.svelte';

  export let list;
  export let progress;

  const dispatch = createEventDispatcher();

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  };

  const handleClick = () => {
    dispatch('click');
  };
</script>

<Card class="pack-list-card" on:click={handleClick}>
  <div class="card-content">
    <div class="card-header">
      <h3>{list.meetingName}</h3>
      <span class="status-badge" class:active={list.status === 'active'} class:archived={list.status === 'archived'}>
        {list.status}
      </span>
    </div>

    <div class="card-meta">
      <p class="date">{formatDate(list.meetingDate)}</p>
    </div>

    <PackListProgress {progress} />

    <div class="card-footer">
      <span class="item-count">
        {progress.total} {progress.total === 1 ? 'item' : 'items'}
      </span>
    </div>
  </div>
</Card>

<style>
  :global(.pack-list-card) {
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
    border: 1px solid #e0e0e0;
  }

  :global(.pack-list-card:hover) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .card-content {
    padding: 1.5rem;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.75rem;
  }

  .card-header h3 {
    margin: 0;
    font-size: 1.25rem;
    color: #333;
    flex: 1;
  }

  .status-badge {
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

  .card-meta {
    margin-bottom: 1rem;
  }

  .date {
    margin: 0;
    color: #666;
    font-size: 0.9rem;
  }

  .card-footer {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #e0e0e0;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .item-count {
    color: #666;
    font-size: 0.9rem;
  }
</style>
