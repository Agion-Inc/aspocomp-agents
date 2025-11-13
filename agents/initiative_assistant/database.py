"""Database operations for Initiative Assistant Agent."""

import sqlite3
import os
from typing import List, Optional
from datetime import datetime
from .models import Initiative, Feedback, SimilarityMatch


class InitiativeDatabase:
    """Database operations for Initiative Assistant."""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database. If None, uses default development path.
        """
        if db_path is None:
            # Default to development database
            data_dir = os.path.join(
                os.path.dirname(__file__),
                '../../data/initiative_assistant'
            )
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, 'initiatives.db')
        
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Initiatives table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS initiatives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                creator_name TEXT NOT NULL,
                creator_department TEXT,
                creator_email TEXT,
                creator_contact TEXT,
                goals TEXT,
                related_processes TEXT,
                expected_outcomes TEXT,
                status TEXT DEFAULT 'proposed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                feedback_count INTEGER DEFAULT 0,
                similarity_checked BOOLEAN DEFAULT 0
            )
        ''')
        
        # Feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                initiative_id INTEGER NOT NULL,
                feedback_text TEXT NOT NULL,
                feedback_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (initiative_id) REFERENCES initiatives(id)
            )
        ''')
        
        # Similarity matches table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS similarity_matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                initiative_id INTEGER NOT NULL,
                similar_to_id INTEGER NOT NULL,
                similarity_score REAL,
                similarity_reasons TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (initiative_id) REFERENCES initiatives(id),
                FOREIGN KEY (similar_to_id) REFERENCES initiatives(id)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_initiatives_title 
            ON initiatives(title)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_initiatives_status 
            ON initiatives(status)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_feedback_initiative_id 
            ON feedback(initiative_id)
        ''')
        
        conn.commit()
        conn.close()
    
    def save_initiative(self, initiative: Initiative) -> int:
        """Save initiative to database.
        
        Args:
            initiative: Initiative object to save
            
        Returns:
            ID of saved initiative
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if initiative.id is None:
            # Insert new initiative
            cursor.execute('''
                INSERT INTO initiatives (
                    title, description, creator_name, creator_department,
                    creator_email, creator_contact, goals, related_processes,
                    expected_outcomes, status, feedback_count, similarity_checked
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                initiative.title,
                initiative.description,
                initiative.creator_name,
                initiative.creator_department,
                initiative.creator_email,
                initiative.creator_contact,
                initiative.goals,
                initiative.related_processes,
                initiative.expected_outcomes,
                initiative.status,
                initiative.feedback_count,
                1 if initiative.similarity_checked else 0
            ))
            initiative_id = cursor.lastrowid
        else:
            # Update existing initiative
            cursor.execute('''
                UPDATE initiatives SET
                    title = ?, description = ?, creator_name = ?,
                    creator_department = ?, creator_email = ?, creator_contact = ?,
                    goals = ?, related_processes = ?, expected_outcomes = ?,
                    status = ?, updated_at = CURRENT_TIMESTAMP,
                    feedback_count = ?, similarity_checked = ?
                WHERE id = ?
            ''', (
                initiative.title,
                initiative.description,
                initiative.creator_name,
                initiative.creator_department,
                initiative.creator_email,
                initiative.creator_contact,
                initiative.goals,
                initiative.related_processes,
                initiative.expected_outcomes,
                initiative.status,
                initiative.feedback_count,
                1 if initiative.similarity_checked else 0,
                initiative.id
            ))
            initiative_id = initiative.id
        
        conn.commit()
        conn.close()
        return initiative_id
    
    def get_initiative(self, initiative_id: int, include_personal: bool = False) -> Optional[Initiative]:
        """Get initiative by ID.
        
        Args:
            initiative_id: ID of initiative
            include_personal: If True, include personal information
            
        Returns:
            Initiative object or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM initiatives WHERE id = ?', (initiative_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return None
        
        data = dict(row)
        # Convert boolean
        data['similarity_checked'] = bool(data['similarity_checked'])
        
        return Initiative.from_dict(data)
    
    def search_similar(self, title: str, description: str, limit: int = 5) -> List[Initiative]:
        """Search for similar initiatives.
        
        Uses keyword matching on title and description.
        Personal information is excluded from results.
        
        Args:
            title: Initiative title to search for
            description: Initiative description to search for
            limit: Maximum number of results
            
        Returns:
            List of similar initiatives (without personal information)
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Simple keyword-based search
        # Split title and description into keywords
        search_terms = []
        if title:
            search_terms.extend(title.lower().split())
        if description:
            search_terms.extend(description.lower().split())
        
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        search_terms = [term for term in search_terms if term not in stop_words and len(term) > 2]
        
        if not search_terms:
            conn.close()
            return []
        
        # Build query with LIKE conditions
        conditions = []
        params = []
        for term in search_terms[:5]:  # Limit to 5 terms
            conditions.append("(LOWER(title) LIKE ? OR LOWER(description) LIKE ?)")
            params.extend([f"%{term}%", f"%{term}%"])
        
        query = f'''
            SELECT * FROM initiatives
            WHERE {' OR '.join(conditions)}
            ORDER BY created_at DESC
            LIMIT ?
        '''
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        initiatives = []
        for row in rows:
            data = dict(row)
            data['similarity_checked'] = bool(data['similarity_checked'])
            initiative = Initiative.from_dict(data)
            initiatives.append(initiative)
        
        return initiatives
    
    def save_feedback(self, feedback: Feedback) -> int:
        """Save feedback to database.
        
        Args:
            feedback: Feedback object to save
            
        Returns:
            ID of saved feedback
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO feedback (initiative_id, feedback_text, feedback_type)
            VALUES (?, ?, ?)
        ''', (
            feedback.initiative_id,
            feedback.feedback_text,
            feedback.feedback_type
        ))
        
        feedback_id = cursor.lastrowid
        
        # Update feedback count
        cursor.execute('''
            UPDATE initiatives
            SET feedback_count = feedback_count + 1
            WHERE id = ?
        ''', (feedback.initiative_id,))
        
        conn.commit()
        conn.close()
        return feedback_id
    
    def get_all_initiatives(self, include_personal: bool = False, limit: int = 100) -> List[Initiative]:
        """Get all initiatives.
        
        Args:
            include_personal: If True, include personal information
            limit: Maximum number of results
            
        Returns:
            List of initiatives
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM initiatives
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        initiatives = []
        for row in rows:
            data = dict(row)
            data['similarity_checked'] = bool(data['similarity_checked'])
            initiatives.append(Initiative.from_dict(data))
        
        return initiatives

