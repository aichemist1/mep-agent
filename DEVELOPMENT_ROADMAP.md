# MEP Agent - Development Roadmap & Flow

## Purpose
This document defines the **recommended flow** for MEP Agent development. All future enhancements must follow this flow to maintain consistency and quality.

**⚠️ IMPORTANT: Always refer to this document before implementing new features.**

---

## Core User Flow (MVP - NOT STARTED)

This is the foundation that must never be broken:

### Step 1: User Interface
1. User opens web application
2. User uploads/captures image file
3. User uploads/records voice file
4. User enters recipient email address
5. User optionally edits email subject
6. User clicks "Preview" (Phase 2)
7. User reviews transcription (original and/or AI-refined)
8. User optionally edits text
9. User clicks "Send"

### Step 2: Processing
1. Backend receives files and form data
2. Validate all inputs:
   - Email format validation
   - File type validation (image: jpg/png/gif, audio: mp3/wav/m4a/ogg)
   - File size validation (max 25MB each)
3. Save files temporarily to `uploads/` directory
4. Upload audio file to S3 bucket
5. Start AWS Transcribe job
6. Poll for transcription completion (max 5 minutes)
7. Retrieve transcription text
8. Format email body with transcription
9. Delete audio from S3

### Step 3: Delivery
1. Create email with:
   - Recipient address
   - Subject line
   - Body text (transcription + greeting/signature)
   - Image attachment
2. Send via AWS SES
3. Receive confirmation (message ID)
4. Cleanup temporary files from `uploads/`
5. Return success/error response to frontend

### Step 4: User Feedback
1. Display success message with transcription preview
2. OR display error message with details
3. Reset form on success
4. Allow user to send another message

---

## Implementation Phases

### ✅ Phase 1: MVP (NOT STARTED)
**Status**: NOT STARTED

**Features**:
- Simple web form interface
- File upload (image + audio)
- AWS Transcribe integration
- AWS SES email delivery
- Basic error handling
- Temporary file cleanup

**Files Created**:
- Backend: `app.py`, `transcribe_service.py`, `email_service.py`, `validators.py`, `file_handler.py`, `settings.py`
- Frontend: `index.html`, `style.css`, `script.js`
- Config: `.env.example`, `requirements.txt`, `.gitignore`
- Docs: `README.md`, `SETUP.md`, `TESTING.md`, `PROJECT_STRUCTURE.md`

---

### ✅ Phase 2: Enhanced User Experience (NOT STARTED)
**Status**: Not started

**Priority Features** (in order):
1. **Text Preview & Edit**
   - Show transcription before sending
   - Allow user to edit text
   - Add "Preview" button before "Send"
   - Split backend into `/api/transcribe` and `/api/send` endpoints
   
2. **LLM Text Refinement**
   - Optional AI-powered text enhancement
   - Remove filler words (um, uh, like, you know)
   - Reformat based on context/industry
   - Show both original and refined versions
   - User can toggle or edit either version
   - Add "Refine with AI" checkbox option
   
3. **Better Error Messages**
   - User-friendly error descriptions
   - Suggestions for fixing issues
   - Retry mechanism

4. **Progress Indicators**
   - Show upload progress
   - Show transcription progress
   - Show LLM refinement progress
   - Estimated time remaining

5. **File Preview**
   - Show image thumbnail before upload
   - Show audio waveform/duration
   - Validate files client-side

**Implementation Order**:
1. Split backend: Create `/api/transcribe` endpoint (returns transcript only)
2. Update frontend with preview UI modal/section
3. Add edit capability for transcription
4. Integrate LLM service for text refinement (AWS Bedrock or OpenAI)
5. Add toggle between original/refined text in preview
6. Update `/api/send` to accept edited transcript
7. Implement progress tracking
8. Add client-side validation

---

### ✅ Phase 3: Advanced Features (NOT STARTED)
**Status**: Not started

**Features Implemented**:
1. ✅ **Multiple Recipients**
   - Support comma-separated emails
   - Validate each email individually
   - Send to all recipients
   - Show recipient count in preview

**Features Skipped**:
2. **Email Templates** - Not needed for MVP, can add later
3. **Real-time Recording** - Not needed for MVP, can add later
4. **User Accounts** - Explicitly skipped per requirements
5. **Delivery Tracking** - Not needed for MVP, can add later

---

### 📋 Phase 4: Mobile & Offline (FUTURE)
**Status**: Not started

**Overview**: Enable mobile access and offline functionality for recording and queuing messages when network unavailable.

---

#### Technical Components

**1. Mobile App (React Native)**
- **Purpose**: Native iOS/Android app with camera and audio recording
- **Architecture**: 
  - Reuse existing Flask backend APIs (`/api/transcribe`, `/api/send`)
  - React Native frontend with native device integrations
  - API client for backend communication
- **Key Features**:
  - Camera integration for image capture
  - Audio recorder for voice recording
  - Form UI matching web version
  - File preview before upload
  - Progress indicators

**2. Offline Recording**
- **Purpose**: Allow users to record when no network available
- **Storage**: AsyncStorage (simple) or SQLite (robust)
- **Data Stored**:
  - Audio files (base64 encoded or file paths)
  - Image files (base64 encoded or file paths)
  - Recipient emails, subject, metadata
  - Timestamp and status
- **Sync Trigger**: Automatic when network detected

**3. Queue Management**
- **Purpose**: Track and sync pending recordings
- **Database Schema** (SQLite):
  ```
  recordings:
    - id (primary key)
    - audio_path (text)
    - image_path (text)
    - recipient_emails (text, comma-separated)
    - subject (text)
    - transcript (text, nullable)
    - refined_transcript (text, nullable)
    - status (pending/uploading/sent/failed)
    - created_at (timestamp)
    - retry_count (integer)
  ```
- **Sync Logic**:
  - Check network connectivity
  - Process queue in FIFO order
  - Retry failed items with exponential backoff
  - Mark as sent on success
  - Keep failed items for manual retry

**4. Push Notifications**
- **Purpose**: Notify user when email delivered
- **Technology**: Firebase Cloud Messaging (FCM)
- **Flow**:
  - Backend sends FCM notification after SES success
  - User receives notification even when app closed
  - Notification shows recipient and timestamp
- **Optional**: Can skip for MVP, add later

---

#### Implementation Strategy

**Recommended Approach** (Incremental):

**Step 1: Basic Mobile App** (Week 1)
- Set up React Native project
- Build UI components (camera, recorder, form)
- Connect to existing backend APIs
- Test on simulators (iOS/Android)
- **Deliverable**: Working mobile app with online-only functionality

**Step 2: Offline Storage** (Week 2)
- Add SQLite database
- Implement local recording storage
- Add queue UI to show pending items
- Test offline recording
- **Deliverable**: App can record offline, shows queue

**Step 3: Sync Mechanism** (Week 3)
- Implement network detection
- Build sync service with retry logic
- Add background sync capability
- Test sync scenarios (online/offline transitions)
- **Deliverable**: Automatic sync when network available

**Step 4: Notifications** (Week 4 - Optional)
- Set up Firebase project
- Add FCM to backend
- Implement notification handling in app
- Test notification delivery
- **Deliverable**: Push notifications on email delivery

---

#### Testing Approach

**Mobile UI Testing**:
- Test on iOS simulator (Xcode)
- Test on Android emulator (Android Studio)
- Test on physical devices (recommended)
- Verify camera and microphone permissions
- Test file size limits and validation

**Offline Mode Testing**:
1. Turn off device network
2. Record multiple messages (audio + image)
3. Verify stored in local queue
4. Turn on network
5. Verify automatic sync
6. Check all emails delivered

**Queue Testing**:
- Create 5+ recordings offline
- Verify queue order (FIFO)
- Test partial failures (some succeed, some fail)
- Verify retry logic
- Test manual retry for failed items

**Notification Testing**:
- Send email while app in foreground
- Send email while app in background
- Send email while app closed
- Verify notification content
- Test notification tap action

**Edge Cases**:
- Network drops during upload
- App killed during sync
- Storage full scenarios
- Large queue (50+ items)
- Concurrent recordings

---

#### Alternative Approaches

**Option A: Web App with Service Workers** (Simpler)
- Add Service Workers to existing web app
- Enable offline recording in browser
- Use IndexedDB for queue storage
- Background sync API for automatic upload
- **Pros**: No mobile app needed, reuse existing code
- **Cons**: Limited device integration, browser-dependent

**Option B: Progressive Web App (PWA)** (Middle Ground)
- Convert existing web app to PWA
- Add manifest.json and service worker
- Enable "Add to Home Screen"
- Offline functionality via Service Workers
- **Pros**: Works on all platforms, simpler than native
- **Cons**: Limited native features

**Option C: Mobile-First, Skip Offline** (Fastest)
- Build React Native app
- Online-only functionality
- No queue or offline storage
- **Pros**: Faster to implement, simpler testing
- **Cons**: Requires network always

---

#### Technology Stack

**Mobile App**:
- React Native (cross-platform)
- React Navigation (routing)
- React Native Camera (image capture)
- React Native Audio Recorder (voice recording)
- Axios (API calls)

**Offline Storage**:
- SQLite (via react-native-sqlite-storage)
- AsyncStorage (simple key-value)
- React Native FS (file system access)

**Notifications**:
- Firebase Cloud Messaging
- react-native-push-notification

**Backend Changes** (Minimal):
- Add FCM notification endpoint (optional)
- No other changes needed

---

#### Recommended Decision

**Before starting Phase 4, choose one**:

1. **Full Mobile + Offline** - Complete Phase 4 as designed (4 weeks)
2. **Mobile Only** - Skip offline, build basic React Native app (1-2 weeks)
3. **PWA Approach** - Convert web app to PWA with offline (2 weeks)
4. **Deploy Current** - Push Phase 1-3 to production, add mobile later

**Recommendation**: Start with Option 2 (Mobile Only) or Option 4 (Deploy Current). Add offline functionality after validating mobile app usage.

---

#### Dependencies

**Required**:
- Node.js and npm
- React Native CLI
- Xcode (for iOS development)
- Android Studio (for Android development)
- Physical devices or simulators

**Optional**:
- Firebase account (for notifications)
- Apple Developer account (for iOS deployment)
- Google Play Developer account (for Android deployment)

---

#### Success Criteria

**Phase 4 Complete When**:
- [ ] Mobile app runs on iOS and Android
- [ ] Can capture image and record audio
- [ ] Can record offline and queue locally
- [ ] Automatic sync when network available
- [ ] Push notifications on delivery (optional)
- [ ] All Phase 1-3 features work on mobile
- [ ] Tested on physical devices
- [ ] Documentation updated

---

## Development Rules

### Must Follow
1. **Always maintain the 3-step flow**: UI → Processing → Delivery
2. **Never skip validation**: Validate at frontend AND backend
3. **Always cleanup**: Delete temporary files in finally blocks
4. **Modular code**: Each service does one thing well
5. **Error handling**: Try/except with meaningful messages
6. **Test incrementally**: Test each feature before moving to next

### Code Organization
```
New features should be added in this order:
1. Update config/settings.py (if new config needed)
2. Add utility functions in utils/ (if needed)
3. Create/update service in services/
4. Update app.py endpoint
5. Update frontend (HTML/CSS/JS)
6. Update documentation
7. Test thoroughly

Phase 2 LLM Integration:
1. Add LLM config to settings.py (API keys, model selection)
2. Create llm_service.py in services/
3. Add /api/transcribe endpoint in app.py
4. Update /api/send to accept edited transcript
5. Add preview modal to frontend
6. Add refinement toggle and comparison view
7. Update documentation with LLM features
```

### File Naming Conventions
- Services: `{service_name}_service.py`
- Utils: `{function_category}.py`
- Frontend: Descriptive names (`style.css`, `script.js`)
- Docs: ALL_CAPS with underscores

### Git Commit Strategy
```
Phase 1: MVP
├── Initial project structure
├── Backend services implementation
├── Frontend interface
└── Documentation and setup

Phase 2: Enhanced UX
├── Add preview functionality
├── Improve error handling
├── Add progress indicators
└── Client-side validation

Phase 3: Advanced features
└── (Each feature gets its own commits)
```

---

## Testing Checklist

Before marking any phase complete, verify:

### Functional Testing
- [ ] All user flows work end-to-end
- [ ] Error cases handled gracefully
- [ ] Files cleaned up properly
- [ ] Email delivered successfully
- [ ] Transcription accurate

### Edge Cases
- [ ] Large files (near 25MB limit)
- [ ] Very short audio (< 5 seconds)
- [ ] Very long audio (> 5 minutes)
- [ ] Special characters in filenames
- [ ] Invalid email formats
- [ ] Network failures
- [ ] AWS service errors

### Performance
- [ ] Response time acceptable (< 2 minutes total)
- [ ] No memory leaks
- [ ] Proper resource cleanup
- [ ] Concurrent requests handled

### Security
- [ ] No file path traversal
- [ ] Email injection prevented
- [ ] File types validated
- [ ] Size limits enforced
- [ ] AWS credentials secure

---

## Decision Log

### Why This Flow?
1. **Simple first**: MVP focuses on core functionality
2. **User-centric**: Each step adds clear user value
3. **Testable**: Each phase can be tested independently
4. **Scalable**: Architecture supports future enhancements

### Technology Choices
- **Flask**: Lightweight, easy to start, Python ecosystem
- **AWS Services**: Reliable, scalable, well-documented
- **Vanilla JS**: No framework overhead for simple UI
- **Modular structure**: Easy to maintain and extend

### What We're NOT Doing (and why)
- ❌ Real-time streaming transcription (MVP too complex)
- ❌ Video support (scope creep)
- ❌ Multiple languages (can add later)
- ❌ Custom ML models (AWS Transcribe sufficient)
- ❌ Database (not needed for MVP)

---

## Future Considerations

### When to Add Database
- User accounts implemented
- Need to store history
- Multiple users sharing data

### When to Add Authentication
- User-specific features needed
- Privacy requirements increase
- Multi-tenant deployment

### When to Refactor
- Code duplication appears
- Performance issues arise
- New patterns emerge

---

## Quick Reference

### Current State
- **Phase**: 3 (Advanced Features)
- **Status**: Phase 3 complete - All core features implemented
- **Next Step**: Phase 4 (Mobile & Offline) or production deployment

### Key Files to Reference
- This file: Development roadmap
- `PROJECT_STRUCTURE.md`: Code organization
- `SETUP.md`: Installation and configuration
- `TESTING.md`: Testing procedures

### Contact Points
- AWS Transcribe: Speech-to-text conversion
- AWS Bedrock (or OpenAI): LLM text refinement (Phase 2)
- AWS SES: Email delivery
- AWS S3: Temporary storage

---

**Last Updated**: 
**Version**: 
**Status**: 