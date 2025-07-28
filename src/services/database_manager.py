"""
Database management class.
"""
import sqlite3
import logging
from typing import List, Tuple, Optional
from contextlib import contextmanager
from ..config.config import Config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Class that manages database operations."""
    
    def __init__(self, database_path: str = None):
        """
        Initializes DatabaseManager.
        
        Args:
            database_path: Database file path
        """
        self.database_path = database_path or Config.DATABASE_PATH
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Sets up logging configuration."""
        logging.basicConfig(
            level=getattr(logging, Config.LOG_LEVEL),
            format=Config.LOG_FORMAT
        )
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connection.
        
        Yields:
            sqlite3.Connection: Database connection
        """
        conn = None
        try:
            conn = sqlite3.connect(self.database_path)
            conn.row_factory = sqlite3.Row  # Dict-like access
            logger.debug(f"Connected to database: {self.database_path}")
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
                logger.debug("Database connection closed")
    
    def create_tables(self) -> None:
        """Creates necessary tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Courses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS courses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    keywords TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # PDF documents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pdf_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL UNIQUE,
                    file_path TEXT NOT NULL,
                    title TEXT,
                    extracted_text TEXT,
                    extracted_keywords TEXT,
                    summary TEXT,
                    file_size INTEGER,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_analyzed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    analysis_status TEXT DEFAULT 'pending'
                )
            """)
            
            # Document-course relationship table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_courses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER,
                    course_id INTEGER,
                    relevance_score REAL DEFAULT 0.0,
                    FOREIGN KEY (document_id) REFERENCES pdf_documents (id),
                    FOREIGN KEY (course_id) REFERENCES courses (id)
                )
            """)
            
            conn.commit()
            logger.info("Tables created successfully")
    
    def insert_sample_data(self) -> None:
        """Adds sample data."""
        sample_courses = [
            ("Android Development", "Developing Android applications with Java", "mobile,android,java"),
            ("iOS Development", "iOS applications with Swift", "mobile,ios,swift"),
            ("React Native", "Cross-platform mobile applications", "mobile,react native,cross-platform"),
            ("Data Science", "Data analysis and machine learning with Python", "data science,python,data,ml"),
            ("Game Development", "Game programming with Unity", "game,Unity,c#"),
            ("Web Development", "Websites with HTML, CSS, JavaScript", "web,html,css,javascript"),
            ("Python Programming", "Python programming language fundamentals", "python,programming,basics"),
            ("Database Management", "SQL and database design", "database,sql,design"),
        ]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT OR IGNORE INTO courses (name, description, keywords) 
                VALUES (?, ?, ?)
            """, sample_courses)
            conn.commit()
            logger.info(f"{len(sample_courses)} sample courses added")
    
    def add_pdf_document(self, filename: str, file_path: str, title: str = None, 
                        extracted_text: str = None, extracted_keywords: str = None, 
                        summary: str = None, file_size: int = None) -> bool:
        """
        Adds a PDF document.
        
        Args:
            filename: File name
            file_path: File path
            title: Document title
            extracted_text: Extracted text
            extracted_keywords: Extracted keywords
            summary: Summary
            file_size: File size
            
        Returns:
            bool: Whether addition was successful
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO pdf_documents 
                    (filename, file_path, title, extracted_text, extracted_keywords, 
                     summary, file_size, analysis_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'completed')
                """, (filename, file_path, title, extracted_text, extracted_keywords, 
                      summary, file_size))
                conn.commit()
                logger.info(f"PDF document added: {filename}")
                return True
        except sqlite3.Error as e:
            logger.error(f"PDF document addition error: {e}")
            return False
    
    def get_pdf_documents(self) -> List[Tuple]:
        """
        Gets all PDF documents.
        
        Returns:
            List[Tuple]: List of PDF documents
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, filename, title, extracted_keywords, summary, 
                       upload_date, analysis_status 
                FROM pdf_documents 
                ORDER BY upload_date DESC
            """)
            return cursor.fetchall()
    
    def search_pdf_documents_by_keywords(self, keywords: List[str]) -> List[Tuple]:
        """
        Searches PDF documents by keywords.
        
        Args:
            keywords: List of keywords to search for
            
        Returns:
            List[Tuple]: Found PDF documents
        """
        if not keywords:
            logger.warning("No keywords provided for search")
            return []
        
        results = set()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for keyword in keywords:
                try:
                    cursor.execute("""
                        SELECT id, filename, title, extracted_keywords, summary 
                        FROM pdf_documents
                        WHERE extracted_keywords LIKE ? OR title LIKE ? OR summary LIKE ?
                    """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
                    
                    keyword_results = cursor.fetchall()
                    results.update(keyword_results)
                    logger.debug(f"Found {len(keyword_results)} PDF results for '{keyword}'")
                    
                except sqlite3.Error as e:
                    logger.error(f"PDF keyword search error '{keyword}': {e}")
                    continue
        
        logger.info(f"Found {len(results)} unique PDF documents")
        return list(results)
    
    def get_pdf_content_by_id(self, document_id: int) -> Optional[Tuple]:
        """
        Gets PDF content by ID.
        
        Args:
            document_id: PDF document ID
            
        Returns:
            Optional[Tuple]: PDF content
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT filename, extracted_text, extracted_keywords, summary
                FROM pdf_documents
                WHERE id = ?
            """, (document_id,))
            return cursor.fetchone()
    
    def update_pdf_analysis(self, document_id: int, extracted_keywords: str, 
                           summary: str) -> bool:
        """
        Updates PDF analysis results.
        
        Args:
            document_id: PDF document ID
            extracted_keywords: Extracted keywords
            summary: Summary
            
        Returns:
            bool: Whether update was successful
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE pdf_documents 
                    SET extracted_keywords = ?, summary = ?, 
                        last_analyzed = CURRENT_TIMESTAMP, analysis_status = 'completed'
                    WHERE id = ?
                """, (extracted_keywords, summary, document_id))
                conn.commit()
                logger.info(f"PDF analysis updated: ID {document_id}")
                return True
        except sqlite3.Error as e:
            logger.error(f"PDF analysis update error: {e}")
            return False
    
    def search_courses_by_keywords(self, keywords: List[str]) -> List[Tuple[str, str]]:
        """
        Searches courses by keywords.
        
        Args:
            keywords: List of keywords to search for
            
        Returns:
            List[Tuple[str, str]]: List of found courses (name, description)
        """
        if not keywords:
            logger.warning("No keywords provided for search")
            return []
        
        results = set()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for keyword in keywords:
                try:
                    cursor.execute("""
                        SELECT name, description FROM courses
                        WHERE keywords LIKE ? OR description LIKE ? OR name LIKE ?
                    """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
                    
                    keyword_results = cursor.fetchall()
                    results.update(keyword_results)
                    logger.debug(f"Found {len(keyword_results)} results for '{keyword}'")
                    
                except sqlite3.Error as e:
                    logger.error(f"Keyword search error '{keyword}': {e}")
                    continue
        
        logger.info(f"Found {len(results)} unique courses")
        return list(results)
    
    def get_all_courses(self) -> List[Tuple[str, str]]:
        """
        Gets all courses.
        
        Returns:
            List[Tuple[str, str]]: List of all courses (name, description)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, description FROM courses ORDER BY name")
            return cursor.fetchall()
    
    def add_course(self, name: str, description: str, keywords: str) -> bool:
        """
        Adds a new course.
        
        Args:
            name: Course name
            description: Course description
            keywords: Keywords
            
        Returns:
            bool: Whether addition was successful
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO courses (name, description, keywords)
                    VALUES (?, ?, ?)
                """, (name, description, keywords))
                conn.commit()
                logger.info(f"New course added: {name}")
                return True
        except sqlite3.Error as e:
            logger.error(f"Course addition error: {e}")
            return False 