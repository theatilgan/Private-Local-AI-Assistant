"""
CLI interface for PDF document management.
"""
import os
import sys
import argparse
from pathlib import Path
from src.app import CourseRecommender

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='PDF Document Management')
    parser.add_argument('--db', default='courses.db', help='Database file path')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add PDF command
    add_parser = subparsers.add_parser('add', help='Add PDF document')
    add_parser.add_argument('file', help='PDF file path')
    
    # Bulk PDF addition command
    add_bulk_parser = subparsers.add_parser('add-bulk', help='Add multiple PDFs')
    add_bulk_parser.add_argument('folder', help='Folder containing PDF files')
    
    # PDF listing command
    list_parser = subparsers.add_parser('list', help='List PDF documents')
    
    # PDF statistics command
    stats_parser = subparsers.add_parser('stats', help='Show PDF statistics')
    
    # PDF search command
    search_parser = subparsers.add_parser('search', help='Search PDF documents')
    search_parser.add_argument('query', help='Search query')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize CourseRecommender
    recommender = CourseRecommender(database_path=args.db)
    
    # Initialize database (for PDF tables) - only if it doesn't exist
    if not os.path.exists(args.db):
        recommender.initialize_database()
    
    try:
        if args.command == 'add':
            add_pdf(recommender, args.file)
        elif args.command == 'add-bulk':
            add_bulk_pdfs(recommender, args.folder)
        elif args.command == 'list':
            list_pdfs(recommender)
        elif args.command == 'stats':
            show_stats(recommender)
        elif args.command == 'search':
            search_pdfs(recommender, args.query)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def add_pdf(recommender: CourseRecommender, file_path: str):
    """Add single PDF."""
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    if not file_path.lower().endswith('.pdf'):
        print(f"❌ File is not in PDF format: {file_path}")
        return
    
    print(f"📄 Adding PDF: {file_path}")
    success = recommender.add_pdf_document(file_path)
    
    if success:
        print(f"✅ PDF added successfully: {os.path.basename(file_path)}")
    else:
        print(f"❌ Failed to add PDF: {os.path.basename(file_path)}")

def add_bulk_pdfs(recommender: CourseRecommender, folder_path: str):
    """Add multiple PDFs."""
    if not os.path.exists(folder_path):
        print(f"❌ Folder not found: {folder_path}")
        return
    
    folder = Path(folder_path)
    pdf_files = list(folder.glob('*.pdf'))
    
    if not pdf_files:
        print(f"❌ No PDF files found in folder: {folder_path}")
        return
    
    print(f"📄 Found {len(pdf_files)} PDF files, adding...")
    
    file_paths = [str(f) for f in pdf_files]
    results = recommender.add_multiple_pdfs(file_paths)
    
    successful = sum(results.values())
    failed = len(results) - successful
    
    print(f"\n📊 Results:")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    
    if failed > 0:
        print(f"\n❌ Failed files:")
        for filename, success in results.items():
            if not success:
                print(f"   - {filename}")

def list_pdfs(recommender: CourseRecommender):
    """List PDFs."""
    pdfs = recommender.get_all_pdfs()
    
    if not pdfs:
        print("📄 No PDF documents have been added yet.")
        return
    
    print(f"\n{'='*80}")
    print(f"📄 PDF DOCUMENT LIST ({len(pdfs)} items)")
    print(f"{'='*80}")
    
    for i, pdf in enumerate(pdfs, 1):
        doc_id, filename, title, keywords, summary, upload_date, status = pdf
        
        print(f"\n{i:2d}. 📄 {title or filename}")
        print(f"    📁 File: {filename}")
        print(f"    🏷️  Keywords: {keywords or 'Not specified'}")
        print(f"    📅 Upload Date: {upload_date}")
        print(f"    📊 Status: {status}")
        if summary:
            print(f"    📖 Summary: {summary[:100]}{'...' if len(summary) > 100 else ''}")
        print(f"    {'─'*60}")

def show_stats(recommender: CourseRecommender):
    """Show PDF statistics."""
    stats = recommender.get_pdf_statistics()
    
    if not stats:
        print("📄 No PDF documents have been added yet.")
        return
    
    print(f"\n{'='*50}")
    print(f"📊 PDF STATISTICS")
    print(f"{'='*50}")
    print(f"📄 Total PDF Count: {stats['total_pdfs']}")
    print(f"✅ Analyzed: {stats['analyzed_pdfs']}")
    print(f"⏳ Pending: {stats['pending_pdfs']}")
    print(f"📈 Analysis Rate: {stats['analysis_rate']:.1f}%")
    print(f"{'='*50}")

def search_pdfs(recommender: CourseRecommender, query: str):
    """Search in PDFs."""
    print(f"🔍 Searching: '{query}'")
    
    pdfs = recommender.recommend_pdfs(query)
    
    if not pdfs:
        print("❌ No PDF documents found matching your criteria.")
        return
    
    print(f"\n{'='*60}")
    print(f"🔍 SEARCH RESULTS ({len(pdfs)} items)")
    print(f"{'='*60}")
    
    for i, (title, summary) in enumerate(pdfs, 1):
        print(f"\n{i:2d}. 📄 {title}")
        print(f"    📖 {summary}")
        print(f"    {'─'*50}")

if __name__ == '__main__':
    main() 