# Project Ideator

A web application that generates technology tool ideas based on various parameters like difficulty, time frame, and creativity level.

## Features

- Generate multiple project ideas at once
- Adjustable difficulty levels (easy, medium, hard)
- Customizable time frames (quick, short, medium, long, extended)
- Creativity control slider
- Keyword-based idea generation
- Modern, responsive UI

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/projectideator.git
cd projectideator
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your Google API key:
```
GOOGLE_API_KEY=your-api-key-here
```

5. Run the application:
```bash
python app.py
```

The application will be available at http://localhost:5001

## Environment Variables

- `GOOGLE_API_KEY`: Your Google AI API key (required)

## Deployment

This application can be deployed to various platforms like Heroku, Google Cloud Platform, or AWS. Make sure to set up the environment variables in your deployment platform.

## License

MIT License - feel free to use this project for your own purposes. 