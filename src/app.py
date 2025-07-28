"""
Main class for course recommendation system.
"""
import logging
import os
from typing import List, Tuple, Optional, Dict, Any
from .services.database_manager import DatabaseManager
from .services.ai_service import AIService
from .services.pdf_service import PDFService
from .config.config import Config

logger = logging.getLogger(__name__)

class CourseRecommender:
    """Main class for course recommendation system."""
    
    def __init__(self, database_path: str = None, ai_model: str = None):
        """
        Initializes CourseRecommender.
        
        Args:
            database_path: Database file path
            ai_model: AI model to use
        """
        self.db_manager = DatabaseManager(database_path)
        self.ai_service = AIService(ai_model)
        self.pdf_service = PDFService(self.ai_service, self.db_manager)
        self._setup_logging()
        logger.info("Course recommendation system initialized")
    
    def _setup_logging(self) -> None:
        """Sets up logging configuration."""
        logging.basicConfig(
            level=getattr(logging, Config.LOG_LEVEL),
            format=Config.LOG_FORMAT
        )
    
    def initialize_database(self) -> bool:
        """
        Initializes database and adds sample data.
        
        Returns:
            bool: Whether initialization was successful
        """
        try:
            self.db_manager.create_tables()
            self.db_manager.insert_sample_data()
            logger.info("Database initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            return False
    
    def test_services(self) -> bool:
        """
        Tests if all services are working.
        
        Returns:
            bool: Whether all services are working
        """
        logger.info("Starting service tests...")
        
        # AI service test
        ai_ok = self.ai_service.test_connection()
        if not ai_ok:
            logger.warning("AI service test failed, fallback mode will be used")
        
        # Database test
        try:
            courses = self.db_manager.get_all_courses()
            db_ok = len(courses) > 0
            logger.info(f"Database test: {len(courses)} courses found")
        except Exception as e:
            logger.error(f"Database test failed: {e}")
            db_ok = False
        
        overall_success = db_ok  # At least database should work
        logger.info(f"Service tests completed - Overall status: {'Success' if overall_success else 'Failed'}")
        
        return overall_success
    
    def recommend_courses(self, user_input: str) -> List[Tuple[str, str]]:
        """
        Recommends courses based on user input.
        
        Args:
            user_input: User input text
            
        Returns:
            List[Tuple[str, str]]: List of recommended courses (name, description)
        """
        if not user_input or not user_input.strip():
            logger.warning("Empty user input")
            return []
        
        logger.info(f"Course recommendation requested: '{user_input}'")
        
        try:
            # Extract keywords
            keywords = self.ai_service.extract_keywords(user_input)
            if not keywords:
                logger.warning("Could not extract keywords")
                return []
            
            # Search courses
            recommended_courses = self.db_manager.search_courses_by_keywords(keywords)
            
            logger.info(f"{len(recommended_courses)} courses recommended for '{user_input}'")
            return recommended_courses
            
        except Exception as e:
            logger.error(f"Course recommendation error: {e}")
            return []
    
    def recommend_pdfs(self, user_input: str) -> List[Tuple[str, str]]:
        """
        Recommends PDF documents based on user input.
        
        Args:
            user_input: User input text
            
        Returns:
            List[Tuple[str, str]]: List of recommended PDFs (title, summary)
        """
        if not user_input or not user_input.strip():
            logger.warning("Empty user input")
            return []
        
        logger.info(f"PDF recommendation requested: '{user_input}'")
        
        try:
            # Search PDFs
            pdf_results = self.pdf_service.search_pdfs_by_query(user_input)
            
            # Format results
            formatted_results = []
            for pdf in pdf_results:
                title = pdf[2] if pdf[2] else pdf[1]  # title or filename
                summary = pdf[4] if pdf[4] else "Summary not found"  # summary
                formatted_results.append((title, summary))
            
            logger.info(f"{len(formatted_results)} PDFs recommended for '{user_input}'")
            return formatted_results
            
        except Exception as e:
            logger.error(f"PDF recommendation error: {e}")
            return []
    
    def recommend_all(self, user_input: str) -> Dict[str, List[Tuple[str, str]]]:
        """
        Provides both course and PDF recommendations.
        
        Args:
            user_input: User input text
            
        Returns:
            Dict[str, List[Tuple[str, str]]]: Course and PDF recommendations
        """
        courses = self.recommend_courses(user_input)
        pdfs = self.recommend_pdfs(user_input)
        
        return {
            'courses': courses,
            'pdfs': pdfs
        }
    
    def add_new_course(self, name: str, description: str, keywords: str) -> bool:
        """
        Adds a new course.
        
        Args:
            name: Course name
            description: Course description
            keywords: Keywords
            
        Returns:
            bool: Whether addition was successful
        """
        logger.info(f"Adding new course: {name}")
        return self.db_manager.add_course(name, description, keywords)
    
    def add_pdf_document(self, file_path: str) -> bool:
        """
        Adds and analyzes a PDF document.
        
        Args:
            file_path: PDF file path
            
        Returns:
            bool: Whether addition was successful
        """
        logger.info(f"Adding PDF document: {file_path}")
        return self.pdf_service.process_pdf_file(file_path)
    
    def add_multiple_pdfs(self, file_paths: List[str]) -> Dict[str, bool]:
        """
        Adds multiple PDF documents.
        
        Args:
            file_paths: List of PDF file paths
            
        Returns:
            Dict[str, bool]: Operation results
        """
        logger.info(f"Adding {len(file_paths)} PDF documents")
        return self.pdf_service.process_multiple_pdfs(file_paths)
    
    def get_all_courses(self) -> List[Tuple[str, str]]:
        """
        Gets all courses.
        
        Returns:
            List[Tuple[str, str]]: List of all courses
        """
        return self.db_manager.get_all_courses()
    
    def get_all_pdfs(self) -> List[Tuple]:
        """
        Gets all PDF documents.
        
        Returns:
            List[Tuple]: List of all PDFs
        """
        return self.db_manager.get_pdf_documents()
    
    def get_pdf_statistics(self) -> Dict[str, Any]:
        """
        Gets PDF statistics.
        
        Returns:
            Dict[str, Any]: PDF statistics
        """
        return self.pdf_service.get_pdf_statistics()
    
    def display_recommendations(self, courses: List[Tuple[str, str]], user_input: str) -> None:
        """
        Displays course recommendations in a nice format.
        
        Args:
            courses: Recommended courses
            user_input: User input
        """
        print(f"\n{'='*60}")
        print(f"🎓 COURSE RECOMMENDATIONS")
        print(f"{'='*60}")
        print(f"📝 User Input: '{user_input}'")
        print(f"📊 Courses Found: {len(courses)}")
        print(f"{'='*60}")
        
        if not courses:
            print("❌ Sorry, no courses found matching your criteria.")
            print("💡 Try different keywords or use more general terms.")
            return
        
        for i, (name, description) in enumerate(courses, 1):
            print(f"\n{i:2d}. 📚 {name}")
            print(f"    📖 {description}")
            print(f"    {'─'*50}")
        
        print(f"\n✨ Total {len(courses)} courses recommended!")
        print(f"{'='*60}")
    
    def display_pdf_recommendations(self, pdfs: List[Tuple[str, str]], user_input: str) -> None:
        """
        Displays PDF recommendations in a nice format.
        
        Args:
            pdfs: Recommended PDFs
            user_input: User input
        """
        print(f"\n{'='*60}")
        print(f"📄 PDF DOCUMENT RECOMMENDATIONS")
        print(f"{'='*60}")
        print(f"📝 User Input: '{user_input}'")
        print(f"📊 PDFs Found: {len(pdfs)}")
        print(f"{'='*60}")
        
        if not pdfs:
            print("❌ Sorry, no PDF documents found matching your criteria.")
            print("💡 Try different keywords or use more general terms.")
            return
        
        for i, (title, summary) in enumerate(pdfs, 1):
            print(f"\n{i:2d}. 📄 {title}")
            print(f"    📖 {summary}")
            print(f"    {'─'*50}")
        
        print(f"\n✨ Total {len(pdfs)} PDF documents recommended!")
        print(f"{'='*60}")
    
    def display_all_recommendations(self, recommendations: Dict[str, List[Tuple[str, str]]], user_input: str) -> None:
        """
        Displays both course and PDF recommendations.
        
        Args:
            recommendations: Course and PDF recommendations
            user_input: User input
        """
        courses = recommendations.get('courses', [])
        pdfs = recommendations.get('pdfs', [])
        
        print(f"\n{'='*60}")
        print(f"🎯 GENERAL RECOMMENDATIONS")
        print(f"{'='*60}")
        print(f"📝 User Input: '{user_input}'")
        print(f"📊 Courses Found: {len(courses)}")
        print(f"📄 PDFs Found: {len(pdfs)}")
        print(f"{'='*60}")
        
        if not courses and not pdfs:
            print("❌ Sorry, no content found matching your criteria.")
            print("💡 Try different keywords or use more general terms.")
            return
        
        # Show courses
        if courses:
            print(f"\n🎓 COURSE RECOMMENDATIONS ({len(courses)} items):")
            for i, (name, description) in enumerate(courses, 1):
                print(f"\n{i:2d}. 📚 {name}")
                print(f"    📖 {description}")
                print(f"    {'─'*30}")
        
        # Show PDFs
        if pdfs:
            print(f"\n📄 PDF DOCUMENT RECOMMENDATIONS ({len(pdfs)} items):")
            for i, (title, summary) in enumerate(pdfs, 1):
                print(f"\n{i:2d}. 📄 {title}")
                print(f"    📖 {summary}")
                print(f"    {'─'*30}")
        
        print(f"\n✨ Total {len(courses) + len(pdfs)} content items recommended!")
        print(f"{'='*60}")
    
    def display_welcome_message(self) -> None:
        """Displays welcome message."""
        print(f"\n{'='*60}")
        print(f"🎓 SMART COURSE AND DOCUMENT RECOMMENDATION SYSTEM")
        print(f"{'='*60}")
        print(f"🤖 Ready for AI-powered course and PDF document recommendations!")
        print(f"💡 Write what you want to learn, and we'll find suitable courses and documents for you.")
        print(f"🔍 Example: 'I want to develop mobile applications'")
        print(f"🔍 Example: 'data analysis with python'")
        print(f"🔍 Example: 'make a website'")
        print(f"📄 PDF documents are also automatically analyzed and recommended!")
        print(f"{'='*60}")
    
    def run_interactive_mode(self) -> None:
        """Runs interactive mode."""
        self.display_welcome_message()
        
        while True:
            try:
                print(f"\n{'─'*40}")
                user_input = input("💭 What do you want to learn? (type 'q' to quit): ").strip()
                
                if user_input.lower() in ['q', 'quit', 'exit']:
                    print("👋 Goodbye! Good luck with your studies!")
                    break
                
                if not user_input:
                    print("⚠️  Please write something.")
                    continue
                
                # Get both course and PDF recommendations
                all_recommendations = self.recommend_all(user_input)
                
                # Display results
                self.display_all_recommendations(all_recommendations, user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 Program terminated by user.")
                break
            except Exception as e:
                logger.error(f"Interactive mode error: {e}")
                print(f"❌ An error occurred: {e}")
                print("🔄 Please try again.") 