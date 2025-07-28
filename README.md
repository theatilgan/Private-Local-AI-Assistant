# 🎓 Smart Course and Document Recommendation System

AI-powered course and PDF document recommendation system. Extracts keywords from user input text and recommends suitable courses and PDF documents.

## ✨ Features

- 🤖 **AI Powered**: Keyword extraction with Ollama
- 📄 **PDF Analysis**: Automatic PDF text extraction and analysis
- 🔍 **Smart Search**: Keyword-based course and document matching
- 📊 **Database**: Course and PDF management with SQLite
- 🎨 **Beautiful UI**: Emoji-supported terminal interface
- 📝 **Logging**: Detailed logging system
- ⚙️ **Configuration**: Environment variables support
- 🧪 **Testable**: Modular and testable structure
- 📁 **PDF Management**: Bulk PDF upload and management

## 🚀 Installation

### Requirements

- Python 3.8+
- Ollama (for AI model)

### Steps

1. **Clone the repository:**
```bash
git clone <repository-url>
cd StajProjesi
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install Ollama and download model:**
```bash
# Ollama installation (https://ollama.ai)
ollama pull gemma2:latest
```

4. **Initialize database:**
```bash
python main.py --init
```

## 🎯 Usage

### Interactive Mode (Default)
```bash
python main.py
```

### Quick Query
```bash
python main.py -q "I want to develop mobile applications"
```

### Service Tests
```bash
python main.py --test
```

### List All Courses
```bash
python main.py --list
```

### Add New Course
```bash
python main.py --add-course "Course Name" "Course Description" "keywords,separated,by,commas"
```

### PDF Document Management

#### Add Single PDF
```bash
python pdf_manager.py add "file_path.pdf"
```

#### Add Multiple PDFs
```bash
python pdf_manager.py add-bulk "pdf_folder/"
```

#### List PDFs
```bash
python pdf_manager.py list
```

#### PDF Statistics
```bash
python pdf_manager.py stats
```

#### Search in PDFs
```bash
python pdf_manager.py search "search query"
```

## 📁 Project Structure

```
StajProjesi/
├── src/                    # Main source code
│   ├── __init__.py
│   ├── app.py             # Main application class
│   ├── services/          # Service layer
│   │   ├── __init__.py
│   │   ├── ai_service.py  # AI services
│   │   ├── database_manager.py # Database management
│   │   └── pdf_service.py # PDF processing service
│   └── config/            # Configuration
│       ├── __init__.py
│       └── config.py      # Configuration settings
├── tests/                 # Test files
│   ├── __init__.py
│   └── test_main.py       # Main test file
├── data/                  # Data files
│   └── database.db        # SQLite database
├── logs/                  # Log files
│   └── course_recommender.log
├── uploads/               # PDF upload folder
├── main.py                # Entry point
├── pdf_manager.py         # PDF management CLI
├── requirements.txt       # Dependencies
├── README.md             # This file
└── .gitignore            # Git ignore file
```

## ⚙️ Configuration

Configurable via environment variables:

```bash
# Database
export DATABASE_PATH="my_database.db"

# AI Model
export OLLAMA_MODEL="gemma2:latest"
export OLLAMA_HOST="http://localhost:11434"

# Application
export MAX_KEYWORDS="5"
export MIN_KEYWORDS="3"

# Logging
export LOG_LEVEL="INFO"
```

## 🔧 Development

### Code Formatting
```bash
black *.py
```

### Linting
```bash
flake8 *.py
```

### Type Checking
```bash
mypy *.py
```

### Tests
```bash
pytest tests/
```

## 📊 Database Schema

### Courses Table
```sql
CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    keywords TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### PDF Documents Table
```sql
CREATE TABLE pdf_documents (
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
);
```

### Document-Course Relationship Table
```sql
CREATE TABLE document_courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER,
    course_id INTEGER,
    relevance_score REAL DEFAULT 0.0,
    FOREIGN KEY (document_id) REFERENCES pdf_documents (id),
    FOREIGN KEY (course_id) REFERENCES courses (id)
);
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🐛 Bug Reports

Use GitHub Issues for bug reports.

## 📞 Contact

- **Developer**: [Atılgan Aktaş]
- **Email**: [atilganaktas@example.com]
- **GitHub**: [github.com/theatilgan]

---

⭐ Don't forget to star this project if you liked it! 