"""
PDF processing service.
"""
import os
import logging
from typing import List, Tuple, Optional, Dict, Any
import PyPDF2
import fitz  # PyMuPDF
from .ai_service import AIService
from .database_manager import DatabaseManager

logger = logging.getLogger(__name__)

class PDFService:
    """Service that processes PDF documents."""
    
    def __init__(self, ai_service: AIService = None, db_manager: DatabaseManager = None):
        """
        Initializes PDFService.
        
        Args:
            ai_service: AI service
            db_manager: Database manager
        """
        self.ai_service = ai_service or AIService()
        self.db_manager = db_manager
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Sets up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extracts text from PDF.
        
        Args:
            file_path: PDF file path
            
        Returns:
            str: Extracted text
        """
        try:
            # Text extraction with PyMuPDF (better results)
            doc = fitz.open(file_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                if page_text:
                    text += page_text + "\n"
            
            doc.close()
            
            # If text couldn't be extracted with PyMuPDF, try PyPDF2
            if not text.strip():
                logger.info(f"Text couldn't be extracted with PyMuPDF, trying PyPDF2: {file_path}")
                text = self._extract_with_pypdf2(file_path)
            
            # Clean text
            text = self._clean_text(text)
            
            # If still no text, extract from filename
            if not text.strip():
                logger.info(f"Text couldn't be extracted from PDF, extracting keywords from filename: {file_path}")
                text = self._extract_keywords_from_filename(file_path)
            
            logger.info(f"Extracted {len(text)} characters from PDF: {file_path}")
            return text
            
        except Exception as e:
            logger.error(f"PDF text extraction error: {e}")
            # Last resort: extract keywords from filename
            return self._extract_keywords_from_filename(file_path)
    
    def _extract_with_pypdf2(self, file_path: str) -> str:
        """Text extraction with PyPDF2."""
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            logger.error(f"PyPDF2 text extraction error: {e}")
            return ""
    
    def _extract_keywords_from_filename(self, file_path: str) -> str:
        """Extract keywords from filename."""
        filename = os.path.basename(file_path)
        # Remove .pdf extension
        name = filename.replace('.pdf', '').replace('.PDF', '')
        # Replace underscores and hyphens with spaces
        name = name.replace('_', ' ').replace('-', ' ')
        # Keep uppercase letters, they might be keywords
        return name
    
    def _clean_text(self, text: str) -> str:
        """
        Cleans extracted text.
        
        Args:
            text: Raw text
            
        Returns:
            str: Cleaned text
        """
        # Clean unnecessary whitespace
        text = ' '.join(text.split())
        
        # Clean special characters
        import re
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        
        return text
    
    def analyze_pdf_content(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        Analyzes PDF content.
        
        Args:
            file_path: PDF file path
            filename: File name
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        logger.info(f"Starting PDF analysis: {filename}")
        
        try:
            # Extract text
            extracted_text = self.extract_text_from_pdf(file_path)
            if not extracted_text:
                logger.warning(f"Text couldn't be extracted from PDF: {filename}")
                return {}
            
            # Analyze with AI
            analysis_result = self._analyze_with_ai(extracted_text, filename)
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            return {
                'filename': filename,
                'file_path': file_path,
                'extracted_text': extracted_text,
                'extracted_keywords': analysis_result.get('keywords', ''),
                'summary': analysis_result.get('summary', ''),
                'title': analysis_result.get('title', filename),
                'file_size': file_size
            }
            
        except Exception as e:
            logger.error(f"PDF analysis error: {e}")
            return {}
    
    def _analyze_with_ai(self, text: str, filename: str) -> Dict[str, str]:
        """
        Analyzes text with AI.
        
        Args:
            text: Text to analyze
            filename: File name
            
        Returns:
            Dict[str, str]: Analysis results
        """
        try:
            # Shorten text (for AI token limit)
            max_chars = 4000
            if len(text) > max_chars:
                text = text[:max_chars] + "..."
            
            # Extract keywords
            keywords = self.ai_service.extract_keywords(text)
            keywords_str = ','.join(keywords) if keywords else ''
            
            # Generate summary
            summary = self._generate_summary(text, filename)
            
            # Extract title
            title = self._extract_title(text, filename)
            
            return {
                'keywords': keywords_str,
                'summary': summary,
                'title': title
            }
            
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            return {
                'keywords': '',
                'summary': f"PDF document: {filename}",
                'title': filename
            }
    
    def _generate_summary(self, text: str, filename: str) -> str:
        """
        Generates text summary.
        
        Args:
            text: Text to summarize
            filename: File name
            
        Returns:
            str: Summary
        """
        try:
            # Simple summary generation (first 200 characters)
            if len(text) > 200:
                summary = text[:200] + "..."
            else:
                summary = text
            
            return summary
            
        except Exception as e:
            logger.error(f"Summary generation error: {e}")
            return f"PDF document: {filename}"
    
    def _extract_title(self, text: str, filename: str) -> str:
        """
        Extracts title from text.
        
        Args:
            text: Text
            filename: File name
            
        Returns:
            str: Title
        """
        try:
            # Take first line as title
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if line and len(line) > 3 and len(line) < 100:
                    return line
            
            # If no suitable title found, use filename
            return filename.replace('.pdf', '').replace('_', ' ').title()
            
        except Exception as e:
            logger.error(f"Title extraction error: {e}")
            return filename.replace('.pdf', '').replace('_', ' ').title()
    
    def process_pdf_file(self, file_path: str, upload_folder: str = "uploads") -> bool:
        """
        Processes PDF file and adds to database.
        
        Args:
            file_path: PDF file path
            upload_folder: Upload folder
            
        Returns:
            bool: Whether processing was successful
        """
        try:
            # Check file existence
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return False
            
            # Get filename
            filename = os.path.basename(file_path)
            
            # Analyze PDF
            analysis_result = self.analyze_pdf_content(file_path, filename)
            if not analysis_result:
                logger.error(f"PDF analysis failed: {filename}")
                return False
            
            # Add to database
            if self.db_manager:
                success = self.db_manager.add_pdf_document(
                    filename=analysis_result['filename'],
                    file_path=analysis_result['file_path'],
                    title=analysis_result['title'],
                    extracted_text=analysis_result['extracted_text'],
                    extracted_keywords=analysis_result['extracted_keywords'],
                    summary=analysis_result['summary'],
                    file_size=analysis_result['file_size']
                )
                
                if success:
                    logger.info(f"PDF successfully processed and added to database: {filename}")
                    return True
                else:
                    logger.error(f"PDF couldn't be added to database: {filename}")
                    return False
            else:
                logger.warning("Database manager not found, only analysis performed")
                return True
                
        except Exception as e:
            logger.error(f"PDF processing error: {e}")
            return False
    
    def process_multiple_pdfs(self, file_paths: List[str]) -> Dict[str, bool]:
        """
        Processes multiple PDF files.
        
        Args:
            file_paths: List of PDF file paths
            
        Returns:
            Dict[str, bool]: Processing results
        """
        results = {}
        
        for file_path in file_paths:
            filename = os.path.basename(file_path)
            success = self.process_pdf_file(file_path)
            results[filename] = success
        
        successful_count = sum(results.values())
        logger.info(f"Successfully processed {successful_count} out of {len(file_paths)} PDFs")
        
        return results
    
    def search_pdfs_by_query(self, query: str) -> List[Tuple]:
        """
        Searches PDFs by query.
        
        Args:
            query: Search query
            
        Returns:
            List[Tuple]: Found PDFs
        """
        if not self.db_manager:
            logger.error("Database manager not found")
            return []
        
        try:
            # First extract keywords with AI
            keywords = self.ai_service.extract_keywords(query)
            
            # Search in database
            results = self.db_manager.search_pdf_documents_by_keywords(keywords)
            
            logger.info(f"Found {len(results)} PDFs for query '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"PDF search error: {e}")
            return []
    
    def get_pdf_statistics(self) -> Dict[str, Any]:
        """
        Gets PDF statistics.
        
        Returns:
            Dict[str, Any]: Statistics
        """
        if not self.db_manager:
            return {}
        
        try:
            pdfs = self.db_manager.get_pdf_documents()
            
            total_pdfs = len(pdfs)
            analyzed_pdfs = len([p for p in pdfs if p[6] == 'completed'])  # analysis_status
            pending_pdfs = total_pdfs - analyzed_pdfs
            
            return {
                'total_pdfs': total_pdfs,
                'analyzed_pdfs': analyzed_pdfs,
                'pending_pdfs': pending_pdfs,
                'analysis_rate': (analyzed_pdfs / total_pdfs * 100) if total_pdfs > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"PDF statistics error: {e}")
            return {} 