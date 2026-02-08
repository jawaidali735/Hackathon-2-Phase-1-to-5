import React from 'react';
import styles from './MessageBubble.module.css';

interface ToolCallInfo {
  tool: string;
  params: Record<string, unknown>;
  result: any;
}

interface MessageBubbleProps {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  toolCalls?: ToolCallInfo[];
  isError?: boolean;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ role, content, timestamp, toolCalls, isError }) => {
  const isUser = role === 'user';
  const isAssistant = role === 'assistant';

  // Format timestamp
  const formattedTime = timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  // Render tool call badges
  const renderToolCallBadges = () => {
    if (!toolCalls || toolCalls.length === 0) return null;

    return (
      <div className={styles.toolCallsContainer}>
        {toolCalls.map((tc, index) => {
          const icon = getToolIcon(tc.tool);
          const label = getToolLabel(tc.tool);
          return (
            <span key={index} className={styles.toolBadge} title={`${label}: ${JSON.stringify(tc.params)}`}>
              {icon} {label}
            </span>
          );
        })}
      </div>
    );
  };

  const bubbleClass = isError
    ? `${styles.messageBubble} ${styles.error}`
    : `${styles.messageBubble} ${isUser ? styles.user : isAssistant ? styles.assistant : styles.system}`;

  return (
    <div className={bubbleClass}>
      <div className={styles.content}>
        <div className={styles.text}>{content}</div>
        {renderToolCallBadges()}
        <div className={styles.timestamp}>{formattedTime}</div>
      </div>
    </div>
  );
};

// Helper function to get icon for tool
const getToolIcon = (tool: string): string => {
  switch (tool) {
    case 'add_task': return '➕';
    case 'list_tasks': return '📋';
    case 'complete_task': return '✅';
    case 'delete_task': return '🗑️';
    case 'update_task': return '✏️';
    case 'get_current_user': return '👤';
    default: return '🔧';
  }
};

// Helper function to get label for tool
const getToolLabel = (tool: string): string => {
  switch (tool) {
    case 'add_task': return 'Added task';
    case 'list_tasks': return 'Listed tasks';
    case 'complete_task': return 'Completed task';
    case 'delete_task': return 'Deleted task';
    case 'update_task': return 'Updated task';
    case 'get_current_user': return 'Got user info';
    default: return 'Executed tool';
  }
};

export default MessageBubble;
