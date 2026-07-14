import csv
import os
from sqlalchemy.orm import Session
from app.database.connection import SessionLocal, engine, Base
from app.models.vocabulary import Vocabulary

def init_db():
    Base.metadata.create_all(bind=engine)

def load_csv_to_db(csv_path: str):
    db: Session = SessionLocal()
    
    # Check if table already has data
    if db.query(Vocabulary).first() is not None:
        print("Database already contains vocabulary data. Skipping load.")
        db.close()
        return

    print(f"Loading data from {csv_path}...")
    try:
        with open(csv_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            count = 0
            for row in reader:
                vocab = Vocabulary(
                    expression=row.get("expression", ""),
                    reading=row.get("reading", ""),
                    meaning=row.get("meaning", ""),
                    tags=row.get("tags", "")
                )
                db.add(vocab)
                count += 1
            
            db.commit()
            print(f"Successfully loaded {count} vocabulary words.")
    except Exception as e:
        print(f"Error loading CSV: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    # Assume script is run from project root
    load_csv_to_db(os.path.join("data", "n5.csv"))
