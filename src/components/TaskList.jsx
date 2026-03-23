import React from 'react';
import './TaskList.css';

const PRIORITY_LABEL = { high: '↑ High', medium: '→ Med', low: '↓ Low' };

function TaskItem({ task, onToggle, onDelete }) {
  return (
    <li className={`task-item ${task.completed ? 'completed' : ''}`} data-testid="task-item">
      <button
        className="task-checkbox"
        onClick={() => onToggle(task.id)}
        aria-label={task.completed ? 'Mark incomplete' : 'Mark complete'}
        data-testid="task-checkbox"
      >
        {task.completed ? '✓' : ''}
      </button>

      <span className="task-title">{task.title}</span>

      <span className={`task-priority priority-${task.priority}`} data-testid="task-priority">
        {PRIORITY_LABEL[task.priority] || task.priority}
      </span>

      <button
        className="task-delete"
        onClick={() => onDelete(task.id)}
        aria-label="Delete task"
        data-testid="task-delete"
      >
        ×
      </button>
    </li>
  );
}

function TaskList({ tasks, onToggle, onDelete }) {
  if (tasks.length === 0) {
    return (
      <div className="task-empty" data-testid="task-empty">
        <span className="empty-icon">◎</span>
        <p>No tasks yet. Add one above!</p>
      </div>
    );
  }

  return (
    <ul className="task-list" data-testid="task-list">
      {tasks.map(task => (
        <TaskItem
          key={task.id}
          task={task}
          onToggle={onToggle}
          onDelete={onDelete}
        />
      ))}
    </ul>
  );
}

export default TaskList;
