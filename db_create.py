from umis import create_app, db  # Import your app factory and database instance

app = create_app()

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()  # Drops all tables
    print("Creating all tables...")
    db.create_all()  # Recreates all tables
    print("Database reset complete!")
