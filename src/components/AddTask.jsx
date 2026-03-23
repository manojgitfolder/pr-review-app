import React, { useState } from 'react';
import './AddTask.css';

function AddTask({ onAdd }) {
  const [title, setTitle] = useState('');
  const [priority, setPriority] = useState('medium');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title.trim()) {
      setError('Task title cannot be empty');
      return;
    }
    const success = onAdd(title, priority);
    if (success) {
      setTitle('');
      setPriority('medium');
      setError('');
    }
  };

  return (
    <form className="add-task-form" onSubmit={handleSubmit} data-testid="add-task-form">
      <div className="form-row">
        <input
          className={`task-input ${error ? 'has-error' : ''}`}
          type="text"
          placeholder="Add a new task..."
          value={title}
          onChange={e => { setTitle(e.target.value); setError(''); }}
          data-testid="task-input"
          aria-label="Task title"
        />
        <select
          className="priority-select"
          value={priority}
          onChange={e => setPriority(e.target.value)}
          data-testid="priority-select"
          aria-label="Task priority"
        >
          <option value="high">↑ High</option>
          <option value="medium">→ Med</option>
          <option value="low">↓ Low</option>
        </select>
        <button type="submit" className="add-btn" data-testid="add-btn" aria-label="Add task">
          + Add
        </button>
      </div>
      {error && <p className="form-error" data-testid="form-error">{error}</p>}
    </form>
  );
}

export default AddTask;
