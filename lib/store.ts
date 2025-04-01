import { create } from 'zustand';

export type Auth = {
  isAuthenticated: boolean | null ;
  setIsAuthenticated: (isAuthenticated: boolean) => void;
  initializeAuth: () => void; // Function to initialize auth from localStorage
};

export const useAuthStore = create<Auth>((set) => ({
  isAuthenticated: null,
  setIsAuthenticated: (isAuthenticated) => set({ isAuthenticated }),
  
  // Function to initialize authentication status from localStorage
  initializeAuth: () => {
    const agencyID = localStorage.getItem("agencyID");
    set({ isAuthenticated: !!agencyID });
  }
}));
