<script>
  import LinearProgress from '@smui/linear-progress';

  export let progress;

  $: percentage = progress.percentage || 0;
  $: checked = progress.checked || 0;
  $: total = progress.total || 0;
</script>

<div class="progress-container">
  <div class="progress-header">
    <span class="progress-label">Progress</span>
    <span class="progress-text">{checked}/{total}</span>
    <span class="progress-percentage">{percentage}%</span>
  </div>
  <LinearProgress progress={percentage / 100} />
</div>

<style>
  .progress-container {
    margin: 1rem 0;
  }

  .progress-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .progress-label {
    font-size: 0.85rem;
    color: #666;
    font-weight: 500;
  }

  .progress-text {
    font-size: 0.9rem;
    color: #333;
    font-weight: 600;
  }

  .progress-percentage {
    font-size: 0.85rem;
    color: #1976d2;
    font-weight: 600;
  }
</style>
