# AI Code Review Guide

You've just used Claude Code or Codex to generate a component for your Kanban board - perhaps a new task creation form. You've followed IQRE: **Iterated** on the requirements, **Questioned** the LLM's approach, and now you've **Accepted** the generated code. But before committing to your repository, you need to **Review** it thoroughly.

This is different from reviewing human-written code. AI confidently generates both brilliant solutions and subtle bugs with equal enthusiasm. Your job is to catch what AI missed.

## The two-phase review process

### Phase 1: Functional validation

**Does it actually work as intended?**

1. **Test the happy path** - Create a task, move it between columns, edit it
2. **Test edge cases** - What happens with empty inputs? Very long task names? Special characters?
3. **Check unintended behaviour** - Does it do anything you didn't discuss?

```javascript
// You asked for a simple task form, but AI added:
const handleSubmit = async (formData) => {
  // ✅ Expected: basic form submission
  await createTask(formData);

  // 🤔 Unexpected: auto-assigns to current user
  formData.assignedTo = currentUser.id;

  // 🚨 Concerning: sends analytics without consent
  analytics.track("task_created", formData);
};
```

**When you find unexpected behaviour, return to Iterate/Question:**

- "Why did you add user assignment? I didn't ask for that."
- "The analytics tracking wasn't in our requirements - explain this decision."

### Phase 2: Code comprehension

**Do you understand every line?**

Following Simon Willison's principle: "Never commit code you couldn't explain to somebody else."

Read through methodically and ask yourself:

- What does this function do?
- Why was this approach chosen?
- How does it integrate with existing code?
- Are there any security implications?

## AI-specific patterns to watch for

### The "tutorial code" anti-pattern

AI often generates code that works in isolation but fails in production:

```javascript
// 🚨 AI's first attempt - no error handling
const saveTask = async (task) => {
  const response = await fetch("/api/tasks", {
    method: "POST",
    body: JSON.stringify(task),
  });
  return response.json();
};

// ✅ After your review and iteration
const saveTask = async (task) => {
  try {
    const response = await fetch("/api/tasks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(task),
    });

    if (!response.ok) {
      throw new Error(`Failed to save task: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Task save failed:", error);
    throw error;
  }
};
```

### The "kitchen sink" anti-pattern

AI includes unnecessary complexity:

```javascript
// 🚨 Over-engineered for a simple Kanban board
class TaskStateManagerFactory {
  constructor(config) {
    this.observers = [];
    this.middleware = [];
    this.reducers = new Map();
  }

  createManager() {
    return new TaskStateManager(this.config);
  }
}

// ✅ What you actually need
const [tasks, setTasks] = useState([]);
```

### The "inconsistent patterns" anti-pattern

Mixed approaches within the same codebase:

```javascript
// 🚨 The AI used different patterns for similar functions
function addTask(task) {
  return { type: "ADD_TASK", payload: task }; // Redux pattern
}

function updateTask(id, changes) {
  setTasks((prev) =>
    prev.map(
      (
        t // React state pattern
      ) => (t.id === id ? { ...t, ...changes } : t)
    )
  );
}

function deleteTask(taskId) {
  fetch(`/api/tasks/${taskId}`, { method: "DELETE" }) // Direct API call
    .then(() => loadTasks());
}
```

### The "anti-modular spaghetti" anti-pattern

> [!NOTE]
> For those practicing WET principles, move along, nothing to see here.

AI loves to generate massive functions that repeat similar logic instead of extracting reusable utilities:

```javascript
// 🚨 AI generated separate functions for each status change
function moveTaskToInProgress(taskId) {
  const task = tasks.find((t) => t.id === taskId);
  if (task && task.status === "todo") {
    task.status = "in-progress";
    task.updatedAt = new Date().toISOString();
    task.updatedBy = getCurrentUser().id;
    saveTask(task);
    updateUI();
    logActivity("task_moved", { taskId, from: "todo", to: "in-progress" });
    sendNotification(task.assignee, "Task moved to in progress");
  }
}

function moveTaskToCompleted(taskId) {
  const task = tasks.find((t) => t.id === taskId);
  if (task && task.status === "in-progress") {
    task.status = "completed";
    task.updatedAt = new Date().toISOString();
    task.updatedBy = getCurrentUser().id;
    task.completedAt = new Date().toISOString();
    saveTask(task);
    updateUI();
    logActivity("task_moved", { taskId, from: "in-progress", to: "completed" });
    sendNotification(task.assignee, "Task completed");
  }
}

function moveTaskToTodo(taskId) {
  const task = tasks.find((t) => t.id === taskId);
  if (task && (task.status === "in-progress" || task.status === "completed")) {
    const oldStatus = task.status;
    task.status = "todo";
    task.updatedAt = new Date().toISOString();
    task.updatedBy = getCurrentUser().id;
    if (task.completedAt) task.completedAt = null;
    saveTask(task);
    updateUI();
    logActivity("task_moved", { taskId, from: oldStatus, to: "todo" });
    sendNotification(task.assignee, "Task moved back to todo");
  }
}

// ✅ DRY principle applied - one function handles all moves
function moveTask(taskId, newStatus) {
  const task = tasks.find((t) => t.id === taskId);
  if (!task || !isValidStatusTransition(task.status, newStatus)) return;

  const oldStatus = task.status;
  updateTaskStatus(task, newStatus);
  saveTask(task);
  updateUI();
  logActivity("task_moved", { taskId, from: oldStatus, to: newStatus });
  sendNotification(task.assignee, `Task moved to ${newStatus}`);
}
```

### The "deprecated patterns" anti-pattern

AI knowledge has a cutoff date and may suggest outdated approaches:

```javascript
// 🚨 AI suggested deprecated React patterns
class TaskComponent extends React.Component {
  componentWillMount() {  // Deprecated since React 16.3
    this.loadTasks();
  }

  render() {
    return <div>{this.renderTasks()}</div>;
  }
}

// 🚨 Old Next.js routing
export default function TaskPage() {
  const router = useRouter();
  const { id } = router.query;  // Pre-App Router approach
}

// ✅ Modern approaches
function TaskComponent() {
  useEffect(() => {
    loadTasks();
  }, []);

  return <div>{renderTasks()}</div>;
}

// Modern Next.js App Router
export default function TaskPage({ params }) {
  const { id } = params;  // App Router approach
}
```

### The "hallucinated dependencies" anti-pattern

AI may invent packages or methods that don't exist:

```javascript
// 🚨 Non-existent packages AI confidently suggested
import { validateTask } from "react-task-validator"; // Doesn't exist
import { KanbanBoard } from "@material-ui/kanban"; // Not a real package
import { useTaskState } from "redux-task-hooks"; // Made up

// 🚨 Non-existent methods
tasks.sortByPriority(); // Array.prototype.sortByPriority doesn't exist
element.fadeInOut(500); // Not a DOM method
database.findTasksOptimised(); // Custom method that doesn't exist in your DB layer
```

**Red flag**: If you don't recognise a package or method, **be suspicious**. Check:

- Does this package exist on npm?
- Is this method documented in the official docs?
- Does this API exist in your codebase?

### The "hardcoded playground" anti-pattern

AI often includes mocked data to make examples work:

```javascript
// 🚨 Hardcoded data that won't work in real scenarios
const TaskList = () => {
  const [tasks, setTasks] = useState([
    { id: 1, title: "Fix bug", status: "todo", assignee: "john@example.com" },
    {
      id: 2,
      title: "Add feature",
      status: "in-progress",
      assignee: "jane@example.com",
    },
    {
      id: 3,
      title: "Review code",
      status: "completed",
      assignee: "bob@example.com",
    },
  ]);

  // Hardcoded user that may not exist
  const currentUser = {
    id: "user123",
    name: "John Doe",
    email: "john@example.com",
  };

  // Fixed API endpoint that might not match your backend
  const API_BASE = "http://localhost:3000/api";

  return (
    <div>
      {tasks.map((task) => (
        <TaskCard key={task.id} task={task} />
      ))}
    </div>
  );
};

// ✅ Production-ready approach
const TaskList = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const currentUser = useAuth();
  const API_BASE = process.env.NEXT_PUBLIC_API_URL;

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/tasks`);
      if (!response.ok) throw new Error("Failed to load tasks");
      const data = await response.json();
      setTasks(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  if (tasks.length === 0) return <EmptyState />;

  return (
    <div>
      {tasks.map((task) => (
        <TaskCard key={task.id} task={task} />
      ))}
    </div>
  );
};
```

## Security review checklist

AI-generated code has a 40-48% higher vulnerability rate than human code. Check for:

### Input validation

```javascript
// 🚨 No validation
const createTask = (title, description) => {
  database.query(
    `INSERT INTO tasks (title, description) VALUES ('${title}', '${description}')`
  );
};

// ✅ Proper validation and parameterisation
const createTask = (title, description) => {
  if (!title || title.length > 100) {
    throw new Error("Invalid title");
  }
  return database.query(
    "INSERT INTO tasks (title, description) VALUES (?, ?)",
    [title, description]
  );
};
```

### XSS vulnerabilities

```javascript
// 🚨 Dangerous innerHTML usage
taskElement.innerHTML = `<h3>${task.title}</h3><p>${task.description}</p>`;

// ✅ Safe text content
taskElement.querySelector(".title").textContent = task.title;
taskElement.querySelector(".description").textContent = task.description;
```

### Authentication issues

```javascript
// 🚨 Missing access control
app.delete("/api/tasks/:id", (req, res) => {
  deleteTask(req.params.id);
});

// ✅ Proper authentication
app.delete("/api/tasks/:id", authenticateUser, (req, res) => {
  if (!canUserDeleteTask(req.user, req.params.id)) {
    return res.status(403).json({ error: "Forbidden" });
  }
  deleteTask(req.params.id);
});
```

## Architectural alignment check

Does the code follow your project's established patterns?

### Component structure

```javascript
// 🚨 AI created inconsistent component structure
function TaskCard({ task }) {
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState(task.title);
  // Inline state management when you're using a store elsewhere
}

// ✅ Follows your established patterns
function TaskCard({ task, onUpdate }) {
  const dispatch = useAppDispatch(); // Consistent with other components
  const isEditing = useSelector((state) => state.ui.editingTask === task.id);
}
```

### Error handling consistency

```javascript
// 🚨 Mixed error handling approaches
try {
  await saveTask(task);
} catch (error) {
  console.error(error); // Different from rest of app
}

// ✅ Consistent with your error handling pattern
try {
  await saveTask(task);
} catch (error) {
  showNotification("error", "Failed to save task");
  reportError(error);
}
```

## Common questions to ask during review

### About the approach

- "Why did the LLM choose this library/pattern over alternatives?"
- "Is this the simplest solution that could work?"
- "Does this fit with our existing architecture?"

### About edge cases

- "What happens if the API is down?"
- "How does this handle empty or invalid data?"
- "What if a user tries to abuse this feature?"

### About maintainability

- "Will another developer understand this in 6 months?"
- "How easy would it be to modify this feature?"
- "Are there any hidden dependencies or side effects?"

## When to iterate back with AI

Return to the **Iterate/Question** phase when you find:

1. **Security vulnerabilities** - "This code is vulnerable to XSS. How should we fix it?"
2. **Architecture misalignment** - "This doesn't follow our Redux patterns. Can you refactor it?"
3. **Missing requirements** - "We need error handling for network failures."
4. **Over-engineering** - "This seems complex for our needs. Can you simplify?"
5. **Inconsistent patterns** - "Use the same error handling approach as our other components."

## The final check

Before committing, ensure you can answer:

- **What does this code do?** (in plain English)
- **Why was this approach chosen?** (architectural fit)
- **How does it handle errors?** (resilience)
- **What could go wrong?** (security and edge cases)
- **How does it integrate?** (system-wide impact)

Remember: AI generated it, but **you're responsible for it**. If you can't confidently explain every line to a colleague, dig deeper or iterate with the LLM until you can.

The goal isn't perfect code - it's code you understand, trust, and can maintain. AI tools help you move faster, but thorough review ensures you don't sacrifice quality for speed.
