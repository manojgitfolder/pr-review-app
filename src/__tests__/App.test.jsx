import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../App';

describe('App Component', () => {
  test('renders the app title', () => {
    render(<App />);
    expect(screen.getByText('TaskFlow')).toBeInTheDocument();
  });

  test('shows initial tasks', () => {
    render(<App />);
    expect(screen.getByText('Setup project')).toBeInTheDocument();
    expect(screen.getByText('Write unit tests')).toBeInTheDocument();
    expect(screen.getByText('Configure CI/CD')).toBeInTheDocument();
  });

  test('displays correct progress count', () => {
    render(<App />);
    // 1 of 3 tasks completed initially
    expect(screen.getByText('1/3')).toBeInTheDocument();
  });

  test('adds a new task', () => {
    render(<App />);
    const input = screen.getByTestId('task-input');
    const addBtn = screen.getByTestId('add-btn');

    fireEvent.change(input, { target: { value: 'New test task' } });
    fireEvent.click(addBtn);

    expect(screen.getByText('New test task')).toBeInTheDocument();
  });

  test('progress updates after adding a task', () => {
    render(<App />);
    const input = screen.getByTestId('task-input');
    const addBtn = screen.getByTestId('add-btn');

    fireEvent.change(input, { target: { value: 'Extra task' } });
    fireEvent.click(addBtn);

    // 1 completed out of 4 now
    expect(screen.getByText('1/4')).toBeInTheDocument();
  });

  test('toggles task completion', () => {
    render(<App />);
    // "Write unit tests" is initially incomplete
    const checkboxes = screen.getAllByTestId('task-checkbox');
    // Second task (index 1) is "Write unit tests" - incomplete
    fireEvent.click(checkboxes[1]);
    expect(screen.getByText('2/3')).toBeInTheDocument();
  });

  test('deletes a task', () => {
    render(<App />);
    const deleteButtons = screen.getAllByTestId('task-delete');
    fireEvent.click(deleteButtons[0]);
    expect(screen.queryByText('Setup project')).not.toBeInTheDocument();
    expect(screen.getByText('2/2')).toBeInTheDocument();
  });
});
