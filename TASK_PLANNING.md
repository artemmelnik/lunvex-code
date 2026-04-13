# Task Planning System for LunVex Code

## 🎯 Overview

The Task Planning System is an intelligent feature that automatically decomposes complex coding tasks into manageable subtasks. This solves the problem of limited context windows by breaking down large tasks into smaller, focused operations that can be executed sequentially.

## ✨ Features

### 1. **Automatic Task Decomposition**
- Analyzes task complexity using heuristics and LLM analysis
- Breaks down complex tasks into 3-7 manageable subtasks
- Identifies dependencies between subtasks
- Creates optimal execution order

### 2. **Context Management**
- Maintains shared context between subtasks
- Passes relevant information from completed subtasks to subsequent ones
- Truncates long results to prevent context overflow
- Tracks file dependencies and tool requirements

### 3. **Intelligent Planning**
- Uses LLM to analyze task requirements
- Identifies needed files and tools for each subtask
- Creates clear expected outputs for each subtask
- Handles circular dependency detection

### 4. **Flexible Execution**
- Works with both sync and async agents
- Can be enabled/disabled per task
- Provides detailed execution summaries
- Graceful error handling and recovery

## 🚀 How It Works

### Task Complexity Detection
The system uses multiple heuristics to determine if a task needs decomposition:

1. **Keyword analysis**: Tasks with "and", "then", "after", "also", "next", "first", "second", "finally"
2. **File mentions**: Tasks mentioning multiple files or modules
3. **Length**: Tasks longer than 50 words
4. **Structure**: Tasks with clear sequential steps or phases

### Planning Process

```python
# 1. Analyze task
analysis = planner._analyze_task_dependencies(task)
# Returns: files_needed, tools_needed, phases, dependencies

# 2. Generate subtasks
subtasks = planner._generate_subtasks(task, analysis)
# Creates 3-7 focused subtasks with clear dependencies

# 3. Calculate execution order
execution_order = planner._calculate_execution_order(subtasks)
# Topological sort based on dependencies

# 4. Execute sequentially
for subtask_id in execution_order:
    context = prepare_context(subtask, shared_context)
    result = agent.execute(subtask_prompt)
    update_shared_context(result, shared_context)
```

### Example: Complex Task Decomposition

**Original Task:**
```
"First analyze the authentication system in auth.py to find security vulnerabilities, then fix any issues found, update the user model in models.py to add two-factor authentication support, and finally write tests for the new functionality."
```

**Decomposed Subtasks:**
1. **analyze_auth**: Read and analyze auth.py for security vulnerabilities
2. **fix_auth**: Fix identified security issues in auth.py
3. **update_models**: Update models.py to add 2FA support
4. **write_tests**: Write tests for authentication and 2FA functionality

**Dependencies:**
- `fix_auth` depends on `analyze_auth`
- `write_tests` depends on `fix_auth` and `update_models`

## 🛠️ Usage

### Command Line

```bash
# Enable task planning (default for complex tasks)
lunvex-code run "Refactor the entire authentication system"

# Disable task planning for a specific task
lunvex-code run --no-planning "Simple file read operation"

# Async mode with planning
lunvex-code run-async "Migrate from Flask to FastAPI"
```

### Programmatic Usage

```python
from lunvex_code import create_agent
from lunvex_code.task_planner import create_task_planner

# Create agent
agent = create_agent()

# Complex task with automatic planning
result = agent.run(
    "Implement user authentication with JWT tokens and refresh mechanism",
    use_planning=True  # Default is True
)

# Simple task without planning
result = agent.run(
    "Read the README.md file",
    use_planning=False
)
```

### Async Usage

```python
from lunvex_code.async_agent import AsyncAgent
from lunvex_code.task_planner import TaskPlanner

async def complex_task():
    agent = AsyncAgent()
    planner = TaskPlanner(agent.client, agent.registry)
    
    task = "Build a complete REST API with CRUD operations for users and posts"
    plan = planner.create_task_plan(task)
    
    result = await planner.execute_plan_async(plan, agent)
    return result
```

## 📊 Configuration

### Environment Variables

```bash
# Enable/disable task planning globally
export LUNVEX_TASK_PLANNING=true  # Default: true

# Minimum task length for planning (words)
export LUNVEX_MIN_TASK_LENGTH=30  # Default: 30

# Maximum subtasks per plan
export LUNVEX_MAX_SUBTASKS=7  # Default: 7
```

### Programmatic Configuration

```python
from lunvex_code.agent import AgentConfig

config = AgentConfig(
    max_turns=50,
    trust_mode=False,
    yolo_mode=False,
    verbose=False,
    # Task planning is enabled by default
    # Can be controlled per-task with use_planning parameter
)

agent = Agent(client, context, config)
```

## 🧪 Examples

### Example 1: Multi-file Refactoring

```bash
lunvex-code run "Rename all occurrences of 'User' to 'Customer' in models.py, services.py, and controllers.py, then update the database schema accordingly"
```

**Plan created:**
1. Analyze files to understand User usage patterns
2. Update models.py with Customer class
3. Update services.py with Customer service logic
4. Update controllers.py with Customer endpoints
5. Update database schema migration
6. Verify all changes work together

### Example 2: Feature Implementation

```bash
lunvex-code run "Add file upload functionality with S3 storage, create API endpoints for upload/download, add file validation, and update documentation"
```

**Plan created:**
1. Analyze current architecture and S3 integration requirements
2. Implement S3 client and file storage service
3. Create upload/download API endpoints
4. Add file validation (size, type, security)
5. Update API documentation
6. Write tests for file upload functionality

## 🔧 Advanced Features

### 1. **Custom Task Analysis**
Override the default analysis logic:

```python
class CustomTaskPlanner(TaskPlanner):
    def _is_complex_task(self, task: str) -> bool:
        # Custom complexity detection
        if "urgent" in task.lower():
            return True  # Always plan urgent tasks
        return super()._is_complex_task(task)
```

### 2. **Manual Task Planning**
Create plans manually for specific workflows:

```python
from lunvex_code.task_planner import Subtask, TaskPlan

# Create custom subtasks
subtasks = [
    Subtask(
        id="setup",
        description="Set up project structure",
        dependencies=[],
        expected_output="Project structure created",
        context_files=[],
        tools_needed=["bash", "write_file"]
    ),
    Subtask(
        id="implement",
        description="Implement core functionality",
        dependencies=["setup"],
        expected_output="Core features implemented",
        context_files=["src/main.py"],
        tools_needed=["read_file", "edit_file"]
    )
]

# Create and execute plan
plan = TaskPlan(
    original_task="Custom project setup",
    subtasks=subtasks,
    execution_order=["setup", "implement"]
)

result = planner.execute_plan(plan, agent)
```

### 3. **Context Sharing Strategies**
Control how context is shared between subtasks:

```python
# Override context preparation
def custom_prepare_context(self, subtask, shared_context):
    # Only share essential information
    essential = {
        "completed_tasks": [k for k, v in shared_context.items() if v.get("completed")],
        "critical_errors": shared_context.get("errors", [])
    }
    return json.dumps(essential)
```

## 📈 Performance Benefits

### 1. **Reduced Context Overflow**
- Subtasks focus on specific files/operations
- Shared context is truncated and summarized
- Each subtask fits within LLM context limits

### 2. **Better Error Handling**
- Failures are isolated to specific subtasks
- Can continue execution after non-critical failures
- Clear error reporting per subtask

### 3. **Improved Planning**
- LLM has clearer focus for each subtask
- Dependencies ensure logical execution order
- Expected outputs provide clear success criteria

### 4. **Enhanced Debugging**
- Can see which subtask failed
- Understand dependencies between failures
- Isolate and fix specific issues

## 🚨 Limitations and Considerations

### 1. **Overhead**
- Additional LLM calls for planning
- Context management overhead
- May not be needed for simple tasks

### 2. **Dependency Complexity**
- Circular dependencies must be avoided
- Complex dependency graphs can be challenging
- Some tasks may have ambiguous dependencies

### 3. **Context Loss**
- Summarization may lose important details
- Very complex tasks may still exceed context
- Balance between detail and brevity

### 4. **LLM Reliability**
- Planning depends on LLM analysis quality
- May generate unrealistic or incomplete plans
- Fallback mechanisms handle poor planning

## 🔮 Future Enhancements

### Planned Features:
1. **Learning from execution**: Improve planning based on past task executions
2. **Parallel execution**: Execute independent subtasks in parallel
3. **Resource estimation**: Estimate time/complexity for each subtask
4. **Interactive planning**: Allow user review and modification of plans
5. **Template-based planning**: Use predefined templates for common tasks

### Research Areas:
- Optimal subtask size and granularity
- Context compression techniques
- Dependency prediction accuracy
- Failure recovery strategies

## 📚 Best Practices

### When to Use Task Planning:
- ✅ Tasks involving multiple files/modules
- ✅ Sequential operations (first X, then Y, finally Z)
- ✅ Complex refactoring or migration tasks
- ✅ Feature implementation with multiple components
- ✅ Tasks longer than 50 words

### When to Disable Task Planning:
- ❌ Simple file operations (read, write single file)
- ❌ Quick analysis or search tasks
- ❌ Tasks with immediate, single-step solutions
- ❌ When maximum speed is required
- ❌ For well-understood, routine operations

### Optimization Tips:
1. **Be specific in task descriptions**: Clear tasks lead to better plans
2. **Use --no-planning for simple tasks**: Avoid overhead for trivial operations
3. **Review generated plans**: Ensure dependencies make sense
4. **Monitor context usage**: Adjust subtask granularity if needed
5. **Provide file hints**: Mention specific files to improve planning accuracy

## 🎉 Conclusion

The Task Planning System transforms LunVex Code from a simple coding assistant into a sophisticated project management tool. By intelligently decomposing complex tasks, it enables handling of large-scale refactoring, multi-file updates, and comprehensive feature implementations that would otherwise exceed context limits.

The system balances automation with flexibility, providing sensible defaults while allowing customization for specific needs. As the system evolves, it will continue to improve its planning accuracy, execution efficiency, and ability to handle increasingly complex software development tasks.

**Key Benefits:**
- 🚀 Handle tasks that exceed LLM context limits
- 🎯 Focused execution on specific subtasks
- 🔗 Clear dependency management
- 📊 Comprehensive progress tracking
- 🛡️ Isolated error handling and recovery

Start using task planning today to tackle your most complex coding challenges with confidence!