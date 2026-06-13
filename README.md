# AI Fitness & Diet Planner

An intelligent fitness and diet planning application powered by Google Gemini AI, built with Streamlit.

## Features (Phase 1)

- **Modern Dark UI** – Premium glassmorphism design with custom CSS
- **Sidebar Navigation** – Smooth multi-page navigation
- **Session State Management** – Persistent user data across pages
- **Home Page** – Hero section with feature highlights
- **Profile Page** – Comprehensive user data collection
- **Dashboard** – Real-time health metric calculations (BMI, BMR, Calories, Protein, Water)

## Project Structure

```
AI_Fitness_Planner/
├── app.py                   # Main entry point
├── requirements.txt
├── .env                     # API keys (not committed)
├── .gitignore
├── README.md
├── assets/
│   ├── images/
│   └── icons/
├── pages/
│   ├── home.py
│   ├── profile.py
│   └── dashboard.py
├── utils/
│   ├── calculations.py      # BMI, BMR, calorie, protein, water calculations
│   ├── styles.py            # Custom CSS and theming
│   └── session_manager.py   # Session state helpers
└── data/
    └── user_data.csv        # Persisted user profile data
```

## Setup

1. **Clone / open the project folder**

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Add your Gemini API key to `.env`**
   ```
   GOOGLE_API_KEY=your_key_here
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

## Tech Stack

- **Frontend**: Streamlit + Custom CSS (glassmorphism dark theme)
- **AI**: Google Gemini API (`google-generativeai`)
- **Data**: Pandas + CSV persistence
- **Config**: python-dotenv

## Roadmap

- [x] Phase 1 – Core structure, UI, Profile, Dashboard
- [ ] Phase 2 – AI Diet Planner (Gemini-powered meal plans)
- [ ] Phase 3 – AI Workout Planner
- [ ] Phase 4 – AI Coach (chat interface)
- [ ] Phase 5 – Progress Tracker
