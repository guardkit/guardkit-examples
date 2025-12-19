<script>
  import { onMount } from 'svelte';
  import { push, link } from 'svelte-spa-router';
  import { getPackTemplate, updatePackTemplate } from '../lib/firestore/packTemplates.js';
  import { showNotification } from '../lib/stores.js';
  import Button from '@smui/button';
  import CircularProgress from '@smui/circular-progress';
  import PackTemplateEditor from '../lib/components/pack-templates/PackTemplateEditor.svelte';

  export let params = {};

  let templateId = '';
  let templateData = {
    name: '',
    description: '',
    categories: [],
    items: []
  };
  let isLoading = true;
  let error = '';

  const loadTemplate = async () => {
    templateId = params.id;
    if (!templateId) {
      error = 'Template ID not provided';
      isLoading = false;
      return;
    }

    try {
      isLoading = true;
      const data = await getPackTemplate(templateId);
      templateData = {
        name: data.name,
        description: data.description,
        categories: data.categories || [],
        items: data.items || []
      };
    } catch (err) {
      error = err.message;
    } finally {
      isLoading = false;
    }
  };

  const handleSubmit = async (newData) => {
    try {
      isLoading = true;
      await updatePackTemplate(templateId, {
        name: newData.name,
        description: newData.description,
        categories: newData.categories,
        items: newData.items
      });
      showNotification(`Template "${newData.name}" updated successfully!`, 'success');
      push('/templates');
    } catch (err) {
      showNotification(`Error updating template: ${err.message}`, 'error');
    } finally {
      isLoading = false;
    }
  };

  const handleCancel = () => {
    push('/templates');
  };

  onMount(() => {
    loadTemplate();
  });
</script>

<div class="form-page">
  <div class="page-header">
    <h1>Edit Pack Template</h1>
    <Button href="/templates" tag="a" use={[link]} variant="outlined">← Back to Templates</Button>
  </div>

  {#if error}
    <div class="error-message">{error}</div>
  {/if}

  {#if isLoading && !templateData.name}
    <div class="loading-state">
      <CircularProgress style="height: 48px; width: 48px;" indeterminate />
      <p>Loading template...</p>
    </div>
  {:else if templateData.name}
    <PackTemplateEditor
      mode="edit"
      initialData={templateData}
      onSubmit={handleSubmit}
      {isLoading}
    />
  {/if}
</div>

<style>
  .form-page {
    max-width: 900px;
    margin: 2rem auto;
    padding: 0 1rem;
  }

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    gap: 1rem;
  }

  .page-header h1 {
    margin: 0;
    font-size: 2rem;
    color: #333;
    flex: 1;
  }

  .error-message {
    padding: 1rem;
    margin-bottom: 1.5rem;
    background-color: #ffebee;
    border-left: 4px solid #f44336;
    color: #c62828;
    border-radius: 4px;
  }

  .loading-state {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 4rem 2rem;
    gap: 1rem;
  }

  .loading-state p {
    color: #666;
    font-size: 1rem;
  }

  @media (max-width: 768px) {
    .form-page {
      margin: 1rem 0;
      padding: 0;
    }

    .page-header {
      flex-direction: column;
      align-items: stretch;
      margin-bottom: 1rem;
    }

    .page-header h1 {
      font-size: 1.5rem;
      padding: 0 1rem;
    }
  }
</style>
