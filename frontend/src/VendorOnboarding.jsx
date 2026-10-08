import React, { useCallback, useEffect, useState } from "react";
import { ArrowUpRight, ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";
import { api, send } from "./api";
import { Badge, Empty, Field } from "./components";
import "./vendor-onboarding.css";

function ErrorBox({ error }) {
  return error ? <p className="error" role="alert">{error}</p> : null;
}

export function VendorApplicationPage() {
  const initial = {
    legal_name: "",
    trading_name: "",
    contact_name: "",
    email: "",
    phone: "",
    tax_id: "",
    registration_number: "",
    address: "",
    categories: "",
    website: "",
    years_in_business: 0,
    notes: "",
    declaration: false,
  };
  const [form, setForm] = useState(initial);
  const [submitted, setSubmitted] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const update = (key, value) => setForm((current) => ({ ...current, [key]: value }));

  const submit = async (event) => {
    event.preventDefault();
    if (!form.declaration) {
      setError("Confirm the supplier declaration before submitting.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const result = await send("/api/v1/vendor-applications", {
        ...form,
        years_in_business: Number(form.years_in_business || 0),
      });
      setSubmitted(result);
      sessionStorage.setItem(
        "procure-supplier-application",
        JSON.stringify({
          application_number: result.application_number,
          email: result.email,
        }),
      );
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="auth-portal vendor-auth supplier-application-page">
      <div className="auth-grid-bg" aria-hidden="true" />
      <div className="auth-orb auth-orb-one" aria-hidden="true" />
      <div className="auth-orb auth-orb-two" aria-hidden="true" />
      <header className="auth-topline">
        <div className="brand">
          <span className="brand-icon">p.</span>procure<span className="brand-dot">/</span>
        </div>
        <Link className="portal-switch-link" to="/vendor-login">
          Vendor portal <ArrowUpRight size={15} />
        </Link>
      </header>

      <main className="supplier-application-wrap">
        <section className="supplier-application-intro">
          <div className="portal-kicker"><span className="portal-pulse" />Supplier onboarding</div>
          <p className="eyebrow">SMART PROCUREMENT INTELLIGENCE HUB</p>
          <h1>Apply to join the vendor network.</h1>
          <p>
            Procurement reviews each supplier before RFQ access is enabled.
            Approval creates a provisional profile, not a fake historical risk score.
          </p>
          <div className="supplier-process">
            <span><b>01</b> Submit company details</span>
            <span><b>02</b> Procurement review</span>
            <span><b>03</b> Approved as provisional</span>
            <span><b>04</b> Build history through orders</span>
          </div>
        </section>

        <section className="supplier-apply-card">
          {submitted ? (
            <div className="supplier-application-success">
              <ShieldCheck size={34} />
              <p className="eyebrow">APPLICATION RECEIVED</p>
              <h2>Pending procurement review</h2>
              <p>
                Reference <strong>{submitted.application_number}</strong>.
                No vendor account or performance score has been created yet.
              </p>
              <p className="notice">
                If Procurement approves this application, return to the vendor portal
                and create a supplier account using <strong>{submitted.email}</strong>.
              </p>
              <div className="supplier-success-actions">
                <Link
                  className="primary supplier-back-link"
                  to={`/vendor-status?ref=${encodeURIComponent(submitted.application_number)}`}
                >
                  Track application status
                </Link>
                <Link className="secondary supplier-back-link" to="/vendor-login">
                  Return to vendor portal
                </Link>
              </div>
            </div>
          ) : (
            <>
              <div className="section-head">
                <div>
                  <p className="eyebrow">NEW SUPPLIER</p>
                  <h2>Organisation details</h2>
                  <p className="muted">Submit accurate legal and contact information for Procurement review.</p>
                </div>
                <Badge value="PENDING REVIEW" />
              </div>

              <form onSubmit={submit}>
                <fieldset disabled={busy}>
                  <div className="grid2 supplier-form-grid">
                    <Field label="Legal company name"><input required value={form.legal_name} onChange={(e) => update("legal_name", e.target.value)} /></Field>
                    <Field label="Trading name (optional)"><input value={form.trading_name} onChange={(e) => update("trading_name", e.target.value)} /></Field>
                    <Field label="Primary contact person"><input required value={form.contact_name} onChange={(e) => update("contact_name", e.target.value)} /></Field>
                    <Field label="Business email"><input required type="email" value={form.email} onChange={(e) => update("email", e.target.value)} /></Field>
                    <Field label="Phone"><input required value={form.phone} onChange={(e) => update("phone", e.target.value)} /></Field>
                    <Field label="GST / tax registration ID"><input required value={form.tax_id} onChange={(e) => update("tax_id", e.target.value)} /></Field>
                    <Field label="Company registration / CIN"><input required value={form.registration_number} onChange={(e) => update("registration_number", e.target.value)} /></Field>
                    <Field label="Years in business"><input type="number" min="0" max="200" value={form.years_in_business} onChange={(e) => update("years_in_business", e.target.value)} /></Field>
                    <Field label="Website (optional)"><input value={form.website} onChange={(e) => update("website", e.target.value)} placeholder="https://company.example" /></Field>
                    <Field label="Products / service categories"><input required value={form.categories} onChange={(e) => update("categories", e.target.value)} placeholder="IT hardware, networking, support" /></Field>
                  </div>
                  <Field label="Registered business address"><textarea required rows="3" value={form.address} onChange={(e) => update("address", e.target.value)} /></Field>
                  <Field label="Additional information (optional)">
                    <textarea rows="3" value={form.notes} onChange={(e) => update("notes", e.target.value)} placeholder="References, certifications, coverage area or relevant supplier information" />
                  </Field>
                  <label className="checkbox supplier-declaration">
                    <input type="checkbox" checked={form.declaration} onChange={(e) => update("declaration", e.target.checked)} />
                    I confirm that the submitted supplier information is accurate and may be reviewed by the Procurement team.
                  </label>
                  <ErrorBox error={error} />
                  <button className="primary" type="submit">{busy ? "Submitting..." : "Submit supplier application"}</button>
                </fieldset>
              </form>

              <div className="supplier-form-footer">
                <span>Already approved?</span>
                <Link className="link" to="/vendor-login">Go to vendor sign in</Link>
              </div>
            </>
          )}
        </section>
      </main>
    </div>
  );
}

export function VendorApplicationStatusPage({ embedded = false }) {
  const saved = (() => {
    try {
      return JSON.parse(sessionStorage.getItem("procure-supplier-application") || "{}");
    } catch {
      return {};
    }
  })();
  const queryRef = new URLSearchParams(window.location.search).get("ref") || "";
  const [reference, setReference] = useState(queryRef || saved.application_number || "");
  const [email, setEmail] = useState(saved.email || "");
  const [application, setApplication] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const track = async (event) => {
    event?.preventDefault();
    setBusy(true);
    setError("");
    try {
      const result = await send("/api/v1/vendor-applications/track", {
        application_number: reference.trim(),
        email: email.trim(),
      });
      setApplication(result);
      sessionStorage.setItem(
        "procure-supplier-application",
        JSON.stringify({
          application_number: result.application_number,
          email: result.email,
        }),
      );
    } catch (e) {
      setApplication(null);
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  const statusLabel = {
    PENDING: "PENDING REVIEW",
    APPROVED: "APPROVED",
    REJECTED: "REJECTED",
  }[application?.status] || application?.status;

  const progress = application
    ? [
        { label: "Application submitted", state: "done" },
        { label: "Procurement review", state: application.status === "PENDING" ? "current" : "done" },
        {
          label: application.status === "REJECTED" ? "Application rejected" : "Supplier decision",
          state:
            application.status === "PENDING"
              ? "upcoming"
              : application.status === "REJECTED"
                ? "rejected"
                : "done",
        },
        {
          label: application.status === "APPROVED" ? "Vendor portal access available" : "Vendor portal access",
          state: application.status === "APPROVED" ? "current" : "upcoming",
        },
      ]
    : [];

  const content = (
    <section className="supplier-status-card">
      {!application ? (
        <>
          <div className="section-head">
            <div>
              <p className="eyebrow">TRACK APPLICATION</p>
              <h2>Check current status</h2>
              <p className="muted">Both details must match the original supplier application.</p>
            </div>
          </div>
          <form onSubmit={track}>
            <fieldset disabled={busy}>
              <Field label="Application reference">
                <input
                  required
                  value={reference}
                  onChange={(e) => setReference(e.target.value.toUpperCase())}
                  placeholder="SUP-2026-ABC123"
                />
              </Field>
              <Field label="Business email">
                <input
                  required
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="supplier@company.com"
                />
              </Field>
              <ErrorBox error={error} />
              <button className="primary" type="submit">
                {busy ? "Checking…" : "Check application status"}
              </button>
            </fieldset>
          </form>
          <div className="supplier-form-footer">
            <span>Not applied yet?</span>
            <Link className="link" to="/vendor-apply">Apply to become a vendor</Link>
          </div>
        </>
      ) : (
        <div className="supplier-status-dashboard">
          <div className="supplier-status-head">
            <div>
              <p className="eyebrow">SUPPLIER APPLICATION</p>
              <h2>{application.trading_name || application.legal_name}</h2>
              <p className="muted">{application.application_number} · {application.email}</p>
            </div>
            <Badge value={statusLabel} />
          </div>

          <div className={`supplier-status-banner ${application.status.toLowerCase()}`}>
            <span>Current status</span>
            <strong>{statusLabel}</strong>
            {application.status === "PENDING" && (
              <p>Your application is waiting for a Procurement decision.</p>
            )}
            {application.status === "APPROVED" && (
              <p>
                Your organisation has been approved. Supplier portal access can now be created
                with the approved business email.
              </p>
            )}
            {application.status === "REJECTED" && (
              <p>
                Procurement did not approve this application. Review the decision note before
                submitting corrected information.
              </p>
            )}
          </div>

          <div className="supplier-tracking-grid">
            <div>
              <small>Submitted</small>
              <strong>{new Date(application.submitted_at).toLocaleString()}</strong>
            </div>
            <div>
              <small>Products / services</small>
              <strong>{application.categories}</strong>
            </div>
            <div>
              <small>Decision date</small>
              <strong>
                {application.reviewed_at
                  ? new Date(application.reviewed_at).toLocaleString()
                  : "Awaiting review"}
              </strong>
            </div>
            <div>
              <small>Performance lifecycle</small>
              <strong>{application.performance?.lifecycle || "Not started"}</strong>
            </div>
          </div>

          <div className="supplier-status-progress">
            <p className="eyebrow">APPLICATION PROGRESS</p>
            {progress.map((item, index) => (
              <div className={`supplier-progress-row ${item.state}`} key={item.label}>
                <span className="supplier-progress-index">
                  {item.state === "done" ? "✓" : String(index + 1).padStart(2, "0")}
                </span>
                <div>
                  <strong>{item.label}</strong>
                  {item.state === "current" && <small>Current stage</small>}
                  {item.state === "upcoming" && <small>Not available yet</small>}
                  {item.state === "rejected" && <small>Application closed</small>}
                </div>
              </div>
            ))}
          </div>

          {application.review_comment && (
            <div className="supplier-decision-note">
              <small>Procurement decision note</small>
              <p>{application.review_comment}</p>
            </div>
          )}

          {application.status === "APPROVED" && (
            <div className="supplier-approved-summary">
              <div>
                <small>Supplier status</small>
                <strong>{application.performance?.band || "NEW_VENDOR"}</strong>
              </div>
              <div>
                <small>Risk score</small>
                <strong>
                  {application.performance?.score == null ? "Not scored" : application.performance.score}
                </strong>
              </div>
              <div>
                <small>Observed orders</small>
                <strong>{application.performance?.total_orders ?? 0}</strong>
              </div>
            </div>
          )}

          <div className="supplier-status-actions">
            {application.portal_access && (
              <Link className="primary supplier-back-link" to="/vendor-login">
                Create / sign in to supplier account
              </Link>
            )}
            {application.status === "REJECTED" && (
              <Link className="primary supplier-back-link" to="/vendor-apply">
                Submit a new application
              </Link>
            )}
            <button
              className="secondary"
              onClick={() => {
                setApplication(null);
                setError("");
              }}
            >
              Check another application
            </button>
          </div>
        </div>
      )}
    </section>
  );

  if (embedded) return content;

  return (
    <div className="auth-portal vendor-auth supplier-status-page">
      <div className="auth-grid-bg" aria-hidden="true" />
      <div className="auth-orb auth-orb-one" aria-hidden="true" />
      <div className="auth-orb auth-orb-two" aria-hidden="true" />
      <header className="auth-topline">
        <div className="brand">
          <span className="brand-icon">p.</span>procure<span className="brand-dot">/</span>
        </div>
        <Link className="portal-switch-link" to="/vendor-login">
          Vendor portal <ArrowUpRight size={15} />
        </Link>
      </header>
      <main className="supplier-status-wrap">
        <section className="supplier-status-intro">
          <div className="portal-kicker"><span className="portal-pulse" />Supplier onboarding</div>
          <p className="eyebrow">APPLICATION TRACKER</p>
          <h1>Follow your supplier application.</h1>
          <p>
            Use the reference issued after submission together with the registered business email.
            Vendor portal access remains locked until Procurement approves the application.
          </p>
        </section>
        {content}
      </main>
    </div>
  );
}


export function VendorApplicationsPanel({ onVendorChanged }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const refresh = useCallback(async () => {
    try {
      setData(await api("/api/v1/vendor-applications"));
      setError("");
    } catch (e) {
      setError(e.message);
    }
  }, []);
  useEffect(() => { refresh(); }, [refresh]);

  const pending = data?.filter((item) => item.status === "PENDING") || [];
  return (
    <section className="panel vendor-applications-panel">
      <div className="section-head">
        <div>
          <p className="eyebrow">SUPPLIER ONBOARDING</p>
          <h2>Vendor applications</h2>
          <p className="muted">Review supplier identity and business details before enabling RFQ access.</p>
        </div>
        <Badge value={`${pending.length} PENDING`} />
      </div>
      <ErrorBox error={error} />
      {!data && <Empty>Loading supplier applications...</Empty>}
      {data?.length === 0 && <Empty>No supplier applications have been submitted.</Empty>}
      <div className="vendor-application-list">
        {data?.map((application) => (
          <VendorApplicationReview
            key={application.id}
            application={application}
            onDone={() => { refresh(); onVendorChanged?.(); }}
          />
        ))}
      </div>
    </section>
  );
}

function VendorApplicationReview({ application, onDone }) {
  const [comment, setComment] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const decide = async (decision) => {
    if (comment.trim().length < 5) {
      setError("Add a review comment of at least 5 characters.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      await send(`/api/v1/vendor-applications/${application.id}/decision`, {
        decision,
        comment: comment.trim(),
      });
      setComment("");
      onDone();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <article className={`vendor-application-card ${application.status.toLowerCase()}`}>
      <div className="vendor-application-card-head">
        <div>
          <small>{application.application_number}</small>
          <h3>{application.trading_name || application.legal_name}</h3>
          <span>{application.legal_name}</span>
        </div>
        <Badge value={application.status} />
      </div>

      <div className="vendor-application-facts">
        <span><small>Contact</small><b>{application.contact_name}</b>{application.email}<br />{application.phone}</span>
        <span><small>Tax / registration</small><b>{application.tax_id}</b>{application.registration_number}</span>
        <span><small>Categories</small><b>{application.categories}</b>{application.years_in_business} years in business</span>
        <span><small>Address</small><b>{application.address}</b>{application.website || "No website supplied"}</span>
      </div>

      {application.notes && <p className="application-notes">{application.notes}</p>}

      {application.status === "PENDING" ? (
        <div className="application-review-box">
          <Field label="Supplier-facing decision comment">
            <textarea rows="2" value={comment} onChange={(e) => setComment(e.target.value)} placeholder="State the decision clearly. This note is visible to the supplier after approval/rejection." />
          </Field>
          <ErrorBox error={error} />
          <div className="application-review-actions">
            <button className="primary" disabled={busy} onClick={() => decide("APPROVED")}>Approve supplier</button>
            <button className="secondary" disabled={busy} onClick={() => decide("REJECTED")}>Reject application</button>
          </div>
        </div>
      ) : (
        <div className="application-reviewed">
          <span>Reviewed decision</span>
          <strong>{application.review_comment}</strong>
          {application.vendor && <small>Vendor profile: {application.vendor.name}</small>}
        </div>
      )}
    </article>
  );
}
