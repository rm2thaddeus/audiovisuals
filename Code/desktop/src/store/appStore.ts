import { create } from 'zustand';

type ThemeOption = 'dark' | 'light';
export type AppTab = 'synesthesia' | 'analysis' | 'styles' | 'explorer' | 'projects';

export interface AppState {
  activeTab: AppTab;
  theme: ThemeOption;
  isLoading: boolean;
  error: string | null;
  setActiveTab: (tab: AppTab) => void;
  setError: (error: string | null) => void;
  setTheme: (theme: ThemeOption) => void;
  setIsLoading: (loading: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  activeTab: 'synesthesia',
  theme: 'dark',
  isLoading: false,
  error: null,
  setActiveTab: (tab) => set({ activeTab: tab }),
  setError: (error) => set({ error }),
  setTheme: (theme) => set({ theme }),
  setIsLoading: (isLoading) => set({ isLoading }),
}));
