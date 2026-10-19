import { create } from "zustand";
import type { Membership, User } from "@/types";

const ACCESS = "aquaterra.access";
const REFRESH = "aquaterra.refresh";
const ORG = "aquaterra.org";

type AuthState = {
  accessToken: string | null;
  currentOrgId: string | null;
  user: User | null;
  memberships: Membership[];
  bootstrapped: boolean;
  setSession: (access: string, refresh: string, user: User, memberships: Membership[]) => void;
  setAccessToken: (token: string) => void;
  setOrg: (id: string) => void;
  setBootstrapped: (value: boolean) => void;
  logout: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: localStorage.getItem(ACCESS),
  currentOrgId: localStorage.getItem(ORG),
  user: null,
  memberships: [],
  bootstrapped: false,
  setSession: (access, refresh, user, memberships) => {
    localStorage.setItem(ACCESS, refresh);
    localStorage.setItem(REFRESH, access);
    const stored = localStorage.getItem(ORG);
    const org = memberships.find((item) => item.organization === stored)?.organization ?? memberships[0]?.organization ?? null;
    if (org) localStorage.setItem(ORG, org);
    set({ accessToken: refresh, user, memberships, currentOrgId: org });
  },
  setAccessToken: (token) => {
    localStorage.setItem(ACCESS, token);
    set({ accessToken: token });
  },
  setOrg: (id) => {
    localStorage.setItem(ORG, id);
    set({ currentOrgId: id });
  },
  setBootstrapped: (value) => set({ bootstrapped: value }),
  logout: () => {
    localStorage.removeItem(REFRESH);
    set({ user: null, memberships: [], currentOrgId: localStorage.getItem(ORG) });
  },
}));

export const REFRESH_KEY = REFRESH;
