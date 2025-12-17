<script>
  import { onMount } from 'svelte';
  import { push, link } from 'svelte-spa-router';
  import { getUserPackTemplates, deletePackTemplate } from '../lib/firestore/packTemplates.js';
  import DataTable, { Head, Body, Row, Cell } from '@smui/data-table';
  import Button from '@smui/button';
  import IconButton from '@smui/icon-button';
  import Menu from '@smui/menu';
  import List, { Item, Text } from '@smui/list';
  import CircularProgress from '@smui/circular-progress';
  import './pack-templates.css';

  let templates = [];
  let loading = true;
  let error = '';
  let menuMap = {};

  const loadTemplates = async () => {
    try {
      loading = true;
      templates = await getUserPackTemplates();
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  };

  const handleDelete = async (templateId) => {
    if (!confirm('Are you sure you want to delete this template? Existing packs created from this template will not be affected.')) {
      return;
    }

    try {
      await deletePackTemplate(templateId);
      await loadTemplates();
    } catch (err) {
      error = err.message;
    }
  };

  const handleMenuItemClick = (action, templateId) => {
    if (menuMap[templateId]) {
      menuMap[templateId].setOpen(false);
    }

    if (action === 'edit') {
      push(`/templates/${templateId}/edit`);
    } else if (action === 'delete') {
      handleDelete(templateId);
    }
  };

  onMount(() => {
    loadTemplates();
  });
</script>

<div class="container container-lg">
  <div class="page-header">
    <h1>Pack Templates</h1>
    <Button href="/templates/new" tag="a" use={[link]} variant="raised" color="primary">
      + Create Template
    </Button>
  </div>

  {#if error}
    <div class="error-message">{error}</div>
  {/if}

  {#if loading}
    <div class="loading-state">
      <CircularProgress style="height: 48px; width: 48px;" indeterminate />
      <p>Loading templates...</p>
    </div>
  {:else if templates.length === 0}
    <div class="empty-state">
      <h3>No templates yet</h3>
      <p>Create your first pack template to get started.</p>
      <Button href="/templates/new" tag="a" use={[link]} variant="raised" color="primary">
        Create Template
      </Button>
    </div>
  {:else}
    <div class="table-container">
      <DataTable style="width: 100%;">
        <Head>
          <Row>
            <Cell>Name</Cell>
            <Cell>Description</Cell>
            <Cell class="col-sessions">Categories</Cell>
            <Cell class="col-status">Items</Cell>
            <Cell class="actions-header col-actions">Actions</Cell>
          </Row>
        </Head>
        <Body>
          {#each templates as template (template.id)}
            <Row class="pack-template-row">
              <div class="clickable-row">
                <Cell>{template.name}</Cell>
                <Cell>{template.description || '—'}</Cell>
                <Cell class="col-sessions">{template.categories?.length || 0}</Cell>
                <Cell class="col-status">{template.items?.length || 0}</Cell>
                <Cell class="col-actions">
                  <div class="action-buttons desktop-actions">
                    <a href="/templates/{template.id}/edit" use:link class="text-button">
                      Edit
                    </a>
                    <button on:click|stopPropagation|preventDefault={() => handleDelete(template.id)} class="text-button delete-button">
                      Delete
                    </button>
                  </div>
                  <div class="kebab-menu-container" on:click|stopPropagation on:keydown|stopPropagation role="none">
                    <div class="menu-surface-anchor">
                      <button
                        class="kebab-button-simple"
                        on:click={() => menuMap[template.id]?.setOpen(true)}
                        aria-label="More actions"
                      >
                        ⋮
                      </button>
                      <Menu bind:this={menuMap[template.id]}>
                        <List>
                          <Item onSMUIAction={() => handleMenuItemClick('edit', template.id)}>
                            <Text>Edit</Text>
                          </Item>
                          <Item onSMUIAction={() => handleMenuItemClick('delete', template.id)}>
                            <Text class="delete-text">Delete</Text>
                          </Item>
                        </List>
                      </Menu>
                    </div>
                  </div>
                </Cell>
              </div>
            </Row>
          {/each}
        </Body>
      </DataTable>
    </div>
  {/if}
</div>

<style>
  :global(.pack-template-row) {
    position: relative;
  }

  :global(.pack-template-row td) {
    vertical-align: middle;
    font-size: 16px;
    overflow: visible;
  }

  .clickable-row {
    display: contents;
  }

  @media (max-width: 768px) {
    :global(.col-sessions) {
      display: none;
    }
  }

  @media (max-width: 640px) {
    :global(.col-status) {
      display: none;
    }
  }

  @media (max-width: 480px) {
    .desktop-actions {
      display: none;
    }

    .kebab-menu-container {
      display: block;
    }

    :global(.actions-header) {
      width: 48px;
    }
  }
</style>
