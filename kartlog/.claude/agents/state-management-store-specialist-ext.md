# State Management Store Specialist - Extended Documentation

This file contains detailed examples, best practices, and in-depth guidance for the **state-management-store-specialist** agent.

**Core documentation**: See [state-management-store-specialist.md](./state-management-store-specialist.md)

---

## Related Templates

### Primary Templates

1. **`templates/state management/lib/stores.js.template`** (PRIMARY)
   - Demonstrates writable store creation for user and loading state
   - Shows Firebase authentication integration with onAuthStateChanged
   - Implements mock vs production environment conditional logic
   - Foundation pattern for all application state management

2. **`templates/service layer/lib/databaseListeners.js.template`**
   - Real-time Firestore listener setup with onSnapshot
   - Debounced refresh pattern to prevent excessive updates
   - Listener lifecycle management with unsubscribe function tracking
   - User-scoped query creation with authentication check

3. **`templates/presentation/routes/Dashboard.svelte.template`**
   - Reactive computed values using `$:` syntax with store data
   - Multiple derived calculations from array stores
   - Date filtering and aggregation patterns on reactive data

### Supporting Templates

4. **`templates/presentation/components/Navigation.svelte.template`**
   - Store consumption in components with `$user` syntax
   - Conditional rendering based on authentication state

5. **`templates/presentation/routes/Chat.svelte.template`**
   - Component-level loading state management
   - Filtering patterns on reactive message arrays
   - Streaming state flags for async operations

## Code Examples

### Example 1: Authentication Store with Mock Support

**DO** - Implement environment-aware authentication store:

```javascript
import { writable } from 'svelte/store';
import { auth, onAuthStateChanged } from './firebase.js';

export const user = writable(null);
export const loading = writable(true);

const useMock = import.meta.env.VITE_USE_MOCK_FIRESTORE === 'true';

if (useMock) {
  const checkAuth = () => {
    if (auth.currentUser) {
      user.set(auth.currentUser);
    }
    loading.set(false);
  };
  checkAuth();
  setTimeout(checkAuth, 100);
} else {
  onAuthStateChanged(auth, (currentUser) => {
    user.set(currentUser);
    loading.set(false);
  });
}
```

**DON'T** - Create store without loading state or environment handling:

```javascript
// Missing loading state, no mock support
import { writable } from 'svelte/store';
export const user = writable(null);
onAuthStateChanged(auth, (currentUser) => {
  user.set(currentUser);
});
```

### Example 2: Real-time Listeners with Debounce

**DO** - Implement debounced listener pattern:

```javascript
import { collection, query, where, onSnapshot } from './firebase.js';
import { auth, db } from './firebase.js';
import { refreshDatabase, isDatabaseInitialized } from './query.js';

let unsubscribeFunctions = [];
let isListening = false;

export function startDatabaseListeners() {
  if (isListening) return;
  
  const userId = auth.currentUser?.uid;
  if (!userId) return;

  let refreshTimeout = null;
  const debouncedRefresh = () => {
    if (refreshTimeout) clearTimeout(refreshTimeout);
    refreshTimeout = setTimeout(async () => {
      if (isDatabaseInitialized()) {
        await refreshDatabase();
      }
    }, 500);
  };

  const tyresQuery = query(
    collection(db, 'tyres'),
    where('userId', '==', userId)
  );
  
  unsubscribeFunctions.push(
    onSnapshot(tyresQuery, () => debouncedRefresh())
  );
  
  isListening = true;
}

export function stopDatabaseListeners() {
  unsubscribeFunctions.forEach(unsubscribe => unsubscribe());
  unsubscribeFunctions = [];
  isListening = false;
}
```

### Example 3: Reactive Computed Values in Components

**DO** - Use reactive statements for derived data:

```javascript
<script>
  let tyres = [];
  let sessions = [];
  
  $: activeTyres = tyres.filter(t => !t.retired).length;
  $: totalSessions = sessions.length;
  $: sessionsThisMonth = sessions.filter(s => {
    const sessionDate = s.date.toDate ? s.date.toDate() : new Date(s.date);
    return sessionDate.getMonth() === new Date().getMonth();
  }).length;
</script>
```

### Example 4: Store Consumption in Components

**DO** - Use `$` auto-subscription syntax:

```javascript
<script>
  import { user } from '../lib/stores.js';
</script>

<nav>
  {#if $user}
    <span>Welcome, {$user.email}</span>
  {:else}
    <a href="/login">Sign In</a>
  {/if}
</nav>
```

---

*This extended documentation is part of GuardKit's progressive disclosure system.*
