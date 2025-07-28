"""
Course recommendation system tests.
"""
import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock
from src.app import CourseRecommender
from src.services.database_manager import DatabaseManager
from src.services.ai_service import AIService
from src.services.pdf_service import PDFService
from src.config.config import Config

class TestCourseRecommender(unittest.TestCase):
    """CourseRecommender class tests."""
    
    def setUp(self):
        """Test preparation."""
        # Create temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Create CourseRecommender for testing
        self.recommender = CourseRecommender(database_path=self.temp_db.name)
    
    def tearDown(self):
        """Test cleanup."""
        # Delete temporary file
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_initialize_database(self):
        """Database initialization test."""
        result = self.recommender.initialize_database()
        self.assertTrue(result)
        
        # Check if courses exist in database
        courses = self.recommender.get_all_courses()
        self.assertGreater(len(courses), 0)
    
    @patch('src.services.ai_service.ollama.chat')
    def test_recommend_courses_with_ai(self, mock_ollama):
        """Course recommendation with AI test."""
        # Mock AI response
        mock_ollama.return_value = {
            'message': {'content': 'mobile,android,application'}
        }
        
        # Initialize database
        self.recommender.initialize_database()
        
        # Get course recommendation
        courses = self.recommender.recommend_courses("I want to develop mobile applications")
        
        # Check results
        self.assertIsInstance(courses, list)
        # At least one mobile course should be found
        mobile_courses = [c for c in courses if 'mobile' in c[1].lower() or 'android' in c[1].lower()]
        self.assertGreater(len(mobile_courses), 0)
    
    def test_recommend_courses_empty_input(self):
        """Empty input test."""
        courses = self.recommender.recommend_courses("")
        self.assertEqual(courses, [])
        
        courses = self.recommender.recommend_courses(None)
        self.assertEqual(courses, [])
    
    def test_add_new_course(self):
        """Add new course test."""
        # Initialize database
        self.recommender.initialize_database()
        
        # Add new course
        result = self.recommender.add_new_course(
            "Test Course",
            "This is a test course",
            "test,course,example"
        )
        
        self.assertTrue(result)
        
        # Check if course was added
        courses = self.recommender.get_all_courses()
        course_names = [c[0] for c in courses]
        self.assertIn("Test Course", course_names)
    
    def test_recommend_pdfs(self):
        """PDF recommendation test."""
        # Initialize database
        self.recommender.initialize_database()
        
        # Get PDF recommendation
        pdfs = self.recommender.recommend_pdfs("python programming")
        
        # Check results
        self.assertIsInstance(pdfs, list)
    
    def test_recommend_all(self):
        """Both course and PDF recommendation test."""
        # Initialize database
        self.recommender.initialize_database()
        
        # Get recommendations
        recommendations = self.recommender.recommend_all("python")
        
        # Check results
        self.assertIsInstance(recommendations, dict)
        self.assertIn('courses', recommendations)
        self.assertIn('pdfs', recommendations)
        self.assertIsInstance(recommendations['courses'], list)
        self.assertIsInstance(recommendations['pdfs'], list)

class TestDatabaseManager(unittest.TestCase):
    """DatabaseManager class tests."""
    
    def setUp(self):
        """Test preparation."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_manager = DatabaseManager(self.temp_db.name)
    
    def tearDown(self):
        """Test cleanup."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_create_tables(self):
        """Table creation test."""
        self.db_manager.create_tables()
        
        # Check if tables were created
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='courses'")
            result = cursor.fetchone()
            self.assertIsNotNone(result)
    
    def test_search_courses_by_keywords(self):
        """Keyword search test."""
        # Prepare database
        self.db_manager.create_tables()
        self.db_manager.insert_sample_data()
        
        # Perform search
        results = self.db_manager.search_courses_by_keywords(["mobile", "android"])
        
        # Check results
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        # Mobile courses should be found
        mobile_courses = [r for r in results if 'mobile' in r[1].lower() or 'android' in r[1].lower()]
        self.assertGreater(len(mobile_courses), 0)

class TestAIService(unittest.TestCase):
    """AIService class tests."""
    
    def setUp(self):
        """Test preparation."""
        self.ai_service = AIService()
    
    @patch('src.services.ai_service.ollama.chat')
    def test_extract_keywords_success(self, mock_ollama):
        """Successful keyword extraction test."""
        # Mock AI response
        mock_ollama.return_value = {
            'message': {'content': 'python,data,analysis'}
        }
        
        keywords = self.ai_service.extract_keywords("I want to do data analysis with Python")
        
        self.assertIsInstance(keywords, list)
        self.assertGreater(len(keywords), 0)
        self.assertIn('python', keywords)
    
    def test_extract_keywords_empty_input(self):
        """Empty input test."""
        keywords = self.ai_service.extract_keywords("")
        self.assertEqual(keywords, [])
        
        keywords = self.ai_service.extract_keywords(None)
        self.assertEqual(keywords, [])
    
    def test_fallback_keyword_extraction(self):
        """Fallback keyword extraction test."""
        keywords = self.ai_service._fallback_keyword_extraction(
            "I want to do data analysis with Python"
        )
        
        self.assertIsInstance(keywords, list)
        self.assertGreater(len(keywords), 0)
        # Stop words should be removed
        self.assertNotIn('with', keywords)
        self.assertNotIn('want', keywords)

class TestPDFService(unittest.TestCase):
    """PDFService class tests."""
    
    def setUp(self):
        """Test preparation."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_manager = DatabaseManager(self.temp_db.name)
        self.ai_service = AIService()
        self.pdf_service = PDFService(self.ai_service, self.db_manager)
    
    def tearDown(self):
        """Test cleanup."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_clean_text(self):
        """Text cleaning test."""
        dirty_text = "  This   is   a   test   text   "
        clean_text = self.pdf_service._clean_text(dirty_text)
        self.assertEqual(clean_text, "This is a test text")
    
    def test_extract_title(self):
        """Title extraction test."""
        text = "Python Programming\nThis is a test document."
        title = self.pdf_service._extract_title(text, "test.pdf")
        self.assertEqual(title, "Python Programming")
    
    def test_generate_summary(self):
        """Summary generation test."""
        long_text = "This is a very long text. " * 20
        summary = self.pdf_service._generate_summary(long_text, "test.pdf")
        self.assertLess(len(summary), len(long_text))
        self.assertTrue(summary.endswith("..."))

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2) 