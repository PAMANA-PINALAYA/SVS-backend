import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import hashlib
import os

class DatabaseManager:
    def __init__(self):
        self.db_config = {
            "dbname": "SmartSurveillanceSystem",
            "user": "postgres",
            "password": "123",
            "host": "localhost",
            "port": "5432"
        }
        self.init_database()

    def get_admin_info(self, email):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, full_name, photo FROM admin_users WHERE email = %s AND is_active = TRUE
        ''', (email,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return {"id": result[0], "full_name": result[1], "photo": result[2]}
        else:
            return {"id": None, "full_name": "Unknown", "photo": "policeman.png"}
            
    def get_connection(self):
        import psycopg2
        import os
        return psycopg2.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            dbname=os.environ.get("DB_NAME", "SmartSurveillanceSystem"),
            user=os.environ.get("DB_USER", "postgres"),
            password=os.environ.get("DB_PASS", "123")
        )

    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create admin users table with photo
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                full_name VARCHAR(255) NOT NULL,
                photo VARCHAR(255) DEFAULT 'policeman.png',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')

        # Create superadmin users table with photo
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS superadmin_users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                full_name VARCHAR(255) NOT NULL,
                admin_key VARCHAR(100) NOT NULL,
                photo VARCHAR(255) DEFAULT 'policeman.png',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')    

        # Create password reset tokens table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) NOT NULL,
                token VARCHAR(255) NOT NULL,
                user_type VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                used BOOLEAN DEFAULT FALSE
            )
        ''')

        self.create_default_users(cursor)
        conn.commit()
        conn.close()

    def create_default_users(self, cursor):
        admin_password = self.hash_password("admin123")
        cursor.execute('''
            INSERT INTO admin_users (email, password, full_name, photo)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        ''', ("admin@test.com", admin_password, "Default Admin", "policeman.png"))

        superadmin_password = self.hash_password("super123")
        cursor.execute('''
            INSERT INTO superadmin_users (email, password, full_name, admin_key, photo)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        ''', ("superadmin@test.com", superadmin_password, "Default SuperAdmin", "SUPER2024", "policeman.png"))

    def hash_password(self, password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def verify_admin_login(self, email, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        hashed_password = self.hash_password(password)
        cursor.execute("""
            SELECT id, full_name, photo FROM admin_users
            WHERE email = %s AND password = %s AND is_active = TRUE
        """, (email.strip(), hashed_password))
        result = cursor.fetchone()
        if result:
            cursor.execute("UPDATE admin_users SET last_login = NOW() WHERE id = %s", (result[0],))
            conn.commit()
        conn.close()
        return result
    
    def verify_superadmin_login(self, email, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        hashed_password = self.hash_password(password)
        cursor.execute('''
            SELECT id, full_name, photo FROM superadmin_users 
            WHERE email = %s AND password = %s AND is_active = TRUE
        ''', (email, hashed_password))
        result = cursor.fetchone()
        if result:
            cursor.execute('''
                UPDATE superadmin_users SET last_login = CURRENT_TIMESTAMP WHERE email = %s
            ''', (email,))
            conn.commit()
        conn.close()
        return result

    def register_admin(self, email, password, full_name, photo="policeman.png"):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            hashed_password = self.hash_password(password)
            cursor.execute('''
                INSERT INTO admin_users (email, password, full_name, photo)
                VALUES (%s, %s, %s, %s)
            ''', (email, hashed_password, full_name, photo))
            conn.commit()
            success = True
        except psycopg2.Error:
            success = False
        finally:
            conn.close()
        return success

    def register_superadmin(self, email, password, full_name, admin_key, photo="policeman.png"):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            hashed_password = self.hash_password(password)
            cursor.execute('''
                INSERT INTO superadmin_users (email, password, full_name, admin_key, photo)
                VALUES (%s, %s, %s, %s, %s)
            ''', (email, hashed_password, full_name, admin_key, photo))
            conn.commit()
            success = True
        except psycopg2.Error:
            success = False
        finally:
            conn.close()
        return success

    def update_password(self, email, new_password, user_type):
        conn = self.get_connection()
        cursor = conn.cursor()
        hashed_password = self.hash_password(new_password)
        table = "admin_users" if user_type == "admin" else "superadmin_users"
        cursor.execute(sql.SQL('''
            UPDATE {} SET password = %s WHERE email = %s
        ''').format(sql.Identifier(table)), (hashed_password, email))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    def get_user_stats(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM admin_users WHERE is_active = TRUE')
        admin_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM superadmin_users WHERE is_active = TRUE')
        superadmin_count = cursor.fetchone()[0]
        conn.close()
        return {"admin_count": admin_count, "superadmin_count": superadmin_count}

    
db_manager = DatabaseManager()