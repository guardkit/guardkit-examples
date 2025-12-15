# Firestore Repository Specialist - Extended Documentation

This file contains detailed examples, best practices, and in-depth guidance for the **firestore-repository-specialist** agent.

**Core documentation**: See [firestore-repository-specialist.md](./firestore-repository-specialist.md)

---

## Related Templates

### Primary References

- **`templates/service layer/firestore/sessions.js.template`** - Comprehensive example showing user-scoped CRUD, relational joins, type processing, and authorization checks for session data
- **`templates/service layer/firestore/tyres.js.template`** - Demonstrates basic CRUD operations with user scope, soft delete (retirement) pattern, and query filtering
- **`templates/service layer/firestore/engines.js.template`** - Shows Timestamp handling, user-scoped collections, and retirement workflow
- **`templates/service layer/firestore/tracks.js.template`** - Illustrates user-scoped track management with ordering and filtering

### Supporting References

- **`templates/infrastructure/lib/firebase.js.template`** - Centralized Firebase module with mock/real implementation switching
- **`templates/service layer/lib/query.js.template`** - Query helper utilities for building complex Firestore queries
- **`templates/infrastructure/firestore-mock/firebase.js.template`** - Mock Firebase implementation for testing user-scoped repositories

## Code Examples

### Example 1: User-Scoped CRUD Repository

**DO** - Always validate authentication and scope data to current user:

```javascript
import { db, auth, collection, addDoc, getDocs, doc, updateDoc, deleteDoc, query, where, orderBy } from '../firebase.js';

// CREATE - Add document with user scope
export const addTyre = async (name, make, type, description, retired) => {
  if (!auth.currentUser) {
    throw new Error('User must be logged in to add tyres');
  }
  await addDoc(collection(db, 'tyres'), {
    userId: auth.currentUser.uid,  // User scope enforced
    name,
    make,
    type,
    description: description || '',
    retired: retired || false,
    createdAt: new Date()
  });
};

// READ - Query with user scope filter
export const getUserTyres = async () => {
  if (!auth.currentUser) {
    throw new Error('User must be logged in to view tyres');
  }
  const q = query(
    collection(db, 'tyres'),
    where('userId', '==', auth.currentUser.uid),  // Filter by user
    orderBy('createdAt', 'desc')
  );
  const querySnapshot = await getDocs(q);
  return querySnapshot.docs.map(doc => ({
    id: doc.id,
    ...doc.data()
  }));
};
```

**DON'T** - Never create documents without user scope or skip auth checks:

```javascript
// WRONG - Missing auth check and userId field
export const addTyre = async (name, make, type) => {
  await addDoc(collection(db, 'tyres'), {
    name,
    make,
    type
    // Missing: userId, auth check, validation
  });
};
```

### Example 2: Relational Joins Across Collections

**DO** - Use Promise.all for parallel fetches and Map for efficient lookups:

```javascript
async function joinSessionData(sessions) {
  const [tyres, engines, chassis, tracks] = await Promise.all([
    getUserTyres(),
    getUserEngines(),
    getUserChassis(),
    getUserTracks()
  ]);

  const tyresMap = new Map(tyres.map(t => [t.id, t]));
  const enginesMap = new Map(engines.map(e => [e.id, e]));
  const chassisMap = new Map(chassis.map(c => [c.id, c]));
  const tracksMap = new Map(tracks.map(t => [t.id, t]));

  const joinSession = (session) => ({
    ...session,
    tyre: session.tyreId ? tyresMap.get(session.tyreId) : null,
    engine: session.engineId ? enginesMap.get(session.engineId) : null,
    chassis: session.chassisId ? chassisMap.get(session.chassisId) : null,
    circuit: session.circuitId ? tracksMap.get(session.circuitId) : null
  });

  return Array.isArray(sessions) 
    ? sessions.map(joinSession)
    : joinSession(sessions);
}

export const getUserSessions = async (join = false) => {
  const sessions = await fetchSessionsFromFirestore();
  return join ? await joinSessionData(sessions) : sessions;
};
```

### Example 3: Authorization and Data Type Processing

**DO** - Verify document ownership and coerce types:

```javascript
export const getSession = async (sessionId, join = false) => {
  if (!auth.currentUser) {
    throw new Error('User must be logged in to view sessions');
  }
  
  const sessionRef = doc(db, 'sessions', sessionId);
  const sessionSnap = await getDoc(sessionRef);
  
  if (!sessionSnap.exists()) {
    throw new Error('Session not found');
  }
  
  const sessionData = sessionSnap.data();
  
  if (sessionData.userId !== auth.currentUser.uid) {
    throw new Error('Access denied');
  }
  
  const session = { id: sessionSnap.id, ...sessionData };
  return join ? await joinSessionData(session) : session;
};

export const addSession = async (sessionData) => {
  if (!auth.currentUser) {
    throw new Error('User must be logged in to add sessions');
  }
  
  const processedData = {
    userId: auth.currentUser.uid,
    date: new Date(sessionData.date),
    temp: parseFloat(sessionData.temp),
    laps: parseInt(sessionData.laps),
    fastest: sessionData.fastest ? parseFloat(sessionData.fastest) : null,
    isRace: sessionData.isRace || false,
    createdAt: new Date()
  };
  
  await addDoc(collection(db, 'sessions'), processedData);
};
```

### Example 4: Soft Delete Pattern

**DO** - Use retirement flags instead of hard deletes:

```javascript
export const retireTyre = async (tyreId) => {
  if (!auth.currentUser) {
    throw new Error('User must be logged in to retire tyres');
  }
  
  const tyreRef = doc(db, 'tyres', tyreId);
  await updateDoc(tyreRef, {
    retired: true,
    retiredAt: new Date()
  });
};
```

---

*This extended documentation is part of GuardKit's progressive disclosure system.*
