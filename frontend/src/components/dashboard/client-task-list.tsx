'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { toggleTaskCompletionAction, deleteTaskAction, updateTaskAction } from '@/app/actions/task-actions';
import type { Task } from '@/types/task';

interface ClientTaskListProps {
  initialTasks: Task[];
  userId: string;
}

export default function ClientTaskList({ initialTasks, userId }: ClientTaskListProps) {
  const [tasks, setTasks] = useState<Task[]>(initialTasks);
  const [loadingTaskId, setLoadingTaskId] = useState<string | null>(null);
  const [editingTaskId, setEditingTaskId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState<string>('');
  const [editDescription, setEditDescription] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // CRITICAL: Update local state when server data changes (after DB operations complete)
  useEffect(() => {
    setTasks(initialTasks);
    setLoadingTaskId(null); // Clear loading state when new data arrives
  }, [initialTasks]);

  // Listen for tasksChanged event to refresh the task list
  useEffect(() => {
    const handleTasksChanged = () => {
      // Refresh to get latest data from server when tasks are changed via chatbot
      router.refresh();
    };

    window.addEventListener('tasksChanged', handleTasksChanged);

    return () => {
      window.removeEventListener('tasksChanged', handleTasksChanged);
    };
  }, [router]); // Include router in dependency array

  // Function to toggle task completion - NO optimistic update, wait for DB
  const toggleTaskCompletion = async (taskId: string) => {
    setError(null);
    setLoadingTaskId(taskId); // Show loading state

    const task = tasks.find(t => t.id === taskId);
    if (!task) return;

    const newCompletedStatus = !task.completed;

    try {
      await toggleTaskCompletionAction(userId, taskId, newCompletedStatus);
      // Refresh to get latest data from server - counter and tasks update together
      router.refresh();
    } catch (err) {
      setLoadingTaskId(null);
      console.error('Failed to toggle task completion:', err);
      setError(err instanceof Error ? err.message : 'Failed to update task. Please try again.');
    }
  };

  // Function to delete a task - NO optimistic update, wait for DB
  const deleteTask = async (taskId: string) => {
    if (!confirm('Are you sure you want to delete this task?')) {
      return;
    }

    setError(null);
    setLoadingTaskId(taskId); // Show loading state

    try {
      await deleteTaskAction(userId, taskId);
      // Refresh to get latest data from server - counter and tasks update together
      router.refresh();
    } catch (err) {
      setLoadingTaskId(null);
      console.error('Failed to delete task:', err);
      setError(err instanceof Error ? err.message : 'Failed to delete task. Please try again.');
    }
  };

  // Function to start editing a task
  const startEdit = (task: Task) => {
    setEditingTaskId(task.id);
    setEditTitle(task.title);
    setEditDescription(task.description || '');
    setError(null);
  };

  // Function to cancel editing
  const cancelEdit = () => {
    setEditingTaskId(null);
    setEditTitle('');
    setEditDescription('');
    setError(null);
  };

  // Function to save edited task
  const saveEdit = async (taskId: string) => {
    setError(null);
    setLoadingTaskId(taskId); // Show loading state

    try {
      await updateTaskAction(userId, taskId, {
        title: editTitle,
        description: editDescription,
      });
      setEditingTaskId(null);
      // Refresh to get latest data from server
      router.refresh();
    } catch (err) {
      setLoadingTaskId(null);
      console.error('Failed to update task:', err);
      setError(err instanceof Error ? err.message : 'Failed to update task. Please try again.');
    }
  };

  return (
    <div>
      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {tasks.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p>No tasks yet. Create your first task!</p>
        </div>
      ) : (
        <div className="space-y-3">
          {tasks.map((task) => {
            const isLoading = loadingTaskId === task.id;
            const isEditing = editingTaskId === task.id;

            return (
              <div
                key={task.id}
                className={`p-4 bg-white rounded-lg border shadow-sm transition-all ${
                  task.completed ? 'bg-green-50 border-green-200' : 'border-gray-200'
                } ${isLoading ? 'opacity-50 pointer-events-none' : ''}`}
              >
                {isEditing ? (
                  // Edit Mode
                  <div className="space-y-3">
                    <input
                      type="text"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      placeholder="Task title"
                      disabled={isLoading}
                    />
                    <textarea
                      value={editDescription}
                      onChange={(e) => setEditDescription(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      placeholder="Task description (optional)"
                      rows={3}
                      disabled={isLoading}
                    />
                    <div className="flex gap-2">
                      <button
                        onClick={() => saveEdit(task.id)}
                        disabled={isLoading || !editTitle.trim()}
                        className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {isLoading ? 'Saving...' : 'Save'}
                      </button>
                      <button
                        onClick={cancelEdit}
                        disabled={isLoading}
                        className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 disabled:opacity-50"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  // View Mode
                  <div>
                    <div className="flex items-start justify-between">
                      <div className="flex items-start flex-1 min-w-0">
                        <input
                          type="checkbox"
                          checked={task.completed}
                          onChange={() => toggleTaskCompletion(task.id)}
                          disabled={isLoading}
                          className="h-5 w-5 mt-0.5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                        />
                        <div className="ml-3 flex-1 min-w-0">
                          <p
                            className={`text-sm font-medium ${
                              task.completed ? 'line-through text-gray-500' : 'text-gray-900'
                            }`}
                          >
                            {task.title}
                          </p>
                          {task.description && (
                            <p className="text-sm text-gray-500 mt-1">{task.description}</p>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center gap-2 ml-4">
                        {isLoading ? (
                          <div className="flex items-center gap-2">
                            <div className="animate-spin rounded-full h-4 w-4 border-2 border-indigo-600 border-t-transparent"></div>
                            <span className="text-xs text-gray-500">Processing...</span>
                          </div>
                        ) : (
                          <>
                            <span
                              className={`px-3 py-1 text-xs font-medium rounded-full ${
                                task.completed
                                  ? 'bg-green-100 text-green-800'
                                  : 'bg-yellow-100 text-yellow-800'
                              }`}
                            >
                              {task.completed ? 'Completed' : 'Pending'}
                            </span>
                            <button
                              onClick={() => startEdit(task)}
                              disabled={isLoading}
                              className="px-3 py-1 text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded disabled:opacity-50"
                            >
                              Edit
                            </button>
                            <button
                              onClick={() => deleteTask(task.id)}
                              disabled={isLoading}
                              className="px-3 py-1 text-sm text-red-600 hover:text-red-800 hover:bg-red-50 rounded disabled:opacity-50"
                            >
                              Delete
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}