# Quick Start Guide

## Starting the Web UI

### 1. Install Dependencies

```bash
# Backend dependencies
cd web_chat/backend
pip install -r requirements.txt

# Or from project root
pip install -r web_chat/backend/requirements.txt
```

### 2. Set Environment Variables

Make sure you have your Gemini API key set:

```bash
export GOOGLE_AI_STUDIO_KEY=your_api_key_here
# or
export GOOGLE_API_KEY=your_api_key_here
```

### 3. Start the Backend Server

```bash
cd web_chat/backend
python app.py
```

The server will start on `http://localhost:5000`

### 4. Open the Frontend

Open your browser and navigate to:
```
http://localhost:5000
```

The Flask server serves the frontend files automatically.

## Testing

Run backend tests:
```bash
pytest tests/backend/ -v
```

## Project Structure

```
web_chat/
├── backend/
│   ├── app.py                 # Flask app with endpoints
│   ├── chat_service.py        # Gemini Agent integration
│   ├── conversation_manager.py
│   ├── config.py
│   ├── errors.py
│   └── requirements.txt
└── frontend/
    ├── index.html
    ├── css/
    │   ├── variables.css
    │   └── styles.css
    └── js/
        ├── app.js
        ├── api.js
        ├── ui.js
        └── utils.js
```

## Features Implemented

✅ Backend API with all endpoints
✅ Frontend HTML/CSS/JS with black & white theme
✅ Message rendering
✅ Function call indicators
✅ Conversation management
✅ Error handling
✅ Responsive design

## Next Steps

- Test the UI in browser
- Add more advanced features (streaming, file uploads, etc.)

