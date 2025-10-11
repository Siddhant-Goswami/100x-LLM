import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
import bcrypt
import yaml

class DatabaseManager:
    def __init__(self, db_path: str = "lead_qualification.db"):
        self.db_path = db_path
        self.init_database()
        self.create_default_users()
    
    def init_database(self):
        """Initialize the SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'enrollment',
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Leads table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                lead_id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                program TEXT,
                role TEXT,
                experience_years INTEGER,
                budget_band TEXT,
                region TEXT,
                intent_text TEXT,
                source TEXT,
                status TEXT DEFAULT 'new',
                raw_data TEXT
            )
        ''')
        
        # Decisions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS decisions (
                decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id INTEGER NOT NULL,
                decided_by INTEGER NOT NULL,
                decided_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL,
                rationale TEXT,
                confidence REAL,
                factors_json TEXT,
                override_flag BOOLEAN DEFAULT 0,
                notes TEXT,
                FOREIGN KEY (lead_id) REFERENCES leads (lead_id),
                FOREIGN KEY (decided_by) REFERENCES users (user_id)
            )
        ''')
        
        # Audit logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audits (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                action TEXT NOT NULL,
                payload_json TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_default_users(self):
        """Create default users for the system"""
        default_users = [
            {"email": "admin@company.com", "password": "admin123", "role": "admin"},
            {"email": "enrollment@company.com", "password": "enroll123", "role": "enrollment"},
            {"email": "manager@company.com", "password": "manager123", "role": "manager"}
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for user in default_users:
            # Check if user already exists
            cursor.execute("SELECT user_id FROM users WHERE email = ?", (user["email"],))
            if not cursor.fetchone():
                password_hash = bcrypt.hashpw(user["password"].encode('utf-8'), bcrypt.gensalt())
                cursor.execute('''
                    INSERT INTO users (email, password_hash, role)
                    VALUES (?, ?, ?)
                ''', (user["email"], password_hash, user["role"]))
        
        conn.commit()
        conn.close()
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data if successful"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, email, password_hash, role, active
            FROM users WHERE email = ? AND active = 1
        ''', (email,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user[2]):
            return {
                "user_id": user[0],
                "email": user[1],
                "role": user[3],
                "active": user[4]
            }
        return None
    
    def add_lead(self, lead_data: Dict) -> int:
        """Add a new lead to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO leads (name, email, phone, program, role, experience_years,
                             budget_band, region, intent_text, source, raw_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            lead_data.get('name', ''),
            lead_data.get('email', ''),
            lead_data.get('phone', ''),
            lead_data.get('program', ''),
            lead_data.get('role', ''),
            lead_data.get('experience_years', 0),
            lead_data.get('budget_band', ''),
            lead_data.get('region', ''),
            lead_data.get('intent_text', ''),
            lead_data.get('source', ''),
            json.dumps(lead_data)
        ))
        
        lead_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return lead_id
    
    def get_leads(self, status: str = None, limit: int = 100) -> List[Dict]:
        """Get leads with optional status filter"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
                SELECT lead_id, created_at, name, email, phone, program, role,
                       experience_years, budget_band, region, intent_text, source, status
                FROM leads WHERE status = ? ORDER BY created_at DESC LIMIT ?
            ''', (status, limit))
        else:
            cursor.execute('''
                SELECT lead_id, created_at, name, email, phone, program, role,
                       experience_years, budget_band, region, intent_text, source, status
                FROM leads ORDER BY created_at DESC LIMIT ?
            ''', (limit,))
        
        columns = [description[0] for description in cursor.description]
        leads = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return leads
    
    def get_lead(self, lead_id: int) -> Optional[Dict]:
        """Get a specific lead by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT lead_id, created_at, name, email, phone, program, role,
                   experience_years, budget_band, region, intent_text, source, status, raw_data
            FROM leads WHERE lead_id = ?
        ''', (lead_id,))
        
        lead = cursor.fetchone()
        conn.close()
        
        if lead:
            columns = ['lead_id', 'created_at', 'name', 'email', 'phone', 'program', 'role',
                      'experience_years', 'budget_band', 'region', 'intent_text', 'source', 'status', 'raw_data']
            return dict(zip(columns, lead))
        return None
    
    def update_lead_status(self, lead_id: int, status: str):
        """Update lead status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE leads SET status = ? WHERE lead_id = ?
        ''', (status, lead_id))
        
        conn.commit()
        conn.close()
    
    def add_decision(self, decision_data: Dict) -> int:
        """Add a decision for a lead"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO decisions (lead_id, decided_by, status, rationale, confidence,
                                 factors_json, override_flag, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            decision_data['lead_id'],
            decision_data['decided_by'],
            decision_data['status'],
            decision_data.get('rationale', ''),
            decision_data.get('confidence', 0.0),
            json.dumps(decision_data.get('factors', {})),
            decision_data.get('override_flag', False),
            decision_data.get('notes', '')
        ))
        
        decision_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return decision_id
    
    def get_decisions(self, lead_id: int = None, user_id: int = None, limit: int = 100) -> List[Dict]:
        """Get decisions with optional filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT d.decision_id, d.lead_id, d.decided_by, d.decided_at, d.status,
                   d.rationale, d.confidence, d.factors_json, d.override_flag, d.notes,
                   u.email as decided_by_email, l.name as lead_name
            FROM decisions d
            JOIN users u ON d.decided_by = u.user_id
            JOIN leads l ON d.lead_id = l.lead_id
        '''
        
        conditions = []
        params = []
        
        if lead_id:
            conditions.append("d.lead_id = ?")
            params.append(lead_id)
        
        if user_id:
            conditions.append("d.decided_by = ?")
            params.append(user_id)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY d.decided_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        columns = [description[0] for description in cursor.description]
        decisions = []
        for row in cursor.fetchall():
            decision = dict(zip(columns, row))
            if decision['factors_json']:
                decision['factors'] = json.loads(decision['factors_json'])
            decisions.append(decision)
        
        conn.close()
        return decisions
    
    def log_audit(self, user_id: int, action: str, payload: Dict = None):
        """Log an audit event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO audits (user_id, action, payload_json)
            VALUES (?, ?, ?)
        ''', (user_id, action, json.dumps(payload) if payload else None))
        
        conn.commit()
        conn.close()
    
    def get_kpi_data(self, days: int = 7) -> Dict:
        """Get KPI data for the specified number of days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total leads
        cursor.execute('''
            SELECT COUNT(*) FROM leads 
            WHERE created_at >= datetime('now', '-{} days')
        '''.format(days))
        total_leads = cursor.fetchone()[0]
        
        # Decisions by status
        cursor.execute('''
            SELECT status, COUNT(*) FROM decisions 
            WHERE decided_at >= datetime('now', '-{} days')
            GROUP BY status
        '''.format(days))
        decisions_by_status = dict(cursor.fetchall())
        
        # Average decision time (simplified)
        cursor.execute('''
            SELECT AVG(confidence) FROM decisions 
            WHERE decided_at >= datetime('now', '-{} days')
        '''.format(days))
        avg_confidence = cursor.fetchone()[0] or 0
        
        # Override rate
        cursor.execute('''
            SELECT COUNT(*) FROM decisions 
            WHERE decided_at >= datetime('now', '-{} days') AND override_flag = 1
        '''.format(days))
        overrides = cursor.fetchone()[0]
        
        override_rate = (overrides / total_leads * 100) if total_leads > 0 else 0
        
        conn.close()
        
        return {
            'total_leads': total_leads,
            'decisions_by_status': decisions_by_status,
            'avg_confidence': round(avg_confidence, 2),
            'override_rate': round(override_rate, 2)
        }






