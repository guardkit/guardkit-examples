# Real Time Firestore Listener Specialist - Extended Documentation

This file contains detailed examples, best practices, and in-depth guidance for the **real-time-firestore-listener-specialist** agent.

**Core documentation**: See [real-time-firestore-listener-specialist.md](./real-time-firestore-listener-specialist.md)

---

## Related Templates

### Primary Templates

1. **`templates/service layer/lib/databaseListeners.js.template`** (PRIMARY)
   - Complete implementation of multi-collection Firestore listeners with debounced refresh pattern
   - Shows lifecycle management (startDatabaseListeners, stopDatabaseListeners)
   - Cleanup with unsubscribe functions and error handling

2. **`templates/infrastructure/lib/firebase.js.template`**
   - Centralized Firebase initialization with conditional mock/real Firestore support
   - Exports onSnapshot, query, where, and other Firestore primitives used by listeners

3. **`templates/state management/lib/stores.js.template`**
   - Authentication state management with onAuthStateChanged listener pattern
   - Demonstrates Svelte store integration and mock authentication detection

### Supporting Templates

4. **`templates/service layer/firestore/sessions.js.template`**
   - Example Firestore service layer showing query patterns
   - Data fetching that listeners trigger refreshes for

5. **`templates/presentation/routes/Dashboard.svelte.template`**
   - Component lifecycle integration
   - Where to call startDatabaseListeners() on mount and stopDatabaseListeners() on destroy

## Code Examples

### Example 1: Multi-Collection Listener Manager

**DO** - Store unsubscribe functions and implement coordinated debounce:

```javascript
import { db, collection, query, where, onSnapshot, auth } from './firebase.js';
import { refreshDatabase, isDatabaseInitialized } from './query.js';

let unsubscribeFunctions = [];
let isListening = false;

export function startDatabaseListeners() {
  if (isListening) {
    console.log('Database listeners already running');
    return;
  }

  const userId = auth.currentUser?.uid;
  if (!userId) {
    console.warn('Cannot start database listeners: no user logged in');
    return;
  }

  let refreshTimeout = null;
  const debouncedRefresh = () => {
    if (refreshTimeout) clearTimeout(refreshTimeout);
    refreshTimeout = setTimeout(async () => {
      if (isDatabaseInitialized()) {
        try {
          await refreshDatabase();
          console.log('Database refreshed due to Firestore changes');
        } catch (error) {
          console.error('Error refreshing database:', error);
        }
      }
    }, 500);
  };

  // Listen to tyres collection
  const tyresQuery = query(collection(db, 'tyres'), where('userId', '==', userId));
  unsubscribeFunctions.push(
    onSnapshot(tyresQuery,
      () => {
        console.log('Tyres collection changed');
        debouncedRefresh();
      },
      (error) => {
        console.error('Tyres listener error:', error);
      }
    )
  );

  // Listen to engines collection
  const enginesQuery = query(collection(db, 'engines'), where('userId', '==', userId));
  unsubscribeFunctions.push(
    onSnapshot(enginesQuery,
      () => {
        console.log('Engines collection changed');
        debouncedRefresh();
      },
      (error) => {
        console.error('Engines listener error:', error);
      }
    )
  );

  isListening = true;
  console.log('Firestore listeners active');
}

export function stopDatabaseListeners() {
  if (!isListening) return;
  
  console.log('Stopping Firestore listeners...');
  unsubscribeFunctions.forEach(unsubscribe => unsubscribe());
  unsubscribeFunctions = [];
  isListening = false;
}
```

**DON'T** - Create separate debounce timers per collection:

```javascript
// ANTI-PATTERN: Multiple uncoordinated debounce timers
export function startDatabaseListeners() {
  const userId = auth.currentUser?.uid;
  
  // BAD: Each collection has its own timeout
  let tyresTimeout = null;
  const tyresQuery = query(collection(db, 'tyres'), where('userId', '==', userId));
  onSnapshot(tyresQuery, () => {
    if (tyresTimeout) clearTimeout(tyresTimeout);
    tyresTimeout = setTimeout(() => refreshDatabase(), 500);
  });
  
  let enginesTimeout = null;
  const enginesQuery = query(collection(db, 'engines'), where('userId', '==', userId));
  onSnapshot(enginesQuery, () => {
    if (enginesTimeout) clearTimeout(enginesTimeout);
    enginesTimeout = setTimeout(() => refreshDatabase(), 500);
  });
  
  // PROBLEM: If tyres and engines change 100ms apart,
  // refreshDatabase() gets called twice instead of once
}
```

### Example 2: Component Lifecycle Integration

**DO** - Start listeners on mount, stop on destroy:

```svelte
<script>
  import { onMount, onDestroy } from 'svelte';
  import { startDatabaseListeners, stopDatabaseListeners } from '../lib/databaseListeners.js';
  import { user } from '../lib/stores.js';

  onMount(() => {
    if ($user) {
      startDatabaseListeners();
    }
  });

  onDestroy(() => {
    stopDatabaseListeners();
  });
</script>
```

**DON'T** - Forget cleanup or start listeners without authentication check:

```svelte
<!-- ANTI-PATTERN: Missing cleanup and auth check -->
<script>
  import { onMount } from 'svelte';
  import { startDatabaseListeners } from '../lib/databaseListeners.js';

  onMount(() => {
    // BAD: No authentication check
    startDatabaseListeners();
    // BAD: No onDestroy cleanup
  });
</script>
```

### Example 3: Authentication-Aware Listener Initialization

**DO** - Use Svelte store reactivity to start listeners after authentication:

```svelte
<script>
  import { user, loading } from '../lib/stores.js';
  import { startDatabaseListeners, stopDatabaseListeners } from '../lib/databaseListeners.js';
  import { onDestroy } from 'svelte';

  let listenersStarted = false;

  $: if ($user && !$loading && !listenersStarted) {
    startDatabaseListeners();
    listenersStarted = true;
  }

  onDestroy(() => {
    if (listenersStarted) {
      stopDatabaseListeners();
    }
  });
</script>
```

---

*This extended documentation is part of GuardKit's progressive disclosure system.*
