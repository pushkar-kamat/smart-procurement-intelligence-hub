BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 2305dc836ec3

CREATE TABLE approval_rules (
    id SERIAL NOT NULL, 
    name VARCHAR(100) NOT NULL, 
    min_amount NUMERIC(16, 2) NOT NULL, 
    max_amount NUMERIC(16, 2), 
    required_role VARCHAR(30) NOT NULL, 
    level INTEGER NOT NULL, 
    active BOOLEAN NOT NULL, 
    PRIMARY KEY (id)
);

CREATE TABLE departments (
    id SERIAL NOT NULL, 
    name VARCHAR(120) NOT NULL, 
    cost_center VARCHAR(40) NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (name)
);

CREATE TABLE price_history (
    id SERIAL NOT NULL, 
    item_name VARCHAR(120) NOT NULL, 
    category VARCHAR(80) NOT NULL, 
    unit VARCHAR(30) NOT NULL, 
    unit_price NUMERIC(16, 2) NOT NULL, 
    observed_at DATE NOT NULL, 
    source VARCHAR(120) NOT NULL, 
    PRIMARY KEY (id)
);

CREATE INDEX ix_price_history_category ON price_history (category);

CREATE INDEX ix_price_history_item_name ON price_history (item_name);

CREATE TABLE vendors (
    id SERIAL NOT NULL, 
    name VARCHAR(120) NOT NULL, 
    email VARCHAR(254) NOT NULL, 
    contact VARCHAR(80), 
    active BOOLEAN NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    UNIQUE (name)
);

CREATE TABLE profiles (
    id SERIAL NOT NULL, 
    supabase_user_id VARCHAR(64) NOT NULL, 
    email VARCHAR(254) NOT NULL, 
    name VARCHAR(120) NOT NULL, 
    role VARCHAR(30) NOT NULL, 
    department_id INTEGER, 
    active BOOLEAN NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    CHECK (role IN ('requester','procurement','approver','finance_admin')), 
    FOREIGN KEY(department_id) REFERENCES departments (id), 
    UNIQUE (email), 
    UNIQUE (supabase_user_id)
);

CREATE TABLE vendor_history (
    id SERIAL NOT NULL, 
    vendor_id INTEGER NOT NULL, 
    total_orders INTEGER NOT NULL, 
    completed_orders INTEGER NOT NULL, 
    late_deliveries INTEGER NOT NULL, 
    anomalous_lines INTEGER NOT NULL, 
    quotation_lines INTEGER NOT NULL, 
    disputed_orders INTEGER NOT NULL, 
    incomplete_orders INTEGER NOT NULL, 
    invoice_mismatches INTEGER NOT NULL, 
    invoiced_orders INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(vendor_id) REFERENCES vendors (id), 
    UNIQUE (vendor_id)
);

CREATE TABLE requisitions (
    id SERIAL NOT NULL, 
    requester_id INTEGER NOT NULL, 
    department_id INTEGER NOT NULL, 
    title VARCHAR(180) NOT NULL, 
    justification VARCHAR(2000) NOT NULL, 
    status VARCHAR(32) NOT NULL, 
    estimated_total NUMERIC(16, 2) NOT NULL, 
    preferred_vendor_id INTEGER, 
    approval_plan JSON, 
    created_at TIMESTAMP WITH TIME ZONE, 
    submitted_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    CHECK (status IN ('DRAFT','SUBMITTED','SOURCING','QUOTATIONS_RECEIVED','COMPARISON_READY','PENDING_APPROVAL','APPROVED','REJECTED','PO_ISSUED','DELIVERED','INVOICED','CLOSED','CANCELLED')), 
    FOREIGN KEY(department_id) REFERENCES departments (id), 
    FOREIGN KEY(preferred_vendor_id) REFERENCES vendors (id), 
    FOREIGN KEY(requester_id) REFERENCES profiles (id)
);

CREATE INDEX ix_requisitions_requester_id ON requisitions (requester_id);

CREATE INDEX ix_requisitions_status ON requisitions (status);

CREATE TABLE approvals (
    id SERIAL NOT NULL, 
    requisition_id INTEGER NOT NULL, 
    approver_id INTEGER NOT NULL, 
    approval_level INTEGER NOT NULL, 
    decision VARCHAR(20) NOT NULL, 
    comment VARCHAR(2000) NOT NULL, 
    decided_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(approver_id) REFERENCES profiles (id), 
    FOREIGN KEY(requisition_id) REFERENCES requisitions (id), 
    UNIQUE (requisition_id, approval_level), 
    UNIQUE (requisition_id, approver_id)
);

CREATE INDEX ix_approvals_requisition_id ON approvals (requisition_id);

CREATE TABLE audit_logs (
    id SERIAL NOT NULL, 
    actor_user_id INTEGER, 
    requisition_id INTEGER, 
    action VARCHAR(80) NOT NULL, 
    entity_type VARCHAR(60) NOT NULL, 
    entity_id INTEGER NOT NULL, 
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL, 
    details JSON NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(actor_user_id) REFERENCES profiles (id), 
    FOREIGN KEY(requisition_id) REFERENCES requisitions (id)
);

CREATE INDEX ix_audit_logs_requisition_id ON audit_logs (requisition_id);

CREATE TABLE purchase_orders (
    id SERIAL NOT NULL, 
    requisition_id INTEGER NOT NULL, 
    vendor_id INTEGER NOT NULL, 
    po_number VARCHAR(60) NOT NULL, 
    total NUMERIC(16, 2) NOT NULL, 
    issued_at TIMESTAMP WITH TIME ZONE, 
    status VARCHAR(30), 
    snapshot_json JSON NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(requisition_id) REFERENCES requisitions (id), 
    FOREIGN KEY(vendor_id) REFERENCES vendors (id), 
    UNIQUE (po_number), 
    UNIQUE (requisition_id)
);

CREATE TABLE quotations (
    id SERIAL NOT NULL, 
    requisition_id INTEGER NOT NULL, 
    vendor_id INTEGER NOT NULL, 
    quotation_number VARCHAR(80) NOT NULL, 
    quotation_date DATE NOT NULL, 
    valid_until DATE, 
    delivery_days INTEGER NOT NULL, 
    delivery_terms VARCHAR(500), 
    subtotal NUMERIC(16, 2) NOT NULL, 
    tax_total NUMERIC(16, 2) NOT NULL, 
    discount_total NUMERIC(16, 2) NOT NULL, 
    grand_total NUMERIC(16, 2) NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(requisition_id) REFERENCES requisitions (id), 
    FOREIGN KEY(vendor_id) REFERENCES vendors (id), 
    UNIQUE (requisition_id, vendor_id)
);

CREATE INDEX ix_quotations_requisition_id ON quotations (requisition_id);

CREATE INDEX ix_quotations_vendor_id ON quotations (vendor_id);

CREATE TABLE requisition_items (
    id SERIAL NOT NULL, 
    requisition_id INTEGER NOT NULL, 
    item_name VARCHAR(120) NOT NULL, 
    category VARCHAR(80) NOT NULL, 
    description VARCHAR(500), 
    quantity NUMERIC(12, 3) NOT NULL, 
    unit VARCHAR(30) NOT NULL, 
    estimated_unit_price NUMERIC(16, 2) NOT NULL, 
    estimated_line_total NUMERIC(16, 2) NOT NULL, 
    PRIMARY KEY (id), 
    CHECK (estimated_unit_price > 0), 
    CHECK (quantity > 0), 
    FOREIGN KEY(requisition_id) REFERENCES requisitions (id)
);

CREATE INDEX ix_requisition_items_requisition_id ON requisition_items (requisition_id);

CREATE TABLE vendor_invitations (
    id SERIAL NOT NULL, 
    requisition_id INTEGER NOT NULL, 
    vendor_id INTEGER NOT NULL, 
    invited_at TIMESTAMP WITH TIME ZONE, 
    status VARCHAR(30), 
    response_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(requisition_id) REFERENCES requisitions (id), 
    FOREIGN KEY(vendor_id) REFERENCES vendors (id), 
    UNIQUE (requisition_id, vendor_id)
);

CREATE INDEX ix_vendor_invitations_requisition_id ON vendor_invitations (requisition_id);

CREATE TABLE deliveries (
    id SERIAL NOT NULL, 
    purchase_order_id INTEGER NOT NULL, 
    status VARCHAR(30) NOT NULL, 
    delivered_at DATE NOT NULL, 
    notes VARCHAR(2000) NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(purchase_order_id) REFERENCES purchase_orders (id)
);

CREATE INDEX ix_deliveries_purchase_order_id ON deliveries (purchase_order_id);

CREATE TABLE invoices (
    id SERIAL NOT NULL, 
    purchase_order_id INTEGER NOT NULL, 
    invoice_number VARCHAR(80) NOT NULL, 
    invoice_date DATE NOT NULL, 
    amount NUMERIC(16, 2) NOT NULL, 
    status VARCHAR(30) NOT NULL, 
    mismatch_flag BOOLEAN NOT NULL, 
    mismatch_reason VARCHAR(500) NOT NULL, 
    resolution_comment VARCHAR(2000), 
    PRIMARY KEY (id), 
    FOREIGN KEY(purchase_order_id) REFERENCES purchase_orders (id), 
    UNIQUE (purchase_order_id)
);

CREATE TABLE quotation_items (
    id SERIAL NOT NULL, 
    quotation_id INTEGER NOT NULL, 
    requisition_item_id INTEGER NOT NULL, 
    unit_price NUMERIC(16, 2) NOT NULL, 
    quantity NUMERIC(12, 3) NOT NULL, 
    tax NUMERIC(16, 2) NOT NULL, 
    discount NUMERIC(16, 2) NOT NULL, 
    line_total NUMERIC(16, 2) NOT NULL, 
    analysis JSON NOT NULL, 
    PRIMARY KEY (id), 
    CHECK (quantity > 0), 
    CHECK (unit_price > 0), 
    FOREIGN KEY(quotation_id) REFERENCES quotations (id), 
    FOREIGN KEY(requisition_item_id) REFERENCES requisition_items (id), 
    UNIQUE (quotation_id, requisition_item_id)
);

CREATE INDEX ix_quotation_items_quotation_id ON quotation_items (quotation_id);

CREATE TABLE documents (
    id SERIAL NOT NULL, 
    requisition_id INTEGER NOT NULL, 
    quotation_id INTEGER, 
    invoice_id INTEGER, 
    storage_key VARCHAR(200) NOT NULL, 
    backend VARCHAR(20) NOT NULL, 
    sha256 VARCHAR(64) NOT NULL, 
    original_name VARCHAR(180) NOT NULL, 
    content_type VARCHAR(60) NOT NULL, 
    size_bytes INTEGER NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    CHECK ((quotation_id IS NULL) <> (invoice_id IS NULL)), 
    FOREIGN KEY(invoice_id) REFERENCES invoices (id), 
    FOREIGN KEY(quotation_id) REFERENCES quotations (id), 
    FOREIGN KEY(requisition_id) REFERENCES requisitions (id), 
    UNIQUE (invoice_id), 
    UNIQUE (quotation_id)
);

CREATE INDEX ix_documents_requisition_id ON documents (requisition_id);

INSERT INTO alembic_version (version_num) VALUES ('2305dc836ec3') RETURNING alembic_version.version_num;

-- Running upgrade 2305dc836ec3 -> 7bfa01

ALTER TABLE "departments" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "profiles" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "vendors" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "requisitions" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "requisition_items" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "vendor_invitations" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "quotations" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "quotation_items" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "price_history" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "vendor_history" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "approval_rules" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "approvals" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "purchase_orders" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "deliveries" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "invoices" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "documents" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "audit_logs" ENABLE ROW LEVEL SECURITY;

UPDATE alembic_version SET version_num='7bfa01' WHERE alembic_version.version_num = '2305dc836ec3';

COMMIT;

