import React, { useState } from 'react';
import './App.css';
import TaskList from './components/TaskList';
import AddTask from './components/AddTask';

function App() {
  const [tasks, setTasks] = useState([
    { id: 1, title: 'Setup project', completed: true, priority: 'high' },
    { id: 2, title: 'Write unit tests', completed: false, priority: 'high' },
    { id: 3, title: 'Configure CI/CD', completed: false, priority: 'medium' },
  ]);

  const addTask = (title, priority = 'medium') => {
    if (!title.trim()) return false;
    const newTask = {
      id: Date.now(),
      title: title.trim(),
      completed: false,
      priority,
    };
    setTasks(prev => [...prev, newTask]);
    return true;
  };

  const toggleTask = (id) => {
    setTasks(prev =>
      prev.map(task =>
        task.id === id ? { ...task, completed: !task.completed } : task
      )
    );
  };

  const deleteTask = (id) => {
    setTasks(prev => prev.filter(task => task.id !== id));
  };

  const completedCount = tasks.filter(t => t.completed).length;
  const totalCount = tasks.length;

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title">
            <span className="title-icon">◈</span>
            TaskFlow
          </h1>
          <div className="progress-badge">
            <span className="progress-text">{completedCount}/{totalCount}</span>
            <span className="progress-label">done</span>
          </div>
        </div>
        <div className="progress-bar-container">
          <div
            className="progress-bar-fill"
            style={{ width: totalCount ? `${(completedCount / totalCount) * 100}%` : '0%' }}
          />
        </div>
      </header>

      <main className="app-main">
        <AddTask onAdd={addTask} />
        <TaskList
          tasks={tasks}
          onToggle={toggleTask}
          onDelete={deleteTask}
        />
      </main>
    </div>
  );
}

export default App;
