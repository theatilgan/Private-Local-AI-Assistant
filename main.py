#!/usr/bin/env python3
"""
Smart Course Recommendation System - Main Application

This application provides an AI-powered course recommendation system.
It extracts keywords from user input text and recommends suitable courses.

Author: Atilgan Aktas
Date: 2025
Version: 1.0.0
"""

import sys
import argparse
import logging
from typing import Optional
from src.app import CourseRecommender
from src.config.config import Config

def setup_logging() -> None:
    """Sets up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format=Config.LOG_FORMAT,
        handlers=[
            logging.FileHandler('logs/course_recommender.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def parse_arguments() -> argparse.Namespace:
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(
        description="Smart Course Recommendation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Interactive mode
  python main.py -q "mobile app development"  # Quick query
  python main.py --test             # Service tests
  python main.py --init             # Initialize database
        """
    )
    
    parser.add_argument(
        '-q', '--query',
        type=str,
        help='Text for quick query'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run service tests'
    )
    
    parser.add_argument(
        '--init',
        action='store_true',
        help='Initialize database and add sample data'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all courses'
    )
    
    parser.add_argument(
        '--add-course',
        nargs=3,
        metavar=('NAME', 'DESCRIPTION', 'KEYWORDS'),
        help='Add new course'
    )
    
    parser.add_argument(
        '--database',
        type=str,
        help='Database file path'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        help='AI model name'
    )
    
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    return parser.parse_args()

def main() -> int:
    """
    Main application function.
    
    Returns:
        int: Exit code (0: success, 1: error)
    """
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Setup logging
        if args.verbose:
            Config.LOG_LEVEL = 'DEBUG'
        setup_logging()
        
        logger = logging.getLogger(__name__)
        logger.info("Starting application...")
        
        # Initialize CourseRecommender
        recommender = CourseRecommender(
            database_path=args.database,
            ai_model=args.model
        )
        
        # Initialize database
        if args.init:
            logger.info("Initializing database...")
            if recommender.initialize_database():
                print("✅ Database initialized successfully!")
                return 0
            else:
                print("❌ Database initialization error!")
                return 1
        
        # Service tests
        if args.test:
            logger.info("Running service tests...")
            if recommender.test_services():
                print("✅ All services are working!")
                return 0
            else:
                print("❌ Some services have issues!")
                return 1
        
        # Course list
        if args.list:
            logger.info("Listing all courses...")
            courses = recommender.get_all_courses()
            if courses:
                print(f"\n📚 TOTAL {len(courses)} COURSES:")
                print("="*60)
                for i, (name, description) in enumerate(courses, 1):
                    print(f"{i:2d}. {name}")
                    print(f"    {description}")
                    print()
            else:
                print("❌ No courses found!")
            return 0
        
        # Add new course
        if args.add_course:
            name, description, keywords = args.add_course
            logger.info(f"Adding new course: {name}")
            if recommender.add_new_course(name, description, keywords):
                print(f"✅ Course added successfully: {name}")
                return 0
            else:
                print(f"❌ Course addition error: {name}")
                return 1
        
        # Quick query
        if args.query:
            logger.info(f"Quick query: {args.query}")
            courses = recommender.recommend_courses(args.query)
            recommender.display_recommendations(courses, args.query)
            return 0
        
        # Interactive mode (default)
        logger.info("Starting interactive mode...")
        recommender.run_interactive_mode()
        return 0
        
    except KeyboardInterrupt:
        print("\n\n👋 Program terminated by user.")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Critical error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 