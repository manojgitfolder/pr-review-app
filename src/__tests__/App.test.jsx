import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../App';

describe('App Component', () => {
  test('renders the app title', () => {
    render(<App />);
    // Match partial text since title could be TaskFlow or TaskFlow Pro
    expect(screen.getByText(/TaskFlow/i)).toBeInTheDocument();
  });

  test('shows initial tasks', () => {
    render(<App />);
    expect(screen.getByText('Setup project')).toBeInTheDocument();
    expect(screen.getByText('Write unit tests')).toBeInTheDocument();
    expect(screen.getByText('Configure CI/CD')).toBeInTheDocument();
  });

  test('displays correct progress count', () => {
    render(<App />);
    // progress-text span has "1/3" but rendered as separate nodes
    const progressText = document.querySelector('.progress-text');
    expect(progressText).toBeTruthy();
    expect(progressText.textContent.replace(/\s/g, '')).toBe('1/3');
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
    const progressText = document.querySelector('.progress-text');
    expect(progressText.textContent.replace(/\s/g, '')).toBe('1/4');
  });

  test('toggles task completion', () => {
    render(<App />);
    const checkboxes = screen.getAllByTestId('task-checkbox');
    fireEvent.click(checkboxes[1]);
    const progressText = document.querySelector('.progress-text');
    expect(progressText.textContent.replace(/\s/g, '')).toBe('2/3');
  });

  test('deletes a task', () => {
    render(<App />);
    const deleteButtons = screen.getAllByTestId('task-delete');
    fireEvent.click(deleteButtons[0]);
    expect(screen.queryByText('Setup project')).not.toBeInTheDocument();
    const progressText = document.querySelector('.progress-text');
    expect(progressText.textContent.replace(/\s/g, '')).toBe('0/2');
  });
});
