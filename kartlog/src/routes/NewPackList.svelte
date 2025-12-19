<script>
  import { onMount } from 'svelte';
  import { push, link } from 'svelte-spa-router';
  import Card from '@smui/card';
  import Textfield from '@smui/textfield';
  import Select, { Option } from '@smui/select';
  import Button from '@smui/button';
  import CircularProgress from '@smui/circular-progress';
  import {
    templates,
    loadingTemplates,
    errorTemplates,
    fetchTemplates,
    createPackListFromTemplate
  } from '../lib/stores/packListStore.js';

  let selectedTemplateId = '';
  let meetingName = '';
  let meetingDate = '';
  let loading = false;
  let error = '';

  const setDefaultDate = () => {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    meetingDate = `${year}-${month}-${day}`;
  };

  const handleSubmit = async () => {
    // Validation
    if (!selectedTemplateId) {
      error = 'Please select a template';
      return;
    }

    if (!meetingName || meetingName.trim() === '') {
      error = 'Please enter a meeting name';
      return;
    }

    if (!meetingDate) {
      error = 'Please select a meeting date';
      return;
    }

    loading = true;
    error = '';

    try {
      const listId = await createPackListFromTemplate(
        selectedTemplateId,
        meetingName.trim(),
        meetingDate
      );

      push(`/pack-lists/view/${listId}`);
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  };

  onMount(() => {
    setDefaultDate();
    fetchTemplates();
  });
</script>

<div class="form-page">
  <div class="header">
    <h1>Create Pack List</h1>
    <Button href="/pack-lists" tag="a" use={[link]} variant="outlined">
      ← Back to Pack Lists
    </Button>
  </div>

  {#if error}
    <div class="error">{error}</div>
  {/if}

  {#if $errorTemplates}
    <div class="error">{$errorTemplates}</div>
  {/if}

  {#if $loadingTemplates}
    <div class="loading">
      <CircularProgress style="height: 32px; width: 32px;" indeterminate />
      <p>Loading templates...</p>
    </div>
  {:else}
    <Card style="padding: 2rem;">
      <form on:submit|preventDefault={handleSubmit}>
        <div class="form-section">
          <h3>Select Template</h3>

          <div class="form-group">
            <Select bind:value={selectedTemplateId} label="Pack Template" required style="width: 100%;">
              <Option value="">Select a template...</Option>
              {#each $templates as template (template.id)}
                <Option value={template.id}>{template.name}</Option>
              {/each}
            </Select>

            {#if $templates.length === 0}
              <p class="no-items">
                No templates found. <a href="#/pack-templates/new">Create a template first</a>.
              </p>
            {/if}
          </div>

          {#if selectedTemplateId}
            {@const selectedTemplate = $templates.find(t => t.id === selectedTemplateId)}
            {#if selectedTemplate}
              <div class="template-preview">
                <p class="description">{selectedTemplate.description}</p>
                <p class="item-count">
                  {selectedTemplate.items.length} {selectedTemplate.items.length === 1 ? 'item' : 'items'}
                  across {selectedTemplate.categories.length} {selectedTemplate.categories.length === 1 ? 'category' : 'categories'}
                </p>
              </div>
            {/if}
          {/if}
        </div>

        <div class="form-section">
          <h3>Meeting Details</h3>

          <div class="form-group">
            <Textfield
              bind:value={meetingName}
              label="Meeting Name"
              required
              style="width: 100%;"
              helperText="e.g., Round 3 - Whilton Mill"
            />
          </div>

          <div class="form-group">
            <Textfield
              type="date"
              bind:value={meetingDate}
              label="Meeting Date"
              required
              style="width: 100%;"
            />
          </div>
        </div>

        <div class="form-actions">
          <Button type="button" onclick={() => push('/pack-lists')} variant="outlined">
            Cancel
          </Button>
          <Button
            type="submit"
            disabled={loading || $templates.length === 0}
            variant="raised"
            style="background-color: #007bff;"
          >
            {loading ? 'Creating...' : 'Create Pack List'}
          </Button>
        </div>
      </form>
    </Card>
  {/if}
</div>

<style>
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
    gap: 1rem;
    padding: 2rem;
  }

  .error {
    padding: 1rem;
    background-color: #fee;
    border: 1px solid #fcc;
    border-radius: 4px;
    color: #c00;
    margin-bottom: 1rem;
  }

  .form-section {
    margin-bottom: 2rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid #e9ecef;
  }

  .form-section:last-of-type {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
  }

  .form-section h3 {
    margin: 0 0 1.5rem 0;
    color: #495057;
    font-size: 1.25rem;
    font-weight: 600;
    border-left: 4px solid #007bff;
    padding-left: 1rem;
  }

  .form-group {
    margin-bottom: 1.5rem;
  }

  .no-items {
    margin-top: 0.5rem;
    color: #dc3545;
    font-size: 0.9rem;
  }

  .no-items a {
    color: #007bff;
    text-decoration: none;
  }

  .no-items a:hover {
    text-decoration: underline;
  }

  .template-preview {
    margin-top: 1rem;
    padding: 1rem;
    background-color: #f8f9fa;
    border-radius: 4px;
    border-left: 4px solid #007bff;
  }

  .template-preview .description {
    margin: 0 0 0.5rem 0;
    color: #666;
  }

  .template-preview .item-count {
    margin: 0;
    color: #888;
    font-size: 0.9rem;
  }

  .form-actions {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
    margin-top: 2rem;
  }

  @media (max-width: 768px) {
    .header {
      flex-direction: column;
      gap: 1rem;
      align-items: stretch;
    }

    .form-actions {
      flex-direction: column;
    }
  }
</style>
