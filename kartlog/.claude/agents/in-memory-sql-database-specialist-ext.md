# In Memory Sql Database Specialist - Extended Documentation

This file contains detailed examples, best practices, and in-depth guidance for the **in-memory-sql-database-specialist** agent.

**Core documentation**: See [in-memory-sql-database-specialist.md](./in-memory-sql-database-specialist.md)

---

## Related Templates

### Primary Template

1. **`templates/service layer/lib/query.js.template`** (PRIMARY)
   - Complete AlaSQL implementation with reserved keyword mapping
   - Firestore Timestamp conversion to ISO strings
   - Nested object flattening with underscore-delimited paths
   - Dynamic schema generation from data structure
   - Database initialization and query execution

2. **`templates/service layer/lib/chat.js.template`**
   - OpenAI function calling integration with `query_data` function schema
   - Database initialization check before query execution
   - SQL query execution via LLM function calls

### Supporting Templates

3. **`templates/service layer/lib/databaseListeners.js.template`**
   - Real-time database synchronization with Firestore
   - Calls `refreshDatabase()` on collection changes

4. **`templates/service layer/firestore/sessions.js.template`**
   - Source of nested Firestore documents requiring flattening
   - Setup objects, arrays, and Timestamps

## Code Examples

### Example 1: Reserved Keyword Mapping

**DO** - Map reserved keywords at root level during flattening:

```javascript
const reservedKeywordMap = {
  'date': 'session_date',
  'temp': 'temperature',
  'session': 'session_type',
  'order': 'order_value',
  'group': 'group_value',
  'table': 'table_value',
  'key': 'key_value',
  'user': 'user_value',
  'index': 'index_value'
};

function flattenObject(obj, prefix = '') {
  const flattened = {};
  
  for (const [key, value] of Object.entries(obj)) {
    // Only rename at root level (no prefix)
    let safeName = key;
    if (!prefix && reservedKeywordMap[key.toLowerCase()]) {
      safeName = reservedKeywordMap[key.toLowerCase()];
    }
    
    const newKey = prefix ? `${prefix}_${safeName}` : safeName;
    flattened[newKey] = value;
  }
  
  return flattened;
}
```

**DON'T** - Skip keyword mapping (causes SQL syntax errors):

```javascript
// WRONG: Uses raw field names
const results = query('SELECT date, temp FROM sessions');
// Throws SQL syntax error - 'date' and 'temp' are reserved
```

### Example 2: Firestore Timestamp Conversion

**DO** - Detect and convert Firestore Timestamps to ISO strings:

```javascript
function flattenObject(obj, prefix = '') {
  const flattened = {};
  
  for (const [key, value] of Object.entries(obj)) {
    const newKey = prefix ? `${prefix}_${key}` : key;
    
    if (value === null || value === undefined) {
      flattened[newKey] = null;
    } else if (value instanceof Date) {
      flattened[newKey] = value.toISOString();
    } else if (typeof value === 'object' && value.seconds !== undefined) {
      // Handle Firestore Timestamp: { seconds: 1702656000, nanoseconds: 0 }
      flattened[newKey] = new Date(value.seconds * 1000).toISOString();
    } else if (typeof value === 'object' && !Array.isArray(value)) {
      Object.assign(flattened, flattenObject(value, newKey));
    } else if (Array.isArray(value)) {
      flattened[newKey] = JSON.stringify(value);
    } else {
      flattened[newKey] = value;
    }
  }
  
  return flattened;
}
```

**DON'T** - Store raw Timestamp objects:

```javascript
// WRONG: Stores Firestore Timestamp object directly
flattened[key] = value; // { seconds: 1702656000, nanoseconds: 0 }
// Query fails: WHERE createdAt > '2023-12-01' (object vs string)
```

### Example 3: Dynamic Schema Generation

**DO** - Infer column types from sample data:

```javascript
export async function initializeDatabase() {
  db = new alasql.Database();
  
  const sessions = await getUserSessions(true);
  
  if (sessions.length > 0) {
    const flatSessions = sessions.map(s => flattenObject(s));
    const sampleSession = flatSessions[0];
    
    const columns = Object.keys(sampleSession).map(key => {
      const value = sampleSession[key];
      let type = 'STRING';
      
      if (typeof value === 'number') {
        type = 'FLOAT';
      } else if (typeof value === 'boolean') {
        type = 'BOOLEAN';
      }
      
      return `${key} ${type}`;
    }).join(', ');
    
    db.exec(`CREATE TABLE sessions (${columns})`);
    db.exec('INSERT INTO sessions SELECT * FROM ?', [flatSessions]);
  }
  
  isInitialized = true;
}
```

**DON'T** - Use hardcoded schemas:

```javascript
// WRONG: Static schema fails when new fields added
db.exec(`CREATE TABLE sessions (
  id STRING,
  session_date STRING,
  temperature FLOAT
)`);
// Breaks if user adds custom fields
```

### Example 4: Database Initialization Guard

**DO** - Always check initialization before queries:

```javascript
export function query(sql, params = []) {
  if (!isInitialized) {
    throw new Error('Database not initialized. Call initializeDatabase() first.');
  }
  return db.exec(sql, params);
}

// In function handler
if (!isDatabaseInitialized()) {
  await initializeDatabase();
}
const results = query('SELECT * FROM sessions');
```

---

*This extended documentation is part of GuardKit's progressive disclosure system.*
