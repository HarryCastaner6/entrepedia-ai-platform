import { create } from 'zustand';

interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  agent_type?: 'coach' | 'strategist';
  sources?: string[];
}

interface AppNotification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface AppSettings {
  theme: 'light' | 'dark' | 'system';
  language: string;
  notifications: {
    email: boolean;
    push: boolean;
    processing: boolean;
  };
  ai: {
    defaultAgent: 'coach' | 'strategist';
    includeKnowledgeBase: boolean;
    responseLength: 'short' | 'medium' | 'long';
  };
}

interface SystemStatus {
  api: 'healthy' | 'warning' | 'error';
  vector_store: 'healthy' | 'warning' | 'error';
  database: 'healthy' | 'warning' | 'error';
  last_updated: Date;
}

interface AppState {
  // Chat state
  chatMessages: ChatMessage[];
  isChatLoading: boolean;
  selectedAgent: 'coach' | 'strategist';

  // Notifications
  notifications: AppNotification[];
  unreadNotificationCount: number;

  // Settings
  settings: AppSettings;

  // System status
  systemStatus: SystemStatus | null;

  // UI state
  sidebarOpen: boolean;
  activeTab: string;
  isOffline: boolean;

  // Actions
  // Chat actions
  addChatMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
  clearChatMessages: () => void;
  setChatLoading: (loading: boolean) => void;
  setSelectedAgent: (agent: 'coach' | 'strategist') => void;

  // Notification actions
  addNotification: (notification: Omit<AppNotification, 'id' | 'timestamp' | 'read'>) => void;
  markNotificationRead: (id: string) => void;
  clearNotification: (id: string) => void;
  clearAllNotifications: () => void;

  // Settings actions
  updateSettings: (updates: Partial<AppSettings>) => void;
  resetSettings: () => void;

  // System status actions
  setSystemStatus: (status: Partial<SystemStatus>) => void;

  // UI actions
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setActiveTab: (tab: string) => void;
  setOfflineStatus: (offline: boolean) => void;
}

const defaultSettings: AppSettings = {
  theme: 'system',
  language: 'en',
  notifications: {
    email: true,
    push: true,
    processing: true
  },
  ai: {
    defaultAgent: 'coach',
    includeKnowledgeBase: true,
    responseLength: 'medium'
  }
};

export const useAppStore = create<AppState>((set, get) => ({
  // Initial state
  chatMessages: [],
  isChatLoading: false,
  selectedAgent: 'coach',
  notifications: [],
  unreadNotificationCount: 0,
  settings: defaultSettings,
  systemStatus: null,
  sidebarOpen: true,
  activeTab: 'dashboard',
  isOffline: false,

  // Chat actions
  addChatMessage: (message) => {
    const newMessage: ChatMessage = {
      ...message,
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      timestamp: new Date()
    };

    set((state) => ({
      chatMessages: [...state.chatMessages, newMessage]
    }));
  },

  clearChatMessages: () => {
    set({ chatMessages: [] });
  },

  setChatLoading: (loading) => {
    set({ isChatLoading: loading });
  },

  setSelectedAgent: (agent) => {
    set({ selectedAgent: agent });
  },

  // Notification actions
  addNotification: (notification) => {
    const newNotification: AppNotification = {
      ...notification,
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      timestamp: new Date(),
      read: false
    };

    set((state) => ({
      notifications: [newNotification, ...state.notifications],
      unreadNotificationCount: state.unreadNotificationCount + 1
    }));
  },

  markNotificationRead: (id) => {
    set((state) => {
      const updatedNotifications = state.notifications.map(notif =>
        notif.id === id ? { ...notif, read: true } : notif
      );

      const unreadCount = updatedNotifications.filter(n => !n.read).length;

      return {
        notifications: updatedNotifications,
        unreadNotificationCount: unreadCount
      };
    });
  },

  clearNotification: (id) => {
    set((state) => {
      const notification = state.notifications.find(n => n.id === id);
      const wasUnread = notification && !notification.read;

      const updatedNotifications = state.notifications.filter(n => n.id !== id);

      return {
        notifications: updatedNotifications,
        unreadNotificationCount: wasUnread
          ? state.unreadNotificationCount - 1
          : state.unreadNotificationCount
      };
    });
  },

  clearAllNotifications: () => {
    set({
      notifications: [],
      unreadNotificationCount: 0
    });
  },

  // Settings actions
  updateSettings: (updates) => {
    set((state) => ({
      settings: { ...state.settings, ...updates }
    }));
  },

  resetSettings: () => {
    set({ settings: defaultSettings });
  },

  // System status actions
  setSystemStatus: (status) => {
    set((state) => ({
      systemStatus: state.systemStatus
        ? { ...state.systemStatus, ...status, last_updated: new Date() }
        : { ...status, last_updated: new Date() } as SystemStatus
    }));
  },

  // UI actions
  toggleSidebar: () => {
    set((state) => ({ sidebarOpen: !state.sidebarOpen }));
  },

  setSidebarOpen: (open) => {
    set({ sidebarOpen: open });
  },

  setActiveTab: (tab) => {
    set({ activeTab: tab });
  },

  setOfflineStatus: (offline) => {
    set({ isOffline: offline });
  }
}));