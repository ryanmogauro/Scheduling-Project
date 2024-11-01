from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
      
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE user RENAME TO user_old"))
            
    
        with db.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE user (
                    userID INTEGER NOT NULL,
                    employeeID INTEGER,
                    passwordHash VARCHAR(128) NOT NULL,
                    email VARCHAR(50) NOT NULL,
                    isActive BOOLEAN,
                    PRIMARY KEY (userID),
                    FOREIGN KEY (employeeID) REFERENCES employee (employeeID)
                )
            """))


        with db.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO user (userID, employeeID, passwordHash, email, isActive)
                SELECT userID, employeeID, passwordHash, email, isActive
                FROM user_old
            """))
            
            
        with db.engine.connect() as conn:
            conn.execute(text("DROP TABLE user_old"))

        print("Column 'username' removed successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")