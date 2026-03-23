import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi } from 'vitest';
import TaskList from '../components/TaskList';

const mockTasks = [
  { id: 1, title: 'Task One', completed: false, priority: 'high' },
  { id: 2, title: 'Task Two', completed: true, priority: 'medium' },
  { id: 3, title: 'Task Three', completed: false, priority: 'low' },
];

describe('TaskList Component', () => {
  test('renders all tasks', () => {
    render(<TaskList tasks={mockTasks} onToggle={vi.fn()} onDelete={vi.fn()} />);
    expect(screen.getByText('Task One')).toBeInTheDocument();
    expect(screen.getByText('Task Two')).toBeInTheDocument();
    expect(screen.getByText('Task Three')).toBeInTheDocument();
  });

  test('shows empty state when no tasks', () => {
    render(<TaskList tasks={[]} onToggle={vi.fn()} onDelete={vi.fn()} />);
    expect(screen.getByTestId('task-empty')).toBeInTheDocument();
    expect(screen.getByText('No tasks yet. Add one above!')).toBeInTheDocument();
  });

  test('displays priority badges correctly', () => {
    render(<TaskList tasks={mockTasks} onToggle={vi.fn()} onDelete={vi.fn()} />);
    expect(screen.getByText('↑ High')).toBeInTheDocument();
    expect(screen.getByText('→ Med')).toBeInTheDocument();
    expect(screen.getByText('↓ Low')).toBeInTheDocument();
  });

  test('calls onToggle with correct id when checkbox clicked', () => {
    const onToggle = vi.fn();
    render(<TaskList tasks={mockTasks} onToggle={onToggle} onDelete={vi.fn()} />);
    const checkboxes = screen.getAllByTestId('task-checkbox');
    fireEvent.click(checkboxes[0]);
    expect(onToggle).toHaveBeenCalledWith(1);
  });

  test('calls onDelete with correct id when delete clicked', () => {
    const onDelete = vi.fn();
    render(<TaskList tasks={mockTasks} onToggle={vi.fn()} onDelete={onDelete} />);
    const deleteButtons = screen.getAllByTestId('task-delete');
    fireEvent.click(deleteButtons[1]);
    expect(onDelete).toHaveBeenCalledWith(2);
  });

  test('applies completed class to completed tasks', () => {
    render(<TaskList tasks={mockTasks} onToggle={vi.fn()} onDelete={vi.fn()} />);
    const items = screen.getAllByTestId('task-item');
    expect(items[1]).toHaveClass('completed');
    expect(items[0]).not.toHaveClass('completed');
  });
});
