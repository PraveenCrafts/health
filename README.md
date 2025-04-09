## project done  by : T.Praveen Kumar Reddy
# Healthy Living - AI-Powered Health & Fitness Platform

A modern, AI-powered health and fitness website that provides personalized recommendations using the Gemini API. The platform features a chatbot for health-related queries and a step-by-step recommendation system for personalized diet plans.

## Features

- **User Authentication**: Secure login and registration system using Firebase
- **AI Chatbot**: Powered by Google's Gemini API for health-related queries
- **Personalized Recommendations**: Step-by-step process for generating custom diet plans
- **BMI Calculator**: Calculate and track your Body Mass Index
- **Modern UI**: Responsive design with dark mode support
- **Download Options**: Export chat conversations and diet plans

## Tech Stack

- **Frontend**: HTML, CSS (Bootstrap), JavaScript
- **Backend**: Flask (Python)
- **Database**: Firebase
- **AI Integration**: Google Gemini API
- **Authentication**: Firebase Auth

## Prerequisites

- Python 3.8 or higher
- Google Gemini API key
- Firebase project credentials

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd healthy-living
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Rename `.env.example` to `.env`
   - Add your Gemini API key and Firebase credentials
   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   FIREBASE_DATABASE_URL=your_firebase_database_url_here
   ```

5. **Set up Firebase**
   - Create a new Firebase project
   - Download the service account key JSON file
   - Save it as `firebase-credentials.json` in the project root

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the website**
   - Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
healthy-living/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables
├── firebase-credentials.json  # Firebase credentials
├── static/
│   ├── css/
│   │   └── style.css     # Custom styles
│   └── js/
│       └── main.js       # Custom JavaScript
└── templates/
    ├── base.html         # Base template
    ├── index.html        # Landing page
    ├── login.html        # Login page
    ├── register.html     # Registration page
    ├── dashboard.html    # User dashboard
    ├── chatbot.html      # AI chatbot interface
    └── recommendations.html  # Diet plan generator
```

## Usage

1. **Registration/Login**
   - Create a new account or login with existing credentials
   - All features require authentication

2. **AI Chatbot**
   - Navigate to the "Try Chatbot" section
   - Ask health-related questions
   - Download chat history as needed

3. **Get Recommendations**
   - Follow the step-by-step process:
     1. Calculate BMI
     2. Select weight goal (loss/gain)
     3. Choose food preference
     4. Select diet intensity
     5. Get personalized plan
   - Download generated diet plans

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Gemini API for AI capabilities
- Firebase for authentication and database
- Bootstrap for UI components
- Font Awesome for icons
- Unsplash for images 
