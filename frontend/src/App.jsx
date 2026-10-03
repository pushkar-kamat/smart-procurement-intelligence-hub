import React, { useEffect, useState, useCallback } from "react";
import { Routes, Route, Navigate, NavLink, Link, useNavigate, useParams } from "react-router-dom";
import {
  LayoutDashboard,
  ClipboardList,
  Building2,
  ShieldCheck,
  Activity,
  LogOut,
  Plus,
  ArrowUpRight,
  PackageCheck,
  Search,
  ChevronRight,
} from "lucide-react";
import { api, send, supabase } from "./api";
import {
  cash,
  human,
  Badge,
  Protected,
  RoleAction,
  Field,
  Empty,
  Docs,
  ComparisonMatrix,
  validateRequisition,
} from "./components";
const Auth = React.createContext(null);
const useAuth = () => React.useContext(Auth);
function useLoad(path) {
  const [data, setData] = useState(null),
    [error, setError] = useState("");
  const refresh = useCallback(async () => {
    try {
      setData(await api(path));
      setError("");
    } catch (e) {
      setError(e.message);
    }
  }, [path]);
  useEffect(() => {
    refresh();
  }, [refresh]);
  return { data, error, refresh };
}
function ErrorBox({ error }) {
  return error ? (
    <p className="error" role="alert">
      {error}
    </p>
  ) : null;
}
function Header({ eyebrow = "WORKSPACE", title, children, subtitle }) {
  return (
    <div className="page-head">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        {subtitle && <p className="muted">{subtitle}</p>}
      </div>
      {children}
    </div>
  );
}
function ActionForm({ onSubmit, children, label = "Save", className = "" }) {
  const [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  return (
    <form
      className={className}
      onSubmit={async (e) => {
        e.preventDefault();
        setBusy(true);
        setError("");
        try {
          await onSubmit(e);
        } catch (e) {
          setError(e.message);
        } finally {
          setBusy(false);
        }
      }}
    >
      <fieldset disabled={busy}>
        {children}
        <ErrorBox error={error} />
        <button className="primary" type="submit">
          {busy ? "Saving…" : label}
        </button>
      </fieldset>
    </form>
  );
}
export default function App() {
  const [user, setUser] = useState(null),
    [ready, setReady] = useState(false),
    [error, setError] = useState("");
  useEffect(() => {
    if (!supabase) {
      setReady(true);
      return;
    }
    let active = true;
    const load = async (session) => {
      if (!session) {
        if (active) {
          setUser(null);
          setReady(true);
        }
        return;
      }
      try {
        const p = await api("/api/v1/me");
        if (active) {
          setUser(p);
          setError("");
        }
      } catch (e) {
        if (active) setError(e.message);
      } finally {
        if (active) setReady(true);
      }
    };
    supabase.auth.getSession().then(({ data }) => load(data.session));
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setTimeout(() => load(session), 0);
    });
    return () => {
      active = false;
      subscription.unsubscribe();
    };
  }, []);
  if (!ready) return <div className="loading">Opening your workspace…</div>;
  return (
    <Auth.Provider value={{ user, setUser }}>
      <Routes>
        <Route path="/login" element={user ? <Navigate to="/" /> : <Login error={error} />} />
        <Route
          path="/*"
          element={
            <Protected user={user}>
              <Shell />
            </Protected>
          }
        />
      </Routes>
    </Auth.Provider>
  );
}
function Login({ error }) {
  const [email, setEmail] = useState(""),
    [password, setPassword] = useState(""),
    [signup, setSignup] = useState(false),
    [notice, setNotice] = useState("");
  return (
    <div className="login">
      <div className="login-story">
        <div className="brand">
          <span className="brand-icon">p.</span>procure<span className="brand-dot">/</span>
        </div>
        <p className="eyebrow">SMART PROCUREMENT INTELLIGENCE HUB</p>
        <h1>
          Every purchase.
          <br />A clearer decision.
        </h1>
        <p>Compare quotations, understand vendor risk and keep every approval accountable.</p>
        <div className="login-points">
          <span>01 &nbsp; Explainable price checks</span>
          <span>02 &nbsp; Human-controlled approval</span>
          <span>03 &nbsp; A complete audit trail</span>
        </div>
        <small>BCA-08 · Capstone prototype</small>
      </div>
      <div className="login-form">
        <h2>{signup ? "Create your account" : "Welcome back"}</h2>
        <p className="muted">
          {signup
            ? "New accounts begin with the requester role."
            : "Sign in to your procurement workspace."}
        </p>
        {!supabase && (
          <p className="error">
            Configure VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in frontend/.env, then restart
            Vite. See the quick-start guide.
          </p>
        )}
        <ErrorBox error={error} />
        <ActionForm
          label={signup ? "Create account" : "Sign in"}
          onSubmit={async () => {
            if (!supabase) throw Error("Supabase configuration is required");
            const { error } = signup
              ? await supabase.auth.signUp({ email, password })
              : await supabase.auth.signInWithPassword({ email, password });
            if (error) throw error;
            if (signup) setNotice("Check your email to confirm your account, then sign in.");
          }}
        >
          <Field label="Email address">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </Field>
          <Field label="Password">
            <input
              type="password"
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete={signup ? "new-password" : "current-password"}
            />
          </Field>
        </ActionForm>
        {notice && <p className="notice">{notice}</p>}
        <button className="link" onClick={() => setSignup(!signup)}>
          {signup ? "Already registered? Sign in" : "New requester? Create an account"}
        </button>
      </div>
    </div>
  );
}
function Shell() {
  const { user } = useAuth();
  return (
    <div className="shell">
      <aside>
        <div className="brand">
          <span className="brand-icon">p.</span>procure<span className="brand-dot">/</span>
        </div>
        <p className="nav-label">WORKSPACE</p>
        <nav>
          {[
            ["/", "Overview", LayoutDashboard],
            ["/requisitions", "Requisitions", ClipboardList],
            ["/vendors", "Vendors", Building2],
            ...(["approver", "finance_admin"].includes(user.role)
              ? [["/approvals", "Approval inbox", ShieldCheck]]
              : []),
            ...(user.role === "finance_admin" ? [["/operations", "Operations", Activity]] : []),
          ].map(([to, label, Icon]) => (
            <NavLink key={to} to={to} end={to === "/"}>
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="prototype">
            BCA-08
            <br />
            <small>Procurement Intelligence Hub</small>
          </div>
          <div className="user">
            <span className="avatar">{user.name.slice(0, 1).toUpperCase()}</span>
            <div>
              <strong>{user.name}</strong>
              <small>{human(user.role)}</small>
            </div>
            <button aria-label="Sign out" onClick={() => supabase.auth.signOut()}>
              <LogOut size={17} />
            </button>
          </div>
        </div>
      </aside>
      <main>
        <div className="topbar">
          <span>
            Procurement workspace <ChevronRight size={14} /> Institutional purchasing
          </span>
          <span className="live-dot">Human oversight enabled</span>
        </div>
        <div className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/requisitions" element={<RequestList />} />
            <Route path="/requisitions/new" element={<RequisitionForm />} />
            <Route path="/requisitions/:id/edit" element={<RequisitionForm />} />
            <Route path="/requisitions/:id" element={<RequestDetail />} />
            <Route path="/vendors" element={<Vendors />} />
            <Route path="/approvals" element={<Approvals />} />
            <Route path="/purchase-orders/:id" element={<PO />} />
            <Route path="/operations" element={<Operations />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}
function Dashboard() {
  const { data, error } = useLoad("/api/v1/requisitions"),
    { user } = useAuth();
  return (
    <>
      <Header
        title="Purchasing, in perspective."
        subtitle="From the first request to the final record. Every decision in one place."
      >
        <RoleAction user={user} roles={["requester"]}>
          <Link className="primary" to="/requisitions/new">
            <Plus size={17} /> New requisition
          </Link>
        </RoleAction>
      </Header>
      <ErrorBox error={error} />
      <div className="stats">
        {[
          [
            "Active requests",
            data?.filter((x) => !["CLOSED", "CANCELLED", "REJECTED"].includes(x.status)).length ??
              "—",
            "In the procurement pipeline",
          ],
          [
            "Awaiting approval",
            data?.filter((x) => x.status === "PENDING_APPROVAL").length ?? "—",
            "Ready for human review",
          ],
          [
            "Estimated value",
            data ? cash(data.reduce((a, x) => a + Number(x.estimated_total), 0)) : "—",
            "Across visible requisitions",
          ],
          [
            "Completed",
            data?.filter((x) => x.status === "CLOSED").length ?? "—",
            "Delivery and invoice recorded",
          ],
        ].map(([label, value, note]) => (
          <div className="stat" key={label}>
            <p>{label}</p>
            <strong>{value}</strong>
            <small>{note}</small>
          </div>
        ))}
      </div>
      <div className="callout">
        <div>
          <p className="eyebrow">DECISION SUPPORT, WITH CONTEXT</p>
          <h2>Good procurement goes beyond the lowest price.</h2>
          <p>
            Compare cost, delivery and vendor history. Every flagged price includes the reason
            behind it.
          </p>
        </div>
        <ShieldCheck size={64} />
      </div>
      <section className="panel">
        <div className="section-head">
          <h2>Recent requisitions</h2>
          <Link className="link" to="/requisitions">
            View all <ArrowUpRight size={16} />
          </Link>
        </div>
        <RequestTable rows={data?.slice(0, 6)} />
      </section>
    </>
  );
}
function RequestTable({ rows }) {
  if (!rows) return <Empty>Loading requisitions…</Empty>;
  if (!rows.length) return <Empty>No requisitions yet. Create a request to begin.</Empty>;
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Requisition</th>
            <th>Status</th>
            <th>Estimated value</th>
            <th>Created</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id}>
              <td>
                <Link className="row-title" to={"/requisitions/" + r.id}>
                  {r.title}
                </Link>
                <small>REQ-{String(r.id).padStart(4, "0")}</small>
              </td>
              <td>
                <Badge value={r.status} />
              </td>
              <td>{cash(r.estimated_total)}</td>
              <td>{new Date(r.created_at).toLocaleDateString()}</td>
              <td>
                <Link aria-label={"Open " + r.title} to={"/requisitions/" + r.id}>
                  <ArrowUpRight size={17} />
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
function RequestList() {
  const { data, error } = useLoad("/api/v1/requisitions"),
    [search, setSearch] = useState(""),
    [status, setStatus] = useState(""),
    { user } = useAuth();
  return (
    <>
      <Header title="Requisitions" subtitle="Track the full journey of every purchase.">
        <RoleAction user={user} roles={["requester"]}>
          <Link className="primary" to="/requisitions/new">
            <Plus size={17} /> New requisition
          </Link>
        </RoleAction>
      </Header>
      <ErrorBox error={error} />
      <section className="panel">
        <div className="filters">
          <Search size={18} />
          <input
            aria-label="Search requisitions"
            placeholder="Search requisitions…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <select
            aria-label="Filter status"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
          >
            <option value="">All statuses</option>
            {[...new Set(data?.map((r) => r.status))].map((s) => (
              <option key={s}>{s}</option>
            ))}
          </select>
        </div>
        <RequestTable
          rows={data?.filter(
            (r) =>
              r.title.toLowerCase().includes(search.toLowerCase()) &&
              (!status || r.status === status),
          )}
        />
      </section>
    </>
  );
}
const blankItem = () => ({
  item_name: "",
  category: "",
  description: "",
  quantity: 1,
  unit: "piece",
  estimated_unit_price: "",
});
function RequisitionForm() {
  const { id } = useParams(),
    { user } = useAuth(),
    navigate = useNavigate(),
    { data: deps, error } = useLoad("/api/v1/departments");
  const [form, setForm] = useState({
      title: "",
      justification: "",
      department_id: user.department_id || "",
      items: [blankItem()],
    }),
    [loadError, setLoadError] = useState("");
  useEffect(() => {
    if (id)
      api("/api/v1/requisitions/" + id)
        .then((d) =>
          setForm({
            title: d.title,
            justification: d.justification,
            department_id: d.department_id,
            items: d.items.map(
              ({ item_name, category, description, quantity, unit, estimated_unit_price }) => ({
                item_name,
                category,
                description,
                quantity,
                unit,
                estimated_unit_price,
              }),
            ),
          }),
        )
        .catch((e) => setLoadError(e.message));
  }, [id]);
  if (user.role !== "requester")
    return <Empty>Only requesters can create or edit requisitions.</Empty>;
  const update = (key, v) => setForm({ ...form, [key]: v });
  return (
    <>
      <Header
        title={id ? "Edit draft" : "New requisition"}
        subtitle="Describe what you need. Totals are calculated from your line items."
      />
      <ErrorBox error={error || loadError} />
      <ActionForm
        className="panel form-panel"
        label="Save draft"
        onSubmit={async () => {
          const error = validateRequisition(form);
          if (error) throw Error(error);
          const d = await send(
            "/api/v1/requisitions" + (id ? "/" + id : ""),
            { ...form, department_id: Number(form.department_id) },
            id ? "PUT" : "POST",
          );
          navigate("/requisitions/" + d.id);
        }}
      >
        <div className="grid2">
          <Field label="Request title">
            <input
              required
              minLength={3}
              value={form.title}
              onChange={(e) => update("title", e.target.value)}
            />
          </Field>
          <Field label="Department">
            <select
              required
              value={form.department_id}
              onChange={(e) => update("department_id", e.target.value)}
            >
              <option value="">Select department</option>
              {deps
                ?.filter((d) => !user.department_id || d.id === user.department_id)
                .map((d) => (
                  <option value={d.id} key={d.id}>
                    {d.name}
                  </option>
                ))}
            </select>
          </Field>
        </div>
        <Field label="Business justification">
          <textarea
            required
            minLength={5}
            value={form.justification}
            onChange={(e) => update("justification", e.target.value)}
          />
        </Field>
        <h2>Line items</h2>
        {form.items.map((item, i) => (
          <div className="item-card" key={i}>
            <div className="grid3">
              {[
                ["Item name", "item_name", "text"],
                ["Category", "category", "text"],
                ["Description / specification", "description", "text"],
                ["Quantity", "quantity", "number"],
                ["Unit", "unit", "text"],
                ["Estimated unit price (INR)", "estimated_unit_price", "number"],
              ].map(([label, key, type]) => (
                <Field key={key} label={label}>
                  <input
                    required={key !== "description"}
                    type={type}
                   min={
  key === 'quantity'
    ? '0.001'
    : key === 'estimated_unit_price'
      ? '0.01'
      : undefined
}
step={
  key === 'quantity'
    ? '0.001'
    : key === 'estimated_unit_price'
      ? '0.01'
      : undefined
}
                    value={item[key]}
                    onChange={(e) =>
                      update(
                        "items",
                        form.items.map((x, j) => (j === i ? { ...x, [key]: e.target.value } : x)),
                      )
                    }
                  />
                </Field>
              ))}
            </div>
            {form.items.length > 1 && (
              <button
                type="button"
                className="link"
                onClick={() =>
                  update(
                    "items",
                    form.items.filter((_, j) => j !== i),
                  )
                }
              >
                Remove item
              </button>
            )}
          </div>
        ))}
        <button
          type="button"
          className="secondary"
          onClick={() => update("items", [...form.items, blankItem()])}
        >
          <Plus size={16} /> Add line item
        </button>
        <p className="total-preview">
          Estimated total{" "}
          <strong>
            {cash(
              form.items.reduce(
                (s, i) => s + Number(i.quantity) * Number(i.estimated_unit_price),
                0,
              ),
            )}
          </strong>
        </p>
      </ActionForm>
    </>
  );
}
function RequestDetail() {
  const { id } = useParams(),
    { user } = useAuth(),
    { data, error, refresh } = useLoad("/api/v1/requisitions/" + id),
    [tab, setTab] = useState("overview"),
    [actionError, setActionError] = useState(""),
    [busy, setBusy] = useState(false);
  const act = async (path, body = {}) => {
    setBusy(true);
    setActionError("");
    try {
      await send("/api/v1/requisitions/" + id + "/" + path, body);
      await refresh();
    } catch (e) {
      setActionError(e.message);
    } finally {
      setBusy(false);
    }
  };
  if (!data)
    return (
      <>
        <ErrorBox error={error} />
        <Empty>Loading requisition…</Empty>
      </>
    );
  return (
    <>
      <Header
        eyebrow={"REQ-" + String(id).padStart(4, "0")}
        title={data.title}
        subtitle={data.justification}
      >
        <Badge value={data.status} />
      </Header>
      <ErrorBox error={error || actionError} />
      <div className="workflow-strip">
        {["Request", "Sourcing", "Comparison", "Approval", "Order", "Fulfilment"].map((s, i) => (
          <span
            key={s}
            className={
              i <=
              (["DRAFT", "SUBMITTED"].includes(data.status)
                ? 0
                : ["SOURCING", "QUOTATIONS_RECEIVED"].includes(data.status)
                  ? 1
                  : data.status === "COMPARISON_READY"
                    ? 2
                    : ["PENDING_APPROVAL", "APPROVED", "REJECTED"].includes(data.status)
                      ? 3
                      : data.status === "PO_ISSUED"
                        ? 4
                        : 5)
                ? "reached"
                : ""
            }
          >
            {i + 1} <b>{s}</b>
          </span>
        ))}
      </div>
      <div className="tabs">
        {["overview", "quotations", "comparison", "audit"].map((t) => (
          <button className={tab === t ? "selected" : ""} onClick={() => setTab(t)} key={t}>
            {human(t)}
          </button>
        ))}
      </div>
      {tab === "overview" && (
        <>
          <section className="panel">
            <div className="section-head">
              <h2>Requested items</h2>
              <strong>{cash(data.estimated_total)} estimated</strong>
            </div>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Item / specification</th>
                    <th>Quantity</th>
                    <th>Unit price</th>
                    <th>Line total</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((i) => (
                    <tr key={i.id}>
                      <td>
                        {i.item_name}
                        <small>
                          {i.description} · {i.category}
                        </small>
                      </td>
                      <td>
                        {i.quantity} {i.unit}
                      </td>
                      <td>{cash(i.estimated_unit_price)}</td>
                      <td>{cash(i.estimated_line_total)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="actions">
              <RoleAction user={user} roles={["requester"]}>
                {data.status === "DRAFT" && (
                  <>
                    <Link className="secondary" to={"/requisitions/" + id + "/edit"}>
                      Edit draft
                    </Link>
                    <button className="primary" disabled={busy} onClick={() => act("submit")}>
                      Submit request
                    </button>
                  </>
                )}
              </RoleAction>
              <RoleAction user={user} roles={["procurement"]}>
                {data.status === "APPROVED" && (
                  <button className="primary" disabled={busy} onClick={() => act("purchase-order")}>
                    Issue purchase order
                  </button>
                )}
              </RoleAction>
              {data.purchase_order && (
                <Link className="primary" to={"/purchase-orders/" + data.purchase_order.id}>
                  Open purchase order <ArrowUpRight size={16} />
                </Link>
              )}
            </div>
          </section>
          <Invitations req={data} refresh={refresh} />
          <ApprovalPanel req={data} refresh={refresh} />
          <RoleAction user={user} roles={["requester"]}>
            {["DRAFT", "SUBMITTED"].includes(data.status) && (
              <section className="panel form-panel">
                <h2>Cancel requisition</h2>
                <CommentAction
                  label="Cancel request"
                  onSubmit={(comment) => act("cancel", { comment })}
                />
              </section>
            )}
          </RoleAction>
        </>
      )}
      {tab === "quotations" && <Quotations req={data} refresh={refresh} />}{" "}
      {tab === "comparison" && <Comparison req={data} refresh={refresh} />}{" "}
      {tab === "audit" && <Audit id={id} />}
    </>
  );
}
function Invitations({ req, refresh }) {
  const { user } = useAuth(),
    { data: vendors } = useLoad("/api/v1/vendors"),
    [vendor, setVendor] = useState("");
  return (
    <section className="panel form-panel">
      <h2>Vendor invitations</h2>
      <p className="muted">
        Invitations are recorded in-app. Contact vendors separately to request quotations.
      </p>
      <div className="chips">
        {req.invitations.map((i) => (
          <span key={i.id}>
            {i.vendor.name} <Badge value={i.status} />
          </span>
        ))}
      </div>
      <RoleAction user={user} roles={["procurement"]}>
        {["SUBMITTED", "SOURCING", "QUOTATIONS_RECEIVED"].includes(req.status) && (
          <ActionForm
            label="Record invitation"
            onSubmit={async () => {
              await send("/api/v1/requisitions/" + req.id + "/invitations", {
                vendor_id: Number(vendor),
              });
              setVendor("");
              refresh();
            }}
          >
            <Field label="Vendor">
              <select required value={vendor} onChange={(e) => setVendor(e.target.value)}>
                <option value="">Choose active vendor</option>
                {vendors
                  ?.filter((v) => v.active && !req.invitations.some((i) => i.vendor_id === v.id))
                  .map((v) => (
                    <option key={v.id} value={v.id}>
                      {v.name}
                    </option>
                  ))}
              </select>
            </Field>
          </ActionForm>
        )}
      </RoleAction>
    </section>
  );
}
function CommentAction({ label, onSubmit }) {
  const [comment, setComment] = useState("");
  return (
    <ActionForm label={label} onSubmit={() => onSubmit(comment)}>
      <Field label="Reason / review comment">
        <textarea
          required
          minLength={5}
          value={comment}
          onChange={(e) => setComment(e.target.value)}
        />
      </Field>
    </ActionForm>
  );
}
function ApprovalPanel({ req, refresh }) {
  const { user } = useAuth(),
    [decision, setDecision] = useState("APPROVED");
  const next = req.approval_plan?.[req.approvals.length];
  return (
    <section className="panel form-panel">
      <h2>Approval record</h2>
      {req.approvals.length ? (
        req.approvals.map((a) => (
          <div className="approval-record" key={a.id}>
            <Badge value={a.decision} />
            <strong>Level {a.approval_level}</strong>
            <p>{a.comment}</p>
            <small>
              Approver #{a.approver_id} · {new Date(a.decided_at).toLocaleString()}
            </small>
          </div>
        ))
      ) : (
        <p className="muted">No approval decisions recorded yet.</p>
      )}
      {req.status === "PENDING_APPROVAL" && (
        <p className="notice">
          Next: {next.name} · {human(next.role)}
        </p>
      )}
      {req.status === "PENDING_APPROVAL" && next.role === user.role && (
        <>
          <Field label="Decision">
            <select value={decision} onChange={(e) => setDecision(e.target.value)}>
              <option>APPROVED</option>
              <option>REJECTED</option>
            </select>
          </Field>
          <CommentAction
            label="Record decision"
            onSubmit={async (comment) => {
              await send("/api/v1/requisitions/" + req.id + "/approval", { decision, comment });
              refresh();
            }}
          />
        </>
      )}
    </section>
  );
}
function Upload({ path, onDone }) {
  const [file, setFile] = useState(null);
  return (
    <ActionForm
      label="Upload document"
      onSubmit={async () => {
        if (!file) throw Error("Choose a document");
        const body = new FormData();
        body.append("file", file);
        await api("/api/v1/" + path + "/file", { method: "POST", body });
        onDone();
      }}
    >
      <Field label="PDF, PNG or JPEG · maximum 10 MB by default">
        <input
          type="file"
          required
          accept="application/pdf,image/png,image/jpeg"
          onChange={(e) => setFile(e.target.files[0])}
        />
      </Field>
    </ActionForm>
  );
}
function Quotations({ req, refresh }) {
  const { user } = useAuth(),
    [editing, setEditing] = useState(null);
  const editable = ["SOURCING", "QUOTATIONS_RECEIVED", "COMPARISON_READY"].includes(req.status);
  return (
    <>
      <section className="panel form-panel">
        <h2>Recorded quotations</h2>
        {!req.quotations.length && <Empty>No quotations received yet.</Empty>}
        {req.quotations.map((q) => (
          <div className="quote-card" key={q.id}>
            <div className="section-head">
              <div>
                <h3>{q.vendor.name}</h3>
                <small>
                  {q.quotation_number} · {q.delivery_days} days delivery
                </small>
              </div>
              <strong>{cash(q.grand_total)}</strong>
            </div>
            <Docs documents={q.documents} />
            <RoleAction user={user} roles={["procurement"]}>
              {editable && (
                <>
                  <button className="secondary" onClick={() => setEditing(q)}>
                    Edit quotation
                  </button>
                  {!q.documents.length && <Upload path={"quotations/" + q.id} onDone={refresh} />}
                </>
              )}
            </RoleAction>
          </div>
        ))}
      </section>
      <RoleAction user={user} roles={["procurement"]}>
        {editable && (
          <QuoteForm
            key={editing?.id || "new-" + req.quotations.length}
            req={req}
            editing={editing}
            onDone={() => {
              setEditing(null);
              refresh();
            }}
            onCancel={() => setEditing(null)}
          />
        )}
      </RoleAction>
    </>
  );
}
function QuoteForm({ req, editing, onDone, onCancel }) {
  const [form, setForm] = useState({
    vendor_id: editing?.vendor_id || "",
    quotation_number: editing?.quotation_number || "",
    quotation_date: editing?.quotation_date || new Date().toLocaleDateString("en-CA"),
    valid_until: editing?.valid_until || "",
    delivery_days: editing?.delivery_days ?? 7,
    delivery_terms: editing?.delivery_terms || "",
    items: req.items.map((i) => {
      const old = editing?.items.find((x) => x.requisition_item_id === i.id);
      return {
        requisition_item_id: i.id,
        unit_price: old?.unit_price || "",
        tax_percent: old
          ? Math.round((old.tax / (old.unit_price * old.quantity - old.discount)) * 10000) / 100
          : 18,
        discount: old?.discount || 0,
      };
    }),
  });
  const update = (key, value) => setForm({ ...form, [key]: value });
  return (
    <section className="panel form-panel">
      <h2>{editing ? "Edit quotation" : "Enter vendor quotation"}</h2>
      <ActionForm
        label="Save quotation"
        onSubmit={async () => {
          await send(
            editing
              ? "/api/v1/quotations/" + editing.id
              : "/api/v1/requisitions/" + req.id + "/quotations",
            {
              ...form,
              vendor_id: Number(form.vendor_id),
              delivery_days: Number(form.delivery_days),
              valid_until: form.valid_until || null,
            },
            editing ? "PUT" : "POST",
          );
          onDone();
        }}
      >
        <div className="grid3">
          <Field label="Invited vendor">
            <select
              required
              disabled={!!editing}
              value={form.vendor_id}
              onChange={(e) => update("vendor_id", e.target.value)}
            >
              <option value="">Select vendor</option>
              {req.invitations
                .filter(
                  (i) =>
                    editing?.vendor_id === i.vendor_id ||
                    !req.quotations.some((q) => q.vendor_id === i.vendor_id),
                )
                .map((i) => (
                  <option value={i.vendor_id} key={i.id}>
                    {i.vendor.name}
                  </option>
                ))}
            </select>
          </Field>
          <Field label="Quotation number">
            <input
              required
              value={form.quotation_number}
              onChange={(e) => update("quotation_number", e.target.value)}
            />
          </Field>
          <Field label="Quotation date">
            <input
              required
              type="date"
              value={form.quotation_date}
              onChange={(e) => update("quotation_date", e.target.value)}
            />
          </Field>
          <Field label="Valid until (optional)">
            <input
              type="date"
              value={form.valid_until}
              onChange={(e) => update("valid_until", e.target.value)}
            />
          </Field>
          <Field label="Delivery days">
            <input
              required
              min="0"
              type="number"
              value={form.delivery_days}
              onChange={(e) => update("delivery_days", e.target.value)}
            />
          </Field>
          <Field label="Delivery terms">
            <input
              value={form.delivery_terms}
              onChange={(e) => update("delivery_terms", e.target.value)}
            />
          </Field>
        </div>
        {req.items.map((item, i) => (
          <div className="item-card" key={item.id}>
            <h3>
              {item.item_name}{" "}
              <small>
                {item.quantity} {item.unit}
              </small>
            </h3>
            <div className="grid3">
              {[
                ["Unit price (INR)", "unit_price"],
                ["Tax (%) on discounted base", "tax_percent"],
                ["Line discount (INR)", "discount"],
              ].map(([label, key]) => (
                <Field key={key} label={label}>
                  <input
                    type="number"
                    required
                    min={key === "unit_price" ? ".01" : "0"}
                    max={key === "tax_percent" ? "100" : undefined}
                    step=".01"
                    value={form.items[i][key]}
                    onChange={(e) =>
                      update(
                        "items",
                        form.items.map((x, j) => (i === j ? { ...x, [key]: e.target.value } : x)),
                      )
                    }
                  />
                </Field>
              ))}
            </div>
          </div>
        ))}
        {editing && (
          <button type="button" className="secondary" onClick={onCancel}>
            Cancel edit
          </button>
        )}
      </ActionForm>
    </section>
  );
}
function Comparison({ req, refresh }) {
  const { user } = useAuth(),
    { data, error, refresh: reload } = useLoad("/api/v1/requisitions/" + req.id + "/comparison"),
    [vendor, setVendor] = useState("");
  return (
    <section className="panel">
      <div className="section-head">
        <div>
          <h2>Quotation comparison</h2>
          <p className="muted">Compare evidence. Final vendor selection remains yours.</p>
        </div>
        <RoleAction user={user} roles={["procurement"]}>
          {["QUOTATIONS_RECEIVED", "COMPARISON_READY"].includes(req.status) && (
            <ActionForm
              label="Mark comparison ready"
              onSubmit={async () => {
                await send("/api/v1/requisitions/" + req.id + "/recalculate");
                refresh();
                reload();
              }}
            />
          )}
        </RoleAction>
      </div>
      <ErrorBox error={error} />
      <ComparisonMatrix data={data} />
      <RoleAction user={user} roles={["procurement"]}>
        {req.status === "COMPARISON_READY" && (
          <div className="form-panel">
            <h3>Propose a vendor for approval</h3>
            <Field label="Preferred vendor">
              <select value={vendor} onChange={(e) => setVendor(e.target.value)}>
                <option value="">Select vendor</option>
                {req.quotations.map((q) => (
                  <option key={q.vendor_id} value={q.vendor_id}>
                    {q.vendor.name} · {cash(q.grand_total)}
                  </option>
                ))}
              </select>
            </Field>
            <CommentAction
              label="Send for approval"
              onSubmit={async (comment) => {
                if (!vendor) throw Error("Select a vendor");
                await send("/api/v1/requisitions/" + req.id + "/send-for-approval", {
                  vendor_id: Number(vendor),
                  comment,
                });
                refresh();
              }}
            />
          </div>
        )}
      </RoleAction>
    </section>
  );
}
function Audit({ id }) {
  const { data, error } = useLoad("/api/v1/requisitions/" + id + "/audit");
  return (
    <section className="panel form-panel">
      <h2>Audit timeline</h2>
      <p className="muted">
        Server-recorded actions. Records cannot be edited through the application.
      </p>
      <ErrorBox error={error} />
      <div className="timeline">
        {data?.map((a) => (
          <div key={a.id}>
            <span className="timeline-dot" />
            <strong>{human(a.action)}</strong>
            <small>
              {a.actor} · {new Date(a.timestamp).toLocaleString()}
            </small>
            <p>{JSON.stringify(a.details)}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
function Vendors() {
  const { user } = useAuth(),
    { data, error, refresh } = useLoad("/api/v1/vendors"),
    [editing, setEditing] = useState(null),
    [show, setShow] = useState(false),
    [risk, setRisk] = useState(null),
    [riskError, setRiskError] = useState("");
  return (
    <>
      <Header
        title="Vendor network"
        subtitle="Keep supplier records and performance evidence together."
      >
        <RoleAction user={user} roles={["procurement"]}>
          <button
            className="primary"
            onClick={() => {
              setEditing(null);
              setShow(!show);
            }}
          >
            <Plus size={16} /> Add vendor
          </button>
        </RoleAction>
      </Header>
      <ErrorBox error={error || riskError} />
      {show && (
        <VendorForm
          key={editing?.id || "new"}
          vendor={editing}
          onDone={() => {
            setShow(false);
            refresh();
          }}
        />
      )}
      <section className="panel">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Vendor</th>
                <th>Contact</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {data?.map((v) => (
                <tr key={v.id}>
                  <td>
                    <strong>{v.name}</strong>
                    <small>VEN-{String(v.id).padStart(3, "0")}</small>
                  </td>
                  <td>
                    {v.email}
                    <small>{v.contact}</small>
                  </td>
                  <td>
                    <Badge value={v.active ? "ACTIVE" : "INACTIVE"} />
                  </td>
                  <td>
                    <button
                      className="link"
                      onClick={async () => {
                        try {
                          setRisk({
                            ...(await api("/api/v1/vendors/" + v.id + "/risk")),
                            name: v.name,
                          });
                          setRiskError("");
                        } catch (e) {
                          setRiskError(e.message);
                        }
                      }}
                    >
                      View risk
                    </button>
                    <RoleAction user={user} roles={["procurement"]}>
                      <button
                        className="link"
                        onClick={() => {
                          setEditing(v);
                          setShow(true);
                        }}
                      >
                        Edit
                      </button>
                    </RoleAction>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      {risk && (
        <section className="panel form-panel">
          <h2>{risk.name} · risk explanation</h2>
          <Badge value={risk.band} />
          <strong>{risk.score === null ? " Not scored" : " " + risk.score + " / 100"}</strong>
          <p>{risk.reason}</p>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Factor</th>
                  <th>Observations</th>
                  <th>Weight</th>
                  <th>Contribution</th>
                </tr>
              </thead>
              <tbody>
                {risk.factors.map((f) => (
                  <tr key={f.factor}>
                    <td>{human(f.factor)}</td>
                    <td>
                      {f.numerator} / {f.denominator}
                    </td>
                    <td>{f.weight}%</td>
                    <td>{f.contribution ?? "Unknown"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </>
  );
}
function VendorForm({ vendor, onDone }) {
  const [form, setForm] = useState(
    vendor
      ? { name: vendor.name, email: vendor.email, contact: vendor.contact, active: vendor.active }
      : { name: "", email: "", contact: "", active: true },
  );
  return (
    <section className="panel form-panel">
      <h2>{vendor ? "Edit vendor" : "New vendor"}</h2>
      <ActionForm
        label="Save vendor"
        onSubmit={async () => {
          await send(
            "/api/v1/vendors" + (vendor ? "/" + vendor.id : ""),
            form,
            vendor ? "PUT" : "POST",
          );
          onDone();
        }}
      >
        <div className="grid3">
          {["name", "email", "contact"].map((k) => (
            <Field label={human(k)} key={k}>
              <input
                required={k !== "contact"}
                type={k === "email" ? "email" : "text"}
                value={form[k]}
                onChange={(e) => setForm({ ...form, [k]: e.target.value })}
              />
            </Field>
          ))}
        </div>
        <label className="checkbox">
          <input
            type="checkbox"
            checked={form.active}
            onChange={(e) => setForm({ ...form, active: e.target.checked })}
          />{" "}
          Active vendor
        </label>
      </ActionForm>
    </section>
  );
}
function Approvals() {
  const { data, error } = useLoad("/api/v1/approvals/inbox");
  return (
    <>
      <Header
        title="Approval inbox"
        subtitle="Requests waiting for your approval level. Review the comparison before deciding."
      />
      <ErrorBox error={error} />
      <section className="panel">
        <RequestTable rows={data} />
      </section>
    </>
  );
}
function PO() {
  const { id } = useParams(),
    { user } = useAuth(),
    { data, error, refresh } = useLoad("/api/v1/purchase-orders/" + id),
    [delivery, setDelivery] = useState({
      status: "DELIVERED",
      delivered_at: new Date().toLocaleDateString("en-CA"),
      notes: "",
    }),
    [invoice, setInvoice] = useState({
      invoice_number: "",
      invoice_date: new Date().toLocaleDateString("en-CA"),
      amount: "",
    });
  if (!data)
    return (
      <>
        <ErrorBox error={error} />
        <Empty>Loading purchase order…</Empty>
      </>
    );
  const q = data.snapshot_json.quotation;
  return (
    <>
      <Header
        title={data.po_number}
        eyebrow="PURCHASE ORDER"
        subtitle="Issued values are preserved as an immutable snapshot."
      >
        <button className="secondary no-print" onClick={() => window.print()}>
          Print purchase order
        </button>
      </Header>
      <ErrorBox error={error} />
      <section className="panel form-panel print-order">
        <div className="po-heading">
          <div>
            <h2>{q.vendor.name}</h2>
            <p>{q.vendor.email}</p>
            <p>{q.vendor.contact}</p>
          </div>
          <div>
            <Badge value={data.status} />
            <p>Issued {new Date(data.issued_at).toLocaleDateString()}</p>
            <p>Quotation {q.quotation_number}</p>
          </div>
        </div>
        <h3>{data.snapshot_json.requisition.title}</h3>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Item</th>
                <th>Quantity</th>
                <th>Unit price</th>
                <th>Tax</th>
                <th>Discount</th>
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              {q.items.map((l) => (
                <tr key={l.id}>
                  <td>
                    {
                      data.snapshot_json.items.find((i) => i.id === l.requisition_item_id)
                        ?.item_name
                    }
                  </td>
                  <td>{l.quantity}</td>
                  <td>{cash(l.unit_price)}</td>
                  <td>{cash(l.tax)}</td>
                  <td>{cash(l.discount)}</td>
                  <td>{cash(l.line_total)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="total-preview">
          Total payable <strong>{cash(data.total)}</strong>
        </div>
        <p>
          Delivery within {q.delivery_days} days · {q.delivery_terms}
        </p>
      </section>
      <div className="no-print">
        <section className="panel form-panel">
          <h2>Delivery & invoice</h2>
          {data.deliveries.map((d) => (
            <p key={d.id}>
              <Badge value={d.status} /> {d.delivered_at} · {d.notes}
            </p>
          ))}
          <RoleAction user={user} roles={["procurement", "finance_admin"]}>
            {data.requisition_status === "PO_ISSUED" && (
              <ActionForm
                label="Record delivery"
                onSubmit={async () => {
                  await send("/api/v1/purchase-orders/" + id + "/delivery", delivery);
                  refresh();
                }}
              >
                <div className="grid2">
                  <Field label="Delivery status">
                    <select
                      value={delivery.status}
                      onChange={(e) => setDelivery({ ...delivery, status: e.target.value })}
                    >
                      <option>DELIVERED</option>
                      <option>PARTIAL</option>
                    </select>
                  </Field>
                  <Field label="Delivery date">
                    <input
                      required
                      type="date"
                      value={delivery.delivered_at}
                      onChange={(e) => setDelivery({ ...delivery, delivered_at: e.target.value })}
                    />
                  </Field>
                </div>
                <Field label="Delivery notes">
                  <textarea
                    required
                    minLength={3}
                    value={delivery.notes}
                    onChange={(e) => setDelivery({ ...delivery, notes: e.target.value })}
                  />
                </Field>
              </ActionForm>
            )}
          </RoleAction>
          <RoleAction user={user} roles={["finance_admin"]}>
            {data.requisition_status === "DELIVERED" && (
              <ActionForm
                label="Record invoice"
                onSubmit={async () => {
                  await send("/api/v1/purchase-orders/" + id + "/invoice", invoice);
                  refresh();
                }}
              >
                <div className="grid3">
                  {[
                    ["Invoice number", "invoice_number", "text"],
                    ["Invoice date", "invoice_date", "date"],
                    ["Invoice amount (INR)", "amount", "number"],
                  ].map(([label, k, type]) => (
                    <Field label={label} key={k}>
                      <input
                        required
                        min={type === "number" ? ".01" : undefined}
                        step=".01"
                        type={type}
                        value={invoice[k]}
                        onChange={(e) => setInvoice({ ...invoice, [k]: e.target.value })}
                      />
                    </Field>
                  ))}
                </div>
              </ActionForm>
            )}
          </RoleAction>
          {data.invoice && (
            <div className="invoice-summary">
              <h3>
                Invoice {data.invoice.invoice_number} · {cash(data.invoice.amount)}
              </h3>
              <Badge value={data.invoice.status} />
              <p className={data.invoice.mismatch_flag ? "warning" : "muted"}>
                {data.invoice.mismatch_reason}
              </p>
              <Docs documents={data.documents} />
              <RoleAction user={user} roles={["finance_admin"]}>
                {data.requisition_status === "INVOICED" && (
                  <>
                    {!data.documents.length && (
                      <Upload path={"invoices/" + data.invoice.id} onDone={refresh} />
                    )}
                    <h3>Complete the workflow</h3>
                    <p>Record your review, including any invoice discrepancy.</p>
                    <CommentAction
                      label="Close requisition"
                      onSubmit={async (comment) => {
                        await send("/api/v1/purchase-orders/" + id + "/close", { comment });
                        refresh();
                      }}
                    />
                  </>
                )}
              </RoleAction>
              {data.invoice.resolution_comment && (
                <p>Final review: {data.invoice.resolution_comment}</p>
              )}
            </div>
          )}
        </section>
        <Link className="link" to={"/requisitions/" + data.requisition_id}>
          Back to requisition and audit trail
        </Link>
      </div>
    </>
  );
}
function Operations() {
  const { data: health, error } = useLoad("/health"),
    { data: metrics, error: metricError } = useLoad("/metrics"),
    { data: profiles, refresh } = useLoad("/api/v1/profiles"),
    { data: rules } = useLoad("/api/v1/approval-rules");
  return (
    <>
      <Header
        title="Operations"
        subtitle="Service health, approval policy and access administration."
      />
      <ErrorBox error={error || metricError} />
      <div className="grid2">
        <section className="panel form-panel">
          <h2>Service health</h2>
          <pre>{JSON.stringify(health, null, 2)}</pre>
        </section>
        <section className="panel form-panel">
          <h2>Operational counters</h2>
          <pre>{JSON.stringify(metrics, null, 2)}</pre>
        </section>
      </div>
      <section className="panel form-panel">
        <h2>Approval policy</h2>
        {rules?.map((r) => (
          <p key={r.id}>
            Level {r.level} · {r.name} · {cash(r.min_amount)} and above · {human(r.required_role)}
          </p>
        ))}
        <small>
          Policy changes require the database operator; pending requests retain their original
          policy snapshot.
        </small>
      </section>
      <section className="panel form-panel">
        <h2>Access administration</h2>
        {profiles?.map((p) => (
          <ProfileEditor key={p.id} profile={p} refresh={refresh} />
        ))}
      </section>
    </>
  );
}
function ProfileEditor({ profile, refresh }) {
  const { user } = useAuth(),
    [role, setRole] = useState(profile.role),
    [active, setActive] = useState(profile.active);
  return (
    <ActionForm
      className="profile-editor"
      label="Update access"
      onSubmit={async () => {
        await send(
          "/api/v1/profiles/" + profile.id,
          { role, active, department_id: profile.department_id },
          "PATCH",
        );
        refresh();
      }}
    >
      <strong>
        {profile.email}
        {profile.id === user.id ? " (your account)" : ""}
      </strong>
      <div className="grid2">
        <Field label="Role">
          <select
            disabled={profile.id === user.id}
            value={role}
            onChange={(e) => setRole(e.target.value)}
          >
            {["requester", "procurement", "approver", "finance_admin"].map((r) => (
              <option key={r}>{r}</option>
            ))}
          </select>
        </Field>
        <label className="checkbox">
          <input
            type="checkbox"
            checked={active}
            disabled={profile.id === user.id}
            onChange={(e) => setActive(e.target.checked)}
          />{" "}
          Active account
        </label>
      </div>
    </ActionForm>
  );
}
