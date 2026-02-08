/**
 * Dashboard Page - Server Component
 * Displays user tasks with real-time updates
 * Production-ready with proper authentication and error handling
 */

/**
 * Dashboard Page - Server Component
 * Displays user tasks with real-time updates
 * Production-ready with proper authentication and error handling
 */

import { auth } from '@/lib/auth';
import { headers } from 'next/headers';
import { redirect } from 'next/navigation';
import AddTaskForm from '@/components/dashboard/add-task-form';
import ClientTaskList from '@/components/dashboard/client-task-list';
import ChatWrapper from '@/components/chatbot/ChatWrapper';
import { getJWT } from '@/lib/get-jwt';
import { getUserTasks } from '@/services/server-api';
import SignOutButton from '@/components/SignOutButton';
import type { Task } from '@/types/task';

// Force dynamic rendering - no caching for real-time updates
export const dynamic = 'force-dynamic';
export const revalidate = 0;

export default async function DashboardPage() {
  // 1️⃣ Verify user is authenticated using Better Auth server-side session
  const session = await auth.api.getSession({
    headers: await headers()
  });

  if (!session?.user) redirect('/login');

  // Extract user ID from session to pass to API
  const userId = session.user.id;
  const jwt = await getJWT();
  if (!jwt) redirect('/login');

  // Fetch tasks - gracefully handles backend down
  const { data: tasks, backendConnected } = await getUserTasks(userId, jwt);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            <p>Welcome, {session.user.name}!</p>
          </div>
          <div>
            <SignOutButton />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main>
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">

            {/* Backend Offline Banner */}
            {!backendConnected && (
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6 flex items-center gap-3">
                <svg className="w-5 h-5 text-amber-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <div>
                  <p className="text-amber-800 font-medium">Service temporarily unavailable</p>
                  <p className="text-amber-600 text-sm">We&apos;re working to restore connection. Your data is safe.</p>
                </div>
              </div>
            )}

            {/* Task Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-blue-50 p-4 rounded-lg text-center">
                <h3 className="text-2xl font-bold text-blue-700">{tasks.length}</h3>
                <p className="text-gray-600">Total Tasks</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg text-center">
                <h3 className="text-2xl font-bold text-green-700">{tasks.filter((t: Task) => t.completed).length}</h3>
                <p className="text-gray-600">Completed</p>
              </div>
              <div className="bg-yellow-50 p-4 rounded-lg text-center">
                <h3 className="text-2xl font-bold text-yellow-700">{tasks.filter((t: Task) => !t.completed).length}</h3>
                <p className="text-gray-600">Pending</p>
              </div>
            </div>

            {/* Add Task Form */}
            <div className="bg-white shadow rounded-lg p-6 mb-6">
              <AddTaskForm userId={userId} /> {/* Pass user ID */}
            </div>

            {/* Task List */}
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Your Tasks</h2>
              <ClientTaskList initialTasks={tasks} userId={userId} /> {/* Pass user ID */}
            </div>

          </div>
        </div>
      </main>

      {/* AI Chat Assistant - Cohere Chatbot */}
      <ChatWrapper userId={userId} token={jwt} />
    </div>
  );
}
