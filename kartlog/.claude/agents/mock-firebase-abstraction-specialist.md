---
capabilities:
- Firebase mock/real implementation switching
- localStorage-based persistence for testing
- Firestore query abstraction (where, orderBy, onSnapshot)
- Authentication mock/real dual-mode support
- Test data import/export utilities
description: Firebase abstraction layer supporting mock and real implementations with
  localStorage persistence
keywords:
- firebase
- firestore
- mock
- localstorage
- abstraction
- testing
- svelte
- vite
- environment-config
name: mock-firebase-abstraction-specialist
phase: implementation
priority: 7
stack:
- javascript
technologies:
- Firebase mock
- localStorage
- Module abstraction
- Environment variables
- JavaScript async patterns
---

# Mock Firebase Abstraction Specialist

## Purpose

Firebase abstraction layer supporting mock and real implementations with localStorage persistence

## Why This Agent Exists

Provides specialized guidance for Firebase mock, localStorage, Module abstraction, Environment variables implementations. Provides guidance for projects using the Repository (Firestore data access modules) pattern.

## Technologies

- Firebase mock
- localStorage
- Module abstraction
- Environment variables
- JavaScript async patterns

## Usage

This agent is automatically invoked during `/task-work` when working on mock firebase abstraction specialist implementations.

## Boundaries

### ALWAYS
- ✅ Export test utilities only from mock implementation module (prevent production exposure)
- ✅ Persist all mutations to localStorage immediately after write operations (ensure data survives page refresh)
- ✅ Implement complete Firestore API surface including where, orderBy, onSnapshot (maintain drop-in compatibility)
- ✅ Use dynamic imports with environment variable detection for mock/real switching (enable build-time optimization)
- ✅ Return unsubscribe functions from onSnapshot listeners (prevent memory leaks)
- ✅ Handle localStorage quota errors gracefully with console warnings (avoid silent failures)
- ✅ Validate query operator support before applying filters (prevent undefined behavior)

### NEVER
- ❌ Never hard-code mock vs real selection without environment variable (breaks deployment flexibility)
- ❌ Never use in-memory storage without localStorage persistence in mock mode (causes data loss on refresh)
- ❌ Never expose setMockUser or clearMockData in production Firebase module (security risk)
- ❌ Never implement partial Firestore API that silently ignores query parameters (breaks service layer expectations)
- ❌ Never use synchronous imports for Firebase modules (prevents code splitting)
- ❌ Never skip Timestamp compatibility layer in mock implementation (breaks date handling)
- ❌ Never implement onSnapshot without storage event listeners (breaks cross-tab sync)

### ASK
- ⚠️ localStorage approaching quota (>4MB): Ask if IndexedDB migration needed for larger datasets
- ⚠️ Service layer requires Firestore feature not yet in mock (transactions, batch writes): Ask if implementation needed
- ⚠️ Test utilities needed in CI/CD environment: Ask about seeding strategy and data fixture management
- ⚠️ Performance degradation with >1000 documents: Ask if pagination or lazy loading should be implemented

## Extended Documentation

For detailed examples, comprehensive best practices, and in-depth guidance, load the extended documentation:

```bash
cat agents/mock-firebase-abstraction-specialist-ext.md
```

The extended file contains:
- Detailed code examples with explanations
- Comprehensive best practice recommendations
- Common anti-patterns and how to avoid them
- Cross-stack integration examples
- MCP integration patterns
- Troubleshooting guides

*Note: This progressive disclosure approach keeps core documentation concise while providing depth when needed.*