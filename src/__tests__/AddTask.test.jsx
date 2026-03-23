import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import AddTask from '../../components/AddTask';

describe('AddTask Component', () => {
  test('renders input and add button', () => {
    render(<AddTask onAdd={jest.fn()} />);
    expect(screen.getByTestId('task-input')).toBeInTheDocument();
    expect(screen.getByTestId('add-btn')).toBeInTheDocument();
    expect(screen.getByTestId('priority-select')).toBeInTheDocument();
  });

  test('calls onAdd with title and priority on submit', () => {
    const onAdd = jest.fn().mockReturnValue(true);
    render(<AddTask onAdd={onAdd} />);

    fireEvent.change(screen.getByTestId('task-input'), { target: { value: 'My new task' } });
    fireEvent.change(screen.getByTestId('priority-select'), { target: { value: 'high' } });
    fireEvent.click(screen.getByTestId('add-btn'));

    expect(onAdd).toHaveBeenCalledWith('My new task', 'high');
  });

  test('shows error when submitting empty input', () => {
    render(<AddTask onAdd={jest.fn()} />);
    fireEvent.click(screen.getByTestId('add-btn'));
    expect(screen.getByTestId('form-error')).toBeInTheDocument();
    expect(screen.getByText('Task title cannot be empty')).toBeInTheDocument();
  });

  test('does not call onAdd with empty input', () => {
    const onAdd = jest.fn();
    render(<AddTask onAdd={onAdd} />);
    fireEvent.click(screen.getByTestId('add-btn'));
    expect(onAdd).not.toHaveBeenCalled();
  });

  test('clears input after successful add', () => {
    const onAdd = jest.fn().mockReturnValue(true);
    render(<AddTask onAdd={onAdd} />);
    const input = screen.getByTestId('task-input');
    fireEvent.change(input, { target: { value: 'Task to clear' } });
    fireEvent.click(screen.getByTestId('add-btn'));
    expect(input.value).toBe('');
  });

  test('clears error message when user starts typing', () => {
    render(<AddTask onAdd={jest.fn()} />);
    fireEvent.click(screen.getByTestId('add-btn'));
    expect(screen.getByTestId('form-error')).toBeInTheDocument();

    fireEvent.change(screen.getByTestId('task-input'), { target: { value: 'a' } });
    expect(screen.queryByTestId('form-error')).not.toBeInTheDocument();
  });

  test('default priority is medium', () => {
    render(<AddTask onAdd={jest.fn()} />);
    expect(screen.getByTestId('priority-select').value).toBe('medium');
  });

  test('handles whitespace-only input as empty', () => {
    const onAdd = jest.fn();
    render(<AddTask onAdd={onAdd} />);
    fireEvent.change(screen.getByTestId('task-input'), { target: { value: '   ' } });
    fireEvent.click(screen.getByTestId('add-btn'));
    expect(onAdd).not.toHaveBeenCalled();
    expect(screen.getByTestId('form-error')).toBeInTheDocument();
  });
});
