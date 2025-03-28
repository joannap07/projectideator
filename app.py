from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import google.generativeai as genai
import json
import re

load_dotenv()

app = Flask(__name__)

# Initialize Gemini Pro
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# List available models
for m in genai.list_models():
    print(f"Available model: {m.name}")

# Use the correct model name
model = genai.GenerativeModel('models/gemini-1.5-pro-latest')  # Using the latest Gemini 1.5 Pro model

def format_response_as_json(text):
    """Helper function to format text into proper JSON structure"""
    # Basic template for a project idea
    template = {
        "title": "",
        "description": "",
        "technical_concepts": "",
        "estimated_time": ""
    }
    
    try:
        # Try to extract meaningful parts from the text
        lines = text.split('\n')
        current_idea = template.copy()
        ideas = []
        
        for line in lines:
            line = line.strip()
            if not line:  # Skip empty lines
                continue
                
            # Check for new idea starting (indicated by "Title:" or numbered item like "1." or "2.")
            if ('title:' in line.lower()) or re.match(r'^\d+\.?\s*title:', line.lower()):
                # Save previous idea if it exists
                if any(current_idea.values()):
                    # Only add if we have all required fields
                    if all(current_idea.values()):
                        ideas.append(current_idea.copy())
                    current_idea = template.copy()
                current_idea['title'] = line.split(':')[-1].strip()
            elif 'description:' in line.lower():
                current_idea['description'] = line.split(':')[-1].strip()
            elif 'technical concepts:' in line.lower():
                current_idea['technical_concepts'] = line.split(':')[-1].strip()
            elif 'estimated time:' in line.lower() or 'time:' in line.lower():
                current_idea['estimated_time'] = line.split(':')[-1].strip()
        
        # Add the last idea if it's complete
        if any(current_idea.values()) and all(current_idea.values()):
            ideas.append(current_idea.copy())
        
        # If we couldn't parse any complete ideas, try a different parsing approach
        if not ideas:
            # Try to split by numbered items
            sections = re.split(r'\n\d+\.', text)
            if len(sections) > 1:  # If we found numbered sections
                for section in sections[1:]:  # Skip the first split as it's before "1."
                    idea = template.copy()
                    lines = section.split('\n')
                    for line in lines:
                        line = line.strip()
                        if 'title:' in line.lower():
                            idea['title'] = line.split(':')[-1].strip()
                        elif 'description:' in line.lower():
                            idea['description'] = line.split(':')[-1].strip()
                        elif 'technical concepts:' in line.lower():
                            idea['technical_concepts'] = line.split(':')[-1].strip()
                        elif 'estimated time:' in line.lower() or 'time:' in line.lower():
                            idea['estimated_time'] = line.split(':')[-1].strip()
                    if all(idea.values()):
                        ideas.append(idea.copy())
        
        # If we still have no ideas, create a single idea from the text
        if not ideas:
            ideas = [{
                "title": "Generated Project Idea",
                "description": text[:200],
                "technical_concepts": "Various concepts from the description",
                "estimated_time": "Duration not specified"
            }]
        
        return ideas
    except Exception as e:
        print(f"Error in format_response_as_json: {str(e)}")
        return [{
            "title": "Project Idea",
            "description": text[:200],
            "technical_concepts": "Please try generating again",
            "estimated_time": "Unknown"
        }]

def generate_idea(difficulty, num_ideas, keywords, randomness, time_frame):
    # Map time frames to descriptions
    time_frames = {
        'quick': 'less than 1 day',
        'short': '1-3 days',
        'medium': '1-2 weeks',
        'long': '2-4 weeks',
        'extended': 'more than 1 month'
    }
    
    # Create creativity guidance based on randomness level
    creativity_guidance = ""
    if randomness <= 3:
        creativity_guidance = "Generate practical, straightforward technology tool ideas that solve common problems. Focus on proven technologies and standard implementations."
    elif randomness <= 7:
        creativity_guidance = "Generate moderately creative technology tool ideas that combine familiar technologies in interesting ways. Feel free to suggest unique features while keeping the core functionality practical."
    else:
        creativity_guidance = "Generate innovative technology tool ideas that solve problems in unexpected ways. While being creative with the application, ensure the tools remain technically feasible and focused on practical utility."

    # Define technology scope based on difficulty
    tech_scope = {
        'easy': "Use common web technologies (HTML, CSS, JavaScript), basic APIs, or simple scripting languages. Focus on single-purpose tools that solve specific problems.",
        'medium': "Incorporate popular frameworks, databases, or cloud services. Tools can have multiple features but should remain focused on a core functionality.",
        'hard': "Leverage advanced technologies like machine learning, complex APIs, or distributed systems. Tools can be more sophisticated but should still be focused on solving specific problems."
    }
    
    # Adjust the prompt based on parameters
    prompt = f"""Generate {num_ideas} technology tool ideas with these parameters:
Difficulty: {difficulty}
Keywords: {', '.join(keywords)}
Time: {time_frames.get(time_frame, '1-2 weeks')}
Creativity: {randomness}/10

{creativity_guidance}

Technical Scope: {tech_scope.get(difficulty, tech_scope['medium'])}

Format each idea exactly like this:
Title: [Clear name for the tool]
Description: [2-3 sentences about what it does]
Technical Concepts: [Key technologies needed]
Estimated Time: [{time_frames.get(time_frame, '1-2 weeks')}]

Example good titles:
• Weather Dashboard
• Task Tracker
• Time Predictor

IMPORTANT: Use clear, final names without any special characters or placeholders."""

    try:
        # Use Gemini Pro
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.4 + (randomness * 0.08),
                max_output_tokens=1000,
            )
        )
        
        # Print debug information
        print("Response type:", type(response))
        print("Raw response:", response.text)
        
        # Get the response text
        response_text = response.text
        
        # Try to format the response as JSON
        ideas = format_response_as_json(response_text)
        
        # If we didn't get enough ideas, try one more time with a more explicit prompt
        if len(ideas) < num_ideas:
            print(f"Only got {len(ideas)} ideas, trying again...")
            response = model.generate_content(
                prompt + f"\n\nNOTE: You MUST generate exactly {num_ideas} ideas. You only generated {len(ideas)} ideas. Please generate {num_ideas} complete ideas with all required fields.",
                generation_config=genai.types.GenerationConfig(
                    temperature=0.4 + (randomness * 0.08),
                    max_output_tokens=1000,
                )
            )
            response_text = response.text
            ideas = format_response_as_json(response_text)
        
        return ideas
        
    except Exception as e:
        print(f"Error generating ideas: {str(e)}")
        return [{
            "title": "Error Generating Ideas",
            "description": f"An error occurred: {str(e)}. Please try again.",
            "technical_concepts": "Error occurred",
            "estimated_time": "Unknown"
        }]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    difficulty = data.get('difficulty', 'medium')
    num_ideas = int(data.get('numIdeas', 3))
    keywords = data.get('keywords', [])
    randomness = float(data.get('randomness', 5))
    time_frame = data.get('timeFrame', 'medium')
    
    try:
        ideas = generate_idea(difficulty, num_ideas, keywords, randomness, time_frame)
        return jsonify({'ideas': ideas})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Run the app on 0.0.0.0 to make it accessible from any host, using port 5001
    app.run(debug=True, host='0.0.0.0', port=5001) 