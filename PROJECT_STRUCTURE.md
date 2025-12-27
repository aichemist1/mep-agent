# MEP Agent - Project Structure

## Overview
MEP Agent is a web application that converts voice recordings to text and sends them via email with image attachments.

## Directory Structure

```
mep-agent/
├── backend/                    # Backend application code
│   ├── config/                 # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py         # Environment and app settings
│   ├── services/               # Business logic services
│   │   ├── __init__.py
│   │   ├── transcribe_service.py  # AWS Transcribe integration
│   │   └── email_service.py       # AWS SES integration
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   ├── validators.py       # Input validation
│   │   └── file_handler.py     # File operations
│   ├── __init__.py
│   └── app.py                  # Main Flask application
├── frontend/                   # Frontend web interface
│   ├── static/
│   │   ├── style.css          # Styling
│   │   └── script.js          # Client-side logic
│   └── index.html             # Main HTML page
├── uploads/                    # Temporary file uploads
│   └── .gitkeep
├── temp/                       # Processing temporary files
│   └── .gitkeep
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── requirements.txt           # Python dependencies
├── run.sh                     # Quick start script
├── README.md                  # Project overview
├── SETUP.md                   # Setup instructions
├── TESTING.md                 # Testing guide
└── PROJECT_STRUCTURE.md       # This file
```

## Component Descriptions

### Backend Components

#### `backend/app.py`
- Main Flask application
- Defines API endpoints
- Handles request/response flow
- Coordinates services

**Key Endpoints:**
- `GET /` - Serves the web interface
- `POST /api/process` - Main processing endpoint
- `GET /api/health` - Health check

#### `backend/config/settings.py`
- Loads environment variables
- Provides configuration constants
- Validates required settings

#### `backend/services/transcribe_service.py`
- Uploads audio to S3
- Starts AWS Transcribe jobs
- Polls for completion
- Retrieves transcription results
- Cleans up S3 files

#### `backend/services/email_service.py`
- Creates MIME email messages
- Attaches images
- Sends via AWS SES

#### `backend/utils/validators.py`
- Email format validation
- File size validation

#### `backend/utils/file_handler.py`
- Secure file uploads
- File extension checking
- File cleanup operations

### Frontend Components

#### `frontend/index.html`
- Simple, clean form interface
- File upload inputs
- Email and subject fields
- Result display area

#### `frontend/static/style.css`
- Modern, gradient design
- Responsive layout
- Loading states
- Success/error styling

#### `frontend/static/script.js`
- Form submission handling
- AJAX API calls
- Loading state management
- Result display

## Data Flow

```
1. User uploads files via web form
   ↓
2. Frontend sends POST to /api/process
   ↓
3. Backend validates inputs
   ↓
4. Files saved temporarily
   ↓
5. Audio uploaded to S3
   ↓
6. Transcribe job started
   ↓
7. Poll for transcription completion
   ↓
8. Format email with transcript
   ↓
9. Send email via SES with image
   ↓
10. Cleanup temporary files
   ↓
11. Return success/error to frontend
```

## Technology Stack

### Backend
- **Flask** - Web framework
- **boto3** - AWS SDK for Python
- **python-dotenv** - Environment variable management
- **werkzeug** - WSGI utilities (file handling)
- **requests** - HTTP library (for fetching transcripts)

### Frontend
- **Vanilla JavaScript** - No framework dependencies
- **CSS3** - Modern styling with gradients
- **HTML5** - Semantic markup

### AWS Services
- **S3** - Temporary audio file storage
- **Transcribe** - Speech-to-text conversion
- **SES** - Email delivery

## Configuration

All configuration is managed through environment variables in `.env`:

```
AWS_REGION              # AWS region for services
AWS_ACCESS_KEY_ID       # AWS credentials
AWS_SECRET_ACCESS_KEY   # AWS credentials
S3_BUCKET_NAME          # S3 bucket for temp storage
SES_SENDER_EMAIL        # Verified sender email
SES_REGION              # SES region
FLASK_PORT              # Application port (default: 5000)
FLASK_DEBUG             # Debug mode (default: True)
MAX_FILE_SIZE_MB        # Max upload size (default: 25)
ALLOWED_IMAGE_EXTENSIONS # Allowed image types
ALLOWED_AUDIO_EXTENSIONS # Allowed audio types
```

## Security Considerations

1. **File Validation**
   - Extension checking
   - Size limits
   - Secure filename handling

2. **Email Validation**
   - Regex pattern matching
   - SES verification required

3. **Temporary Files**
   - Automatic cleanup after processing
   - Stored outside web root

4. **AWS Credentials**
   - Never committed to git
   - Loaded from environment

## Future Enhancements (Not in MVP)

- User authentication
- File history/tracking
- Multiple recipients
- Email templates
- Real-time recording
- Mobile app
- Offline mode
- Delivery tracking
- Text editing before send
- Multiple language support
- Custom audio formats
- Batch processing

## Development Guidelines

1. **Modularity** - Keep services separate and focused
2. **Error Handling** - Always use try/except with cleanup
3. **Validation** - Validate all inputs
4. **Documentation** - Comment complex logic
5. **Testing** - Test each component independently
6. **Git** - Commit frequently with clear messages