import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from dotenv import load_dotenv
import json
import firebase_admin
from firebase_admin import credentials, auth, db

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Load environment variables
load_dotenv()

# Initialize Firebase Admin
cred = credentials.Certificate('firebase-credentials.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': os.getenv('FIREBASE_DATABASE_URL')
})

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Define a function to get the AI model when needed instead of at startup
def get_ai_model():
    import google.generativeai as genai
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set")
    
    genai.configure(api_key=api_key)
    
    # Print available models to help with debugging
    try:
        print("Available models:")
        for m in genai.list_models():
            print(f"- {m.name}")
    except Exception as e:
        print(f"Error listing models: {str(e)}")
    
    # Use gemini-pro which is available on the free tier
    # For version 0.3.2, model names must start with "models/"
    model_name = "models/gemini-pro"
    
    # Configure safety settings - less restrictive for health advice
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"}
    ]
    
    return genai, model_name, safety_settings

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.get_user_by_email(email)
            # In a real application, you would verify the password here
            login_user(User(user.uid))
            flash('Logged in successfully!', 'success')
            
            # Check if there's a next parameter
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f'Login failed: {str(e)}', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.create_user(
                email=email,
                password=password
            )
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'error')
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/chatbot')
@login_required
def chatbot():
    return render_template('chatbot.html')

@app.route('/get-ai-response', methods=['POST'])
@login_required
def get_ai_response():
    try:
        import google.generativeai as genai
        
        user_input = request.json.get('message', '')
        if not user_input.strip():
            return jsonify({'response': 'Please enter a question about health or fitness.'})
        
        print(f"Processing chatbot request: '{user_input}'")
        
        # Set API key
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            return jsonify({'response': 'API key not configured. Please add your Google API key to the .env file.'})
            
        genai.configure(api_key=api_key)
        
        # Check if input is a basic greeting or small talk
        greeting_words = ['hi', 'hello', 'hey', 'hola', 'howdy', 'greetings', 'good morning', 'good afternoon', 'good evening']
        smalltalk_phrases = ['how are you', 'what can you do', 'who are you', 'tell me about yourself', 'what is your name']
        
        # Convert to lowercase and remove punctuation for comparison
        cleaned_input = user_input.lower().strip().rstrip('.!?')
        
        # Check for greetings (including variations with extra letters like "hiii")
        is_greeting = any(cleaned_input.startswith(greeting) for greeting in greeting_words) or any(greeting in cleaned_input.split() for greeting in greeting_words)
        
        # Check for small talk
        is_smalltalk = any(phrase in cleaned_input for phrase in smalltalk_phrases)
        
        # Determine the appropriate prompt based on message type
        if is_greeting:
            prompt = f"""As a health and wellness assistant, respond to this greeting: "{user_input}"

Create a warm, personalized response that:
1. Acknowledges their greeting specifically
2. Introduces yourself briefly as a health and wellness assistant 
3. Shows enthusiasm to help with their health questions
4. Uses 1-2 appropriate emojis to add warmth

Keep it casual, friendly and brief (2-3 sentences). Make it sound like a human conversation, not a templated response."""
            
        elif is_smalltalk:
            prompt = f"""As a health and wellness assistant, respond to this question: "{user_input}"

Create a friendly, personalized response that:
1. Directly addresses their specific question
2. Keeps the focus on health and wellness
3. Shows personality and warmth
4. Offers to help with health-related topics
5. Uses 1-2 appropriate emojis

Keep it conversational and authentic - avoid sounding like a generic AI response."""
            
        else:
            prompt = f"""You are a personalized health and wellness assistant having a one-on-one conversation. 
The person has just asked: "{user_input}"

Respond directly to their specific question with a tailored, helpful answer about health, nutrition, fitness, or wellness.

Guidelines for your response:
1. Start by directly addressing their specific question - don't use generic introductions
2. Make your response conversational and natural, like a knowledgeable friend would talk
3. Include relevant, evidence-based information
4. Use some emojis where appropriate to add warmth
5. Format using Markdown to enhance readability
6. If appropriate, include one interesting fact related to their specific question
7. End with a brief, relevant medical disclaimer only if providing health advice

Your response should feel personal and specific to their question, not like a generic article or template."""
        
        print("Sending request to Gemini API...")
        
        # Try to use GenerativeModel (newer API) first
        try:
            # Check available models
            available_models = [model.name for model in genai.list_models()]
            print(f"Available models: {available_models}")
            
            # Get the best available model
            model_name = "gemini-1.5-flash"  # First preference
            if not any("gemini-1.5" in model for model in available_models):
                # Fall back to gemini-pro if 1.5 is not available
                model_name = "gemini-pro"
                print(f"Falling back to {model_name}")
            
            # Configure the model with settings that encourage more creative, varied responses
            generation_config = {
                "temperature": 0.8,  # Higher temperature for more creative responses
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 800,
            }
            
            model = genai.GenerativeModel(model_name)
            
            # Generate content with creativity-enhancing settings
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            response_text = response.text
            
            print(f"Received response from {model_name}: {len(response_text)} characters")
                
            # Add disclaimer if needed (but only for specific health advice, not for greetings/small talk)
            if not (is_greeting or is_smalltalk) and not any(phrase in response_text.lower() for phrase in ["consult", "healthcare", "medical professional", "doctor", "disclaimer"]):
                disclaimer = "\n\n*Note: This is general advice. Please consult healthcare professionals for medical concerns.*"
                response_text += disclaimer
                
            return jsonify({'response': response_text})
            
        except Exception as e:
            print(f"Error with GenerativeModel API: {str(e)}")
            print("Falling back to generate_text API...")
            
            # Fall back to older API method
            try:
                # For older versions of the API
                model = 'gemini-pro'  # Use the most widely supported model
                
                response = genai.generate_text(
                    model=model,
                    prompt=prompt,
                    temperature=0.8,  # Higher temperature for more creative responses
                    max_output_tokens=800,
                    top_k=40,
                    top_p=0.95,
                )
                
                # Handle different response structures
                if hasattr(response, 'result'):
                    response_text = response.result
                elif hasattr(response, 'text'):
                    response_text = response.text
                else:
                    # Try to extract text from response object
                    response_text = str(response)
                    if not response_text or len(response_text) < 20:
                        raise ValueError("Received empty or invalid response from API")
                
                print(f"Received response from fallback API: {len(response_text)} characters")
                
                # Add disclaimer if needed (but only for specific health advice, not for greetings/small talk)
                if not (is_greeting or is_smalltalk) and not any(phrase in response_text.lower() for phrase in ["consult", "healthcare", "medical professional", "doctor", "disclaimer"]):
                    disclaimer = "\n\n*Note: This is general advice. Please consult healthcare professionals for medical concerns.*"
                    response_text += disclaimer
                    
                return jsonify({'response': response_text})
                
            except Exception as nested_e:
                print(f"Error with fallback API: {str(nested_e)}")
                raise nested_e
            
    except Exception as e:
        import traceback
        print(f"Error in AI response: {str(e)}")
        print(traceback.format_exc())
        
        return jsonify({
            'response': f"I apologize, but I couldn't process your request due to a technical issue: {str(e)}\n\nPlease try again with a different question or check your API key settings.",
            'error': str(e)
        })

@app.route('/recommendations')
@login_required
def recommendations():
    return render_template('recommendations.html')

@app.route('/calculate-bmi', methods=['POST'])
@login_required
def calculate_bmi():
    try:
        weight = float(request.json.get('weight'))
        height = float(request.json.get('height'))
        bmi = weight / (height * height)
        
        # Get BMI category
        category = ""
        if bmi < 18.5:
            category = "Underweight"
        elif bmi < 25:
            category = "Normal weight"
        elif bmi < 30:
            category = "Overweight"
        else:
            category = "Obese"
            
        return jsonify({
            'bmi': round(bmi, 2),
            'category': category
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/generate-diet-plan', methods=['POST'])
@login_required
def generate_diet_plan():
    try:
        import google.generativeai as genai
        
        data = request.json
        
        print(f"Generating diet plan for: BMI: {data.get('bmi', 'Not specified')}, Category: {data.get('category', 'Not specified')}")
        
        # Set API key
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            return jsonify({'plan': 'API key not configured. Please add your Google API key to the .env file.'})
            
        genai.configure(api_key=api_key)
        
        # Create detailed prompt for diet plan
        prompt = f"""Create a detailed 7-day meal plan formatted in Markdown for someone with:
- BMI: {data.get('bmi', 'Not specified')} ({data.get('category', 'Not specified')})
- Goal: {data.get('goal', 'Not specified')}
- Diet preference: {data.get('foodType', 'Not specified')} ({data.get('dietType', 'Not specified')})

Structure your response as follows:
1. Start with a "# 🍽️ Personalized 7-Day Meal Plan 🥗" header
2. Include a "## Plan Overview" section with profile information
3. Format each day clearly with proper markdown headers and organized meals
4. Include nutritional breakdown and calorie target
5. Add hydration recommendations 
6. Include meal prep tips
7. End with a disclaimer about consulting professionals

Use emojis to make the plan visually appealing. Include specific portion sizes, meal timing, and variety of foods."""
        
        print("Sending request to Gemini API for diet plan...")
        
        # Try to use GenerativeModel (newer API) first
        try:
            # Check available models
            available_models = [model.name for model in genai.list_models()]
            print(f"Available models: {available_models}")
            
            # Get the best available model
            model_name = "gemini-1.5-flash"  # First preference
            if not any("gemini-1.5" in model for model in available_models):
                # Fall back to gemini-pro if 1.5 is not available
                model_name = "gemini-pro"
                print(f"Falling back to {model_name}")
            
            model = genai.GenerativeModel(model_name)
            
            # Generate content
            response = model.generate_content(prompt)
            diet_plan = response.text
            
            print(f"Received diet plan from {model_name}: {len(diet_plan)} characters")
                
            # Add disclaimer if needed
            if not any(phrase in diet_plan.lower() for phrase in ["consult", "dietitian", "nutritionist", "healthcare", "professional", "disclaimer"]):
                disclaimer = "\n\n*Note: This meal plan is a general suggestion. Please consult with a registered dietitian for personalized advice.*"
                diet_plan += disclaimer
                
            return jsonify({'plan': diet_plan})
            
        except Exception as e:
            print(f"Error with GenerativeModel API: {str(e)}")
            print("Falling back to generate_text API...")
            
            # Fall back to older API method
            try:
                # For older versions of the API
                model = 'gemini-pro'  # Use the most widely supported model
                
                response = genai.generate_text(
                    model=model,
                    prompt=prompt,
                    temperature=0.7,
                    max_output_tokens=1500,
                    top_k=40,
                    top_p=0.95,
                )
                
                # Handle different response structures
                if hasattr(response, 'result'):
                    diet_plan = response.result
                elif hasattr(response, 'text'):
                    diet_plan = response.text
                else:
                    # Try to extract text from response object
                    diet_plan = str(response)
                    if not diet_plan or len(diet_plan) < 20:
                        raise ValueError("Received empty or invalid response from API")
                
                print(f"Received diet plan from fallback API: {len(diet_plan)} characters")
                
                # Add disclaimer if needed
                if not any(phrase in diet_plan.lower() for phrase in ["consult", "dietitian", "nutritionist", "healthcare", "professional", "disclaimer"]):
                    disclaimer = "\n\n*Note: This meal plan is a general suggestion. Please consult with a registered dietitian for personalized advice.*"
                    diet_plan += disclaimer
                    
                return jsonify({'plan': diet_plan})
                
            except Exception as nested_e:
                print(f"Error with fallback API: {str(nested_e)}")
                raise nested_e
            
    except Exception as e:
        import traceback
        print(f"Error in diet plan generation: {str(e)}")
        print(traceback.format_exc())
        
        return jsonify({
            'error': str(e),
            'plan': f"I apologize, but I couldn't generate a diet plan due to a technical issue: {str(e)}\n\nPlease try again or check your API key settings."
        }), 400

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True) 