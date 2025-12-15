# Mock Firebase Abstraction Specialist - Extended Documentation

This file contains detailed examples, best practices, and in-depth guidance for the **mock-firebase-abstraction-specialist** agent.

**Core documentation**: See [mock-firebase-abstraction-specialist.md](./mock-firebase-abstraction-specialist.md)

---

## Related Templates

### Primary Templates

1. **`templates/infrastructure/firestore-mock/firebase.js.template`** (PRIMARY)
   - Complete mock Firebase/Firestore implementation using localStorage persistence
   - Mock query engine with where filters, orderBy sorting, onSnapshot listeners
   - Timestamp utilities and test helpers (setMockUser, clearMockData)

2. **`templates/infrastructure/lib/firebase.js.template`**
   - Centralized abstraction layer with environment-based switching
   - Dynamic imports based on VITE_USE_MOCK_FIRESTORE
   - Single import point for all Firebase functionality

### Supporting Templates

3. **`templates/service layer/firestore/sessions.js.template`**
   - Service layer consuming the abstraction
   - Business logic unchanged between mock and real

4. **`templates/service layer/lib/databaseListeners.js.template`**
   - Real-time listener patterns using onSnapshot
   - Works with both mock and real implementations

5. **`templates/state management/lib/stores.js.template`**
   - Svelte stores integration with Firebase abstraction

## Code Examples

### Example 1: Environment-Based Abstraction Layer

**DO** - Use dynamic imports with environment detection:

```javascript
// templates/infrastructure/lib/firebase.js.template
const useMock = import.meta.env.VITE_USE_MOCK_FIRESTORE === 'true';

let auth, db, collection, addDoc, getDocs, query, where, orderBy, onSnapshot;
let setMockUser, clearMockUser, clearMockData, exportMockData, importMockData;

if (useMock) {
  const firebaseModule = await import('./firestore-mock/firebase.js');
  auth = firebaseModule.auth;
  db = firebaseModule.db;
  collection = firebaseModule.collection;
  addDoc = firebaseModule.addDoc;
  getDocs = firebaseModule.getDocs;
  query = firebaseModule.query;
  where = firebaseModule.where;
  orderBy = firebaseModule.orderBy;
  onSnapshot = firebaseModule.onSnapshot;
  
  // Test utilities only in mock mode
  setMockUser = firebaseModule.setMockUser;
  clearMockUser = firebaseModule.clearMockUser;
  clearMockData = firebaseModule.clearMockData;
} else {
  const firebaseModule = await import('./firestore/firebase.js');
  const firestoreModule = await import('firebase/firestore');
  
  auth = firebaseModule.auth;
  db = firebaseModule.db;
  collection = firestoreModule.collection;
  addDoc = firestoreModule.addDoc;
  getDocs = firestoreModule.getDocs;
  query = firestoreModule.query;
  where = firestoreModule.where;
  orderBy = firestoreModule.orderBy;
  onSnapshot = firestoreModule.onSnapshot;
}

export { auth, db, collection, addDoc, getDocs, query, where, orderBy, onSnapshot };
export { setMockUser, clearMockUser, clearMockData, exportMockData, importMockData };

console.log(useMock ? '🔧 MOCK' : '🔥 REAL');
```

**DON'T** - Hard-code implementation:

```javascript
// WRONG - No environment detection
import { auth, db } from './firestore-mock/firebase.js';
```

### Example 2: Mock Query Engine with localStorage Persistence

**DO** - Implement full Firestore API with automatic persistence:

```javascript
class MockFirestoreDB {
  constructor() {
    this.collections = new Map();
    this.loadData();
  }

  loadData() {
    try {
      const stored = localStorage.getItem('mockFirestoreData');
      if (stored) {
        const data = JSON.parse(stored);
        Object.entries(data).forEach(([collectionName, docs]) => {
          this.collections.set(collectionName, new Map(Object.entries(docs)));
        });
      }
    } catch (error) {
      console.warn('Failed to load mock data:', error);
    }
  }

  saveData() {
    try {
      const data = {};
      this.collections.forEach((docs, collectionName) => {
        data[collectionName] = Object.fromEntries(docs);
      });
      localStorage.setItem('mockFirestoreData', JSON.stringify(data));
    } catch (error) {
      console.warn('Failed to save mock data:', error);
    }
  }

  clearAll() {
    this.collections.clear();
    localStorage.removeItem('mockFirestoreData');
  }
}

export const addDoc = async (collectionRef, data) => {
  const coll = mockDB.getCollection(collectionRef._collectionName);
  const id = `mock-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  
  coll.set(id, {
    ...data,
    createdAt: data.createdAt?.toDate ? data.createdAt.toDate() : new Date()
  });
  mockDB.saveData(); // Auto-persist
  
  return { id };
};

export const getDocs = async (queryObj) => {
  let docs = Array.from(mockDB.getCollection(queryObj._collectionName).entries())
    .map(([id, data]) => ({ id, data: () => data, exists: () => true }));
  
  // Apply where filters
  if (queryObj._where) {
    docs = docs.filter(doc => {
      return queryObj._where.every(([field, op, value]) => {
        const fieldVal = doc.data()[field];
        if (op === '==') return fieldVal === value;
        if (op === '!=') return fieldVal !== value;
        if (op === '<') return fieldVal < value;
        if (op === '>') return fieldVal > value;
        return true;
      });
    });
  }
  
  // Apply orderBy
  if (queryObj._orderBy) {
    queryObj._orderBy.forEach(([field, dir]) => {
      docs.sort((a, b) => {
        const cmp = a.data()[field] < b.data()[field] ? -1 : 1;
        return dir === 'desc' ? -cmp : cmp;
      });
    });
  }
  
  return { docs, empty: docs.length === 0, size: docs.length };
};
```

**DON'T** - Use in-memory only storage:

```javascript
// WRONG - Data lost on refresh
const mockData = {};
export function addDoc(coll, data) {
  mockData[coll] = mockData[coll] || [];
  mockData[coll].push(data);
}
```

### Example 3: Real-time Listeners with Storage Events

**DO** - Implement onSnapshot with cross-tab synchronization:

```javascript
export const onSnapshot = (queryObj, callback, errorCallback) => {
  // Initial data load
  getDocs(queryObj).then(callback).catch(errorCallback);
  
  // Listen for localStorage changes (cross-tab sync)
  const storageListener = (event) => {
    if (event.key === 'mockFirestoreData') {
      mockDB.loadData();
      getDocs(queryObj).then(callback).catch(errorCallback);
    }
  };
  
  window.addEventListener('storage', storageListener);
  
  // Return unsubscribe function
  return () => window.removeEventListener('storage', storageListener);
};
```

### Example 4: Test Utilities

**DO** - Provide test helpers in mock implementation:

```javascript
export const setMockUser = (userId = 'test-user-1') => {
  mockAuth.setCurrentUser({
    uid: userId,
    email: `${userId}@test.com`
  });
};

export const clearMockUser = () => mockAuth.signOut();
export const clearMockData = () => mockDB.clearAll();

export const exportMockData = () => {
  const data = {};
  mockDB.collections.forEach((docs, name) => {
    data[name] = Object.fromEntries(docs);
  });
  return data;
};

export const importMockData = (data) => {
  mockDB.collections.clear();
  Object.entries(data).forEach(([name, docs]) => {
    mockDB.collections.set(name, new Map(Object.entries(docs)));
  });
  mockDB.saveData();
};
```

---

*This extended documentation is part of GuardKit's progressive disclosure system.*
