# Ai Llm Function Calling Specialist - Extended Documentation

This file contains detailed examples, best practices, and in-depth guidance for the **ai-llm-function-calling-specialist** agent.

**Core documentation**: See [ai-llm-function-calling-specialist.md](./ai-llm-function-calling-specialist.md)

---

## Related Templates

### Primary Templates

**`templates/service layer/lib/chat.js.template`** - Core function calling implementation
- Defines OpenAI function schemas for `get_user_tyres` and `query_data`
- Implements multi-turn execution loop with automatic function dispatch
- Shows system prompt engineering with schema documentation
- Demonstrates structured error handling for function results

**`templates/service layer/lib/query.js.template`** - SQL query execution engine
- In-memory database initialization with AlaSQL
- Dynamic table creation from nested JSON objects
- Reserved keyword mapping to prevent SQL syntax errors
- Type inference for column definitions

**`templates/testing/test/test_chat_deepeval.py.template`** - LLM output validation
- DeepEval test cases for function calling behavior
- GEval metrics for semantic correctness
- Threshold-based assertion framework for non-deterministic outputs

### Supporting Templates

**`templates/service layer/firestore/sessions.js.template`** - Data source for SQL aggregation
- Provides session data structure consumed by `query_data` function

**`templates/presentation/routes/Chat.svelte.template`** - UI integration
- Shows client-side streaming and function call visualization

## Code Examples

### Example 1: Defining Function Schemas

**DO** - Use detailed descriptions with context about data sources and constraints:

```javascript
const functions = [
  {
    name: 'query_data',
    description: 'Execute SQL queries on the user\'s karting data using an in-memory database. Available tables: sessions, tyres, engines, chassis, tracks. Reserved keywords renamed: session_date (not date), temperature (not temp), session_type (not session).',
    parameters: {
      type: 'object',
      properties: {
        sql: {
          type: 'string',
          description: 'The SQL query to execute. Must be valid SQL syntax.'
        }
      },
      required: ['sql']
    }
  }
];
```

### Example 2: Multi-Turn Function Execution Loop

**DO** - Implement a loop that handles multiple sequential function calls:

```javascript
export async function sendChatMessage(messages, onChunk, onComplete, apiKey = null) {
  const openai = createOpenAIClient(apiKey);

  while (true) {
    const response = await openai.chat.completions.create({
      model: 'gpt-4o',
      messages: messages,
      functions: functions,
      function_call: 'auto'
    });

    const assistantMessage = response.choices[0].message;

    if (assistantMessage.function_call) {
      const functionName = assistantMessage.function_call.name;
      const functionArgs = JSON.parse(assistantMessage.function_call.arguments);
      const functionResult = await executeFunctionCall(functionName, functionArgs);
      
      messages.push(assistantMessage);
      messages.push({
        role: 'function',
        name: functionName,
        content: JSON.stringify(functionResult)
      });
      continue;
    }

    return { role: 'assistant', content: assistantMessage.content };
  }
}
```

### Example 3: Function Implementation with Structured Error Handling

**DO** - Return consistent result structure with success/error fields:

```javascript
async function executeFunctionCall(functionName, functionArgs) {
  if (functionName === 'query_data') {
    try {
      if (!isDatabaseInitialized()) {
        await initializeDatabase();
        startDatabaseListeners();
      }
      const results = query(functionArgs.sql);
      return {
        success: true,
        data: results,
        rowCount: results.length,
        sql: functionArgs.sql
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        sql: functionArgs.sql
      };
    }
  }
  return { success: false, error: 'Unknown function' };
}
```

### Example 4: Dynamic SQL Schema from Nested Objects

**DO** - Flatten nested objects and handle reserved keywords:

```javascript
const reservedKeywordMap = {
  'date': 'session_date',
  'temp': 'temperature',
  'session': 'session_type'
};

function flattenObject(obj, prefix = '') {
  const flattened = {};
  for (const [key, value] of Object.entries(obj)) {
    let safeName = key;
    if (!prefix && reservedKeywordMap[key.toLowerCase()]) {
      safeName = reservedKeywordMap[key.toLowerCase()];
    }
    const fullKey = prefix ? `${prefix}_${safeName}` : safeName;
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      Object.assign(flattened, flattenObject(value, fullKey));
    } else {
      flattened[fullKey] = value;
    }
  }
  return flattened;
}
```

### Example 5: LLM Output Validation with DeepEval

**DO** - Use semantic metrics for non-deterministic LLM outputs:

```python
from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

def test_sql_function_calling():
    user_input = "What was my average lap time at Daytona?"
    actual_output = run_chat(user_input)
    
    test_case = LLMTestCase(input=user_input, actual_output=actual_output)
    correctness_metric = GEval(
        name="SQL Query Usage",
        criteria="The response must indicate SQL query was executed with aggregate statistics.",
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
        threshold=0.8
    )
    assert_test(test_case, [correctness_metric])
```

---

*This extended documentation is part of GuardKit's progressive disclosure system.*
