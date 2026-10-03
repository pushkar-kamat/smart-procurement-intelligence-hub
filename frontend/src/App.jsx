import React, { useEffect, useState } from "react";
import { Routes, Route, Navigate, NavLink } from "react-router-dom";
import { LayoutDashboard, LogOut } from "lucide-react";
import { api, supabase } from "./api";
import { Protected, Field } from "./components";

const Auth = React.createContext(null);
const useAuth = () => React.useContext(Auth);

function Login() {
  const [email, setEmail] = useState(""),
    [password, setPassword] = useState(""),
    [error, setError] = useState("");
  return (
    <div className="login">
      <div className="login-story">
        <div className="brand">
          <span className="brand-icon">p.</span>procure<span className="brand-dot">/</span>
        </div>
        <p className="eyebrow">SMART PROCUREMENT INTELLIGENCE HUB</p>
        <h1>Procurement foundation.</h1>
        <p>Authentication, shared data contracts and database foundation.</p>
      </div>
      <div className="login-form">
        <h2>Sign in</h2>
        {error && <p className="error">{error}</p>}
        <form
          onSubmit={async (e) => {
            e.preventDefault();
            const { error } = await supabase.auth.signInWithPassword({ email, password });
            if (error) setError(error.message);
          }}
        >
          <Field label="Email address">
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </Field>
          <Field label="Password">
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </Field>
          <button className="primary">Sign in</button>
        </form>
      </div>
    </div>
  );
}
function Home() {
  const { user } = useAuth();
  return (
    <div className="shell">
      <aside>
        <div className="brand">
          <span className="brand-icon">p.</span>procure<span className="brand-dot">/</span>
        </div>
        <nav>
          <NavLink to="/">
            <LayoutDashboard size={18} />
            Foundation
          </NavLink>
        </nav>
        <div className="sidebar-bottom">
          <div className="user">
            <span className="avatar">{user.name.slice(0, 1).toUpperCase()}</span>
            <div>
              <strong>{user.name}</strong>
              <small>{user.role}</small>
            </div>
            <button onClick={() => supabase.auth.signOut()}>
              <LogOut size={17} />
            </button>
          </div>
        </div>
      </aside>
      <main>
        <div className="content">
          <h1>Shared foundation ready</h1>
          <p>Role: {user.role}</p>
          <p>Feature modules will be integrated stage by stage.</p>
        </div>
      </main>
    </div>
  );
}
export default function App() {
  const [user, setUser] = useState(null),
    [ready, setReady] = useState(false);
  useEffect(() => {
    if (!supabase) {
      setReady(true);
      return;
    }
    const load = async (session) => {
      if (!session) {
        setUser(null);
        setReady(true);
        return;
      }
      try {
        setUser(await api("/api/v1/me"));
      } finally {
        setReady(true);
      }
    };
    supabase.auth.getSession().then(({ data }) => load(data.session));
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_e, s) => setTimeout(() => load(s), 0));
    return () => subscription.unsubscribe();
  }, []);
  if (!ready) return <div className="loading">Opening workspace…</div>;
  return (
    <Auth.Provider value={{ user, setUser }}>
      <Routes>
        <Route path="/login" element={user ? <Navigate to="/" /> : <Login />} />
        <Route
          path="/*"
          element={
            <Protected user={user}>
              <Home />
            </Protected>
          }
        />
      </Routes>
    </Auth.Provider>
  );
}
