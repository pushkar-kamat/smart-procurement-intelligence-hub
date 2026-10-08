"""Bootstrap the zero-Docker SQLite fallback using the current SQLAlchemy model."""
from app.core.database import Base, engine, SessionLocal
from app.seed import seed
from app.seed_vendor_marketplace import upsert as seed_marketplace
from app.seed_local_users import main as seed_local_users


def main():
    Base.metadata.create_all(engine)

    with SessionLocal.begin() as db:
        print("Synthetic seed:", "created" if seed(db) else "already present")
        print("Marketplace seed:", seed_marketplace(db))

    # Uses a separate transaction because it intentionally updates credentials.
    seed_local_users()

    print("")
    print("Local fallback database is ready.")


if __name__ == "__main__":
    main()
