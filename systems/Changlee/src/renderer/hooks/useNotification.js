import { useState, useCallback } from 'react';

// 通知系统Hook
export const useNotification = () => {
  const [notifications, setNotifications] = useState([]);

  // 添加通知
  const addNotification = useCallback((notification) => {
    const id = Date.now() + Math.random();
    const newNotification = {
      id,
      type: 'info', // 'success' | 'error' | 'warning' | 'info'
      title: '',
      message: '',
      duration: 5000,
      ...notification
    };

    setNotifications(prev => [...prev, newNotification]);

    // 自动移除通知
    if (newNotification.duration > 0) {
      setTimeout(() => {
        removeNotification(id);
      }, newNotification.duration);
    }

    return id;
  }, []);

  // 移除通知
  const removeNotification = useCallback((id) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  }, []);

  // 清空所有通知
  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  // 快捷方法
  const showSuccess = useCallback((message, title = '成功') => {
    return addNotification({
      type: 'success',
      title,
      message,
      duration: 3000
    });
  }, [addNotification]);

  const showError = useCallback((message, title = '错误') => {
    return addNotification({
      type: 'error',
      title,
      message,
      duration: 5000
    });
  }, [addNotification]);

  const showWarning = useCallback((message, title = '警告') => {
    return addNotification({
      type: 'warning',
      title,
      message,
      duration: 4000
    });
  }, [addNotification]);

  const showInfo = useCallback((message, title = '提示') => {
    return addNotification({
      type: 'info',
      title,
      message,
      duration: 3000
    });
  }, [addNotification]);

  // 桌宠专用通知
  const showPetNotification = useCallback((message, emoji = '🐱') => {
    return addNotification({
      type: 'info',
      title: `${emoji} 长离`,
      message,
      duration: 4000
    });
  }, [addNotification]);

  return {
    notifications,
    addNotification,
    removeNotification,
    clearNotifications,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    showPetNotification
  };
};