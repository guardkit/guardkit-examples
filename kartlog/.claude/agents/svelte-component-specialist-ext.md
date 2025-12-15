# Svelte Component Specialist - Extended Documentation

This file contains detailed examples, best practices, and in-depth guidance for the **svelte-component-specialist** agent.

**Core documentation**: See [svelte-component-specialist.md](./svelte-component-specialist.md)

---

## Related Templates

### Primary Component Templates

- **`templates/presentation/components/SessionsTable.svelte.template`** - Advanced DataTable with grouped data, custom sorting, and Material Design styling. Demonstrates complex table patterns with day-based grouping and session rows.

- **`templates/presentation/routes/NewSession.svelte.template`** - Comprehensive form component with validation, conditional fields, SMUI input components (Textfield, Select, Checkbox), and async submission with error handling.

- **`templates/presentation/components/Navigation.svelte.template`** - TopAppBar with authentication state, mobile-responsive menu, store subscriptions, and SPA routing integration.

### Supporting Templates

- **`templates/presentation/routes/Dashboard.svelte.template`** - Dashboard layout with LayoutGrid, Paper components, parallel data loading, and reactive computed values.

- **`templates/presentation/routes/Chat.svelte.template`** - Streaming UI pattern with real-time content updates and message list management.

- **`templates/state management/lib/stores.js.template`** - Svelte writable stores for global state (user, sessions, tyres, tracks, engines, chassis).

## Code Examples

### Example 1: SMUI Form with Validation (Svelte 5)

**DO**: Use SMUI components with comprehensive validation and loading states

```javascript
<script>
  import Button from '@smui/button';
  import Textfield from '@smui/textfield';
  import Select, { Option } from '@smui/select';
  import Checkbox from '@smui/checkbox';
  import FormField from '@smui/form-field';
  import CircularProgress from '@smui/circular-progress';
  import { push } from 'svelte-spa-router';
  import { addSession } from '../service-layer/firestore/sessions.js';

  let date = '';
  let circuitId = '';
  let temp = '';
  let isRace = false;
  let loading = false;
  let error = '';

  // Reactive validation
  $: isValid = date && circuitId && !isNaN(Number(temp)) && Number(temp) > 0;

  const handleSubmit = async () => {
    if (!date || !circuitId) {
      error = 'Please fill in all required fields';
      return;
    }
    if (isNaN(Number(temp)) || Number(temp) <= 0) {
      error = 'Temperature must be a valid positive number';
      return;
    }

    loading = true;
    error = '';
    try {
      const sessionData = {
        date,
        circuitId,
        temp: Number(temp),
        isRace
      };
      await addSession(sessionData);
      push('/sessions');
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  };
</script>

<form on:submit|preventDefault={handleSubmit}>
  <Textfield
    bind:value={date}
    label="Date"
    type="date"
    required
    style="width: 100%;"
  />

  <Select bind:value={circuitId} label="Circuit" required>
    <Option value="">Select circuit...</Option>
    <Option value="spa">Spa-Francorchamps</Option>
    <Option value="monza">Monza</Option>
  </Select>

  <Textfield
    bind:value={temp}
    label="Temperature (°C)"
    type="number"
    input$min="1"
    required
  />

  <FormField>
    <Checkbox bind:checked={isRace} />
    <span slot="label">Race Session</span>
  </FormField>

  {#if error}
    <div class="error">{error}</div>
  {/if}

  {#if loading}
    <CircularProgress indeterminate />
  {:else}
    <Button variant="raised" type="submit" disabled={!isValid}>
      Submit
    </Button>
  {/if}
</form>
```

**DON'T**: Use plain HTML inputs without validation or loading states

```javascript
<!-- AVOID: No validation, no SMUI, no loading states -->
<form on:submit={handleSubmit}>
  <input bind:value={date} type="date" />
  <input bind:value={temp} type="number" />
  <button type="submit">Submit</button>
</form>
```

---

### Example 2: DataTable with Grouped Data

**DO**: Use SMUI DataTable with proper grouping, reactive sorting, and semantic structure

```javascript
<script>
  import DataTable, { Head, Body, Row, Cell } from '@smui/data-table';

  export let sessions = [];

  // Reactive grouping by day
  $: sessionsByDay = sessions.reduce((acc, session) => {
    const dayKey = session.date.split('T')[0];
    if (!acc[dayKey]) acc[dayKey] = [];
    acc[dayKey].push(session);
    return acc;
  }, {});

  $: dayKeys = Object.keys(sessionsByDay).sort((a, b) => 
    new Date(b) - new Date(a)
  );
</script>

<DataTable style="width: 100%;">
  <Head>
    <Row>
      <Cell>Date</Cell>
      <Cell>Circuit</Cell>
      <Cell>Temp (°C)</Cell>
      <Cell>Type</Cell>
      <Cell>Actions</Cell>
    </Row>
  </Head>
  <Body>
    {#each dayKeys as dayKey}
      {@const daySessions = sessionsByDay[dayKey]}
      <Row class="day-header-row">
        <Cell colspan="5">
          <strong>{new Date(dayKey).toLocaleDateString()}</strong>
          ({daySessions.length} sessions)
        </Cell>
      </Row>
      {#each daySessions as session (session.id)}
        <Row class="session-row">
          <Cell>{session.date}</Cell>
          <Cell>{session.circuitName}</Cell>
          <Cell>{session.temp}</Cell>
          <Cell>{session.isRace ? 'Race' : 'Practice'}</Cell>
          <Cell>
            <IconButton class="material-icons" size="button">edit</IconButton>
          </Cell>
        </Row>
      {/each}
    {/each}
  </Body>
</DataTable>

<style>
  :global(.day-header-row) {
    background-color: #f5f5f5;
  }
  :global(.session-row:hover) {
    background-color: #fafafa;
  }
</style>
```

---

### Example 3: Async Data Loading with Error Handling

**DO**: Use Promise.all for parallel loading with proper lifecycle management

```javascript
<script>
  import { onMount } from 'svelte';
  import CircularProgress from '@smui/circular-progress';
  import { getUserTyres } from '../service-layer/firestore/tyres.js';
  import { getUserEngines } from '../service-layer/firestore/engines.js';
  import { getUserSessions } from '../service-layer/firestore/sessions.js';

  let tyres = [];
  let engines = [];
  let sessions = [];
  let loading = false;
  let error = '';

  // Reactive computed values
  $: activeTyres = tyres.filter(t => !t.retired).length;
  $: totalSessions = sessions.length;

  const loadData = async () => {
    try {
      loading = true;
      error = '';
      const [tyresData, enginesData, sessionsData] = await Promise.all([
        getUserTyres(),
        getUserEngines(),
        getUserSessions()
      ]);
      tyres = tyresData;
      engines = enginesData;
      sessions = sessionsData;
    } catch (err) {
      error = err.message;
      console.error('Data loading error:', err);
    } finally {
      loading = false;
    }
  };

  onMount(loadData);
</script>

{#if loading}
  <div class="loading-container">
    <CircularProgress indeterminate />
    <p>Loading data...</p>
  </div>
{:else if error}
  <div class="error-container">
    <p>Error: {error}</p>
    <Button on:click={loadData}>Retry</Button>
  </div>
{:else}
  <div class="stats">
    <div class="stat-card">
      <h3>Active Tyres</h3>
      <p>{activeTyres}</p>
    </div>
    <div class="stat-card">
      <h3>Total Sessions</h3>
      <p>{totalSessions}</p>
    </div>
  </div>
{/if}
```

---

*This extended documentation is part of GuardKit's progressive disclosure system.*
