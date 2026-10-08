import { createClient } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

export const authProvider = (import.meta.env.VITE_AUTH_PROVIDER || "supabase").toLowerCase();
export const supabase =
  supabaseUrl && supabaseKey ? createClient(supabaseUrl, supabaseKey) : null;

export const API = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");

const LOCAL_TOKEN_KEY = "procure-local-access-token";
const localListeners = new Set();

function localToken() {
  return localStorage.getItem(LOCAL_TOKEN_KEY);
}

function localSession() {
  const token = localToken();
  return token
    ? {
        access_token: token,
        token_type: "bearer",
      }
    : null;
}

function emitLocalAuth(event, session) {
  localListeners.forEach((listener) => {
    try {
      listener(event, session);
    } catch {
      // Listener failures must not break authentication.
    }
  });
}

async function rawJson(path, options = {}) {
  const response = await fetch(API + path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  let payload = {};
  try {
    payload = await response.json();
  } catch {
    payload = {};
  }

  if (!response.ok) {
    throw new Error(payload.detail || `Request failed (${response.status})`);
  }
  return payload;
}

const localAuth = {
  configured: true,

  async getSession() {
    return { data: { session: localSession() } };
  },

  onAuthStateChange(callback) {
    localListeners.add(callback);
    return {
      data: {
        subscription: {
          unsubscribe() {
            localListeners.delete(callback);
          },
        },
      },
    };
  },

  async signInWithPassword({ email, password }) {
    try {
      const payload = await rawJson("/api/v1/auth/local/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      localStorage.setItem(LOCAL_TOKEN_KEY, payload.access_token);
      const session = localSession();
      emitLocalAuth("SIGNED_IN", session);
      return { data: { session }, error: null };
    } catch (error) {
      return { data: { session: null }, error };
    }
  },

  async signUp({ email, password, portal = "requester" }) {
    try {
      const payload = await rawJson("/api/v1/auth/local/signup", {
        method: "POST",
        body: JSON.stringify({ email, password, portal }),
      });
      localStorage.setItem(LOCAL_TOKEN_KEY, payload.access_token);
      const session = localSession();
      emitLocalAuth("SIGNED_IN", session);
      return { data: { session }, error: null };
    } catch (error) {
      return { data: { session: null }, error };
    }
  },

  async signOut() {
    localStorage.removeItem(LOCAL_TOKEN_KEY);
    emitLocalAuth("SIGNED_OUT", null);
    return { error: null };
  },

  async resetPasswordForEmail() {
    return {
      error: new Error(
        "Email password reset is unavailable in local-auth mode. Use the seeded demo password or ask an administrator to reset the local credential.",
      ),
    };
  },

  async updateUser({ password }) {
    try {
      await api("/api/v1/auth/local/change-password", {
        method: "POST",
        body: JSON.stringify({ password }),
      });
      return { error: null };
    } catch (error) {
      return { error };
    }
  },
};

const supabaseAuth = {
  configured: Boolean(supabase),

  getSession: () => supabase.auth.getSession(),
  onAuthStateChange: (callback) => supabase.auth.onAuthStateChange(callback),
  signInWithPassword: (values) => supabase.auth.signInWithPassword(values),
  signUp: (values) => supabase.auth.signUp({
    email: values.email,
    password: values.password,
  }),
  signOut: () => supabase.auth.signOut(),
  resetPasswordForEmail: (email, options) =>
    supabase.auth.resetPasswordForEmail(email, options),
  updateUser: (values) => supabase.auth.updateUser(values),
};

export const authClient = authProvider === "local" ? localAuth : supabaseAuth;

export async function api(path, options = {}) {
  const session = (await authClient.getSession()).data.session;
  const headers = {
    ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
    ...options.headers,
  };

  if (session?.access_token) {
    headers.Authorization = `Bearer ${session.access_token}`;
  }

  const response = await fetch(API + path, { ...options, headers });

  if (!response.ok) {
    let error;
    try {
      error = await response.json();
    } catch {
      error = { detail: `Request failed (${response.status})` };
    }
    throw new Error(
      Array.isArray(error.detail)
        ? error.detail.map((x) => `${x.loc.slice(1).join(".")}: ${x.msg}`).join("; ")
        : error.detail || "Request failed",
    );
  }

  if (options.blob) return response.blob();
  return response.json();
}

export const send = (path, data = {}, method = "POST") =>
  api(path, { method, body: JSON.stringify(data) });

export async function downloadDocument(doc) {
  const blob = await api("/api/v1/documents/" + doc.id, { blob: true });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = doc.original_name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
