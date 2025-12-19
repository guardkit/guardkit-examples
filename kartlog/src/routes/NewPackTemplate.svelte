<script>
  import { push } from 'svelte-spa-router';
  import { addPackTemplate } from '../lib/firestore/packTemplates.js';
  import { showNotification } from '../lib/stores.js';
  import PackTemplateEditor from '../lib/components/pack-templates/PackTemplateEditor.svelte';

  let isLoading = false;

  const handleSubmit = async (templateData) => {
    try {
      isLoading = true;
      const templateId = await addPackTemplate(
        templateData.name,
        templateData.description,
        templateData.categories,
        templateData.items
      );
      showNotification(`Template "${templateData.name}" created successfully!`, 'success');
      push('/templates');
    } catch (err) {
      showNotification(`Error creating template: ${err.message}`, 'error');
    } finally {
      isLoading = false;
    }
  };
</script>

<div class="form-page">
  <div class="page-header">
    <h1>Create Pack Template</h1>
  </div>

  <PackTemplateEditor
    mode="create"
    initialData={{
      name: '',
      description: '',
      categories: [],
      items: []
    }}
    onSubmit={handleSubmit}
    {isLoading}
  />
</div>

<style>
  .form-page {
    max-width: 900px;
    margin: 2rem auto;
    padding: 0 1rem;
  }

  .page-header {
    margin-bottom: 2rem;
  }

  .page-header h1 {
    margin: 0;
    font-size: 2rem;
    color: #333;
  }

  @media (max-width: 768px) {
    .form-page {
      margin: 1rem 0;
      padding: 0;
    }

    .page-header h1 {
      font-size: 1.5rem;
      padding: 0 1rem;
    }
  }
</style>
