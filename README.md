# 🏠 CoHabit — AI-Powered Roommate Matching Platform

> **A full-stack roommate-matching web application designed to help users find compatible roommates based on lifestyle, habits, preferences, and daily routines.**

---

## 📌 Overview

**CoHabit** is a full-stack roommate-matching web application that helps users discover compatible roommates based on their personal preferences and lifestyle habits.

Instead of matching users only on basic profile information, CoHabit considers factors such as:

* 🕐 Daily schedule
* 🧹 Cleanliness preferences
* 🔇 Noise tolerance
* 🔐 Privacy preferences
* 🍽️ Lifestyle habits
* 🛏️ Sleeping patterns
* 🏠 Living preferences
* 👥 Social preferences

The application provides users with personalized roommate recommendations and allows them to interact with profiles through **Like** and **Save** functionality.

---

## 🎯 Problem Statement

Finding a suitable roommate can be difficult because basic information such as age, gender, education, or location does not necessarily indicate whether two people will be compatible.

Two people may have similar backgrounds but completely different:

* Sleeping schedules
* Cleanliness standards
* Social habits
* Privacy requirements
* Study/work routines
* Noise preferences

**CoHabit addresses this problem by focusing on lifestyle compatibility rather than simple profile matching.**

---

## 💡 Solution

CoHabit collects detailed lifestyle and roommate preferences through a multi-step onboarding process.

The collected information is processed by the recommendation system to identify users with compatible preferences.

```text
User Registration
       ↓
OTP Authentication
       ↓
Create Profile
       ↓
Lifestyle & Preference Form
       ↓
Preference Processing
       ↓
Compatibility Matching
       ↓
Recommended Roommates
       ↓
Like / Save / Interact
```

---

# ✨ Key Features

## 🔐 OTP-Based Authentication

Users can authenticate through an OTP-based login flow.

Features include:

* OTP input validation
* Frontend authentication flow
* Backend-ready verification architecture
* Session handling
* Authentication state management

---

## 👤 Multi-Step Profile Creation

Users complete a structured onboarding process instead of filling out one large form.

The profile collects information related to:

### Lifestyle

* Sleeping habits
* Food preferences
* Social habits
* Daily routine

### Cleanliness

* Cleaning frequency
* Organization preferences
* Shared-space expectations

### Privacy

* Personal space requirements
* Guest preferences
* Social interaction preferences

### Schedule

* College/work timings
* Wake-up time
* Sleep time
* Daily availability

---

## 🤖 Roommate Recommendation System

CoHabit analyzes user preferences and identifies potentially compatible roommates.

The matching system can consider multiple compatibility dimensions:

```text
Lifestyle
   +
Schedule
   +
Cleanliness
   +
Privacy
   +
Habits
   ↓
Compatibility Score
   ↓
Recommended Roommates
```

The architecture is designed so that the recommendation logic can be improved or replaced with more advanced AI/ML models in the future.

---

## ❤️ Like & Save Profiles

Users can interact with recommended profiles through:

* ❤️ Like
* 🔖 Save
* 👤 View Profile

This allows users to maintain a personalized list of profiles they are interested in.

---

## 🔔 Notifications

The application includes notification functionality for user interactions and application events.

Examples include:

* New interactions
* Profile activity
* Match-related events
* User actions

---

# 🎨 UI/UX Design

CoHabit uses a **premium warm-brand visual identity** rather than a generic dashboard design.

### Design principles

* Clean navigation
* Responsive layouts
* Card-based profile organization
* Consistent spacing
* Clear call-to-action buttons
* Accessible typography
* Mobile-friendly layouts
* Consistent visual hierarchy

The interface is designed to feel more like a modern consumer product than a traditional college project.

---

# 🏗️ System Architecture

```text
                    ┌──────────────────────┐
                    │       User           │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Frontend UI        │
                    │ HTML + CSS + JS       │
                    └──────────┬───────────┘
                               │
                         REST API Calls
                               │
                               ▼
                    ┌──────────────────────┐
                    │    FastAPI Backend   │
                    │                      │
                    │ Authentication       │
                    │ Profile Management   │
                    │ Recommendations      │
                    │ Interactions         │
                    │ Notifications        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Application Data     │
                    └──────────────────────┘
```

---

# 🔄 Application Workflow

### Step 1 — Authentication

```text
User
 ↓
Enter Login Information
 ↓
Request OTP
 ↓
Verify OTP
 ↓
Authenticated Session
```

### Step 2 — Profile Creation

```text
Authenticated User
 ↓
Basic Information
 ↓
Lifestyle Preferences
 ↓
Schedule Preferences
 ↓
Cleanliness Preferences
 ↓
Privacy Preferences
 ↓
Submit Profile
```

### Step 3 — Matching

```text
User Preferences
       ↓
Preference Processing
       ↓
Compatibility Calculation
       ↓
Candidate Ranking
       ↓
Recommended Profiles
```

### Step 4 — Interaction

```text
Recommended Profile
       ↓
 ┌─────┴─────┐
 ↓           ↓
Like        Save
 ↓           ↓
Interaction Tracking
```

---

# 🛠️ Tech Stack

## Frontend

* HTML5
* CSS3
* JavaScript
* Responsive Web Design

## Backend

* Python
* FastAPI
* REST APIs

## Authentication

* OTP-based authentication
* Session management
* Frontend validation
* Backend verification architecture

## Recommendation

* Preference-based matching
* Compatibility scoring
* Profile ranking

---

# 📁 Project Structure

```text
CoHabit/
│
├── frontend/
│   ├── index.html
│   ├── profile.html
│   ├── preferences.html
│   ├── matches.html
│   │
│   ├── css/
│   │   └── styles.css
│   │
│   ├── js/
│   │   ├── app.js
│   │   ├── auth.js
│   │   ├── profile.js
│   │   └── matches.js
│   │
│   └── assets/
│       ├── images/
│       └── icons/
│
├── backend/
│   ├── main.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── profile.py
│   │   ├── matches.py
│   │   └── interactions.py
│   │
│   ├── models/
│   ├── services/
│   └── database/
│
├── requirements.txt
├── README.md
└── .gitignore
```

> The exact folder structure can be adjusted according to the current implementation.

---

# 🚀 Getting Started

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/CoHabit.git
cd CoHabit
```

---

## 2. Create a Virtual Environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Start the Backend

```bash
uvicorn backend.main:app --reload
```

The FastAPI server will run locally.

---

## 5. Start the Frontend

If the frontend is served separately, run it using a local development server.

For example:

```bash
python -m http.server 8000
```

Then open the application in your browser.

---

# 🔌 API Architecture

The frontend communicates with the backend using REST APIs.

Typical application endpoints include:

```text
POST   /auth/request-otp
POST   /auth/verify-otp

POST   /profile
GET    /profile/{user_id}

GET    /matches/{user_id}

POST   /interactions/like
POST   /interactions/save

GET    /notifications
```

The exact endpoints depend on the current backend implementation.

---

# 🧠 Recommendation Logic

The current architecture is based on **preference compatibility**.

A conceptual compatibility score can be represented as:

```text
Compatibility Score =
    Lifestyle Compatibility
    +
    Schedule Compatibility
    +
    Cleanliness Compatibility
    +
    Privacy Compatibility
    +
    Habit Compatibility
```

The system can then rank potential roommates according to their compatibility.

### Future AI/ML Enhancement

The recommendation engine can be extended using:

* Cosine similarity
* Collaborative filtering
* Content-based recommendation
* K-Nearest Neighbors
* Clustering
* Neural recommendation models
* Learning-to-rank models

This makes the application suitable for further development into a more advanced **AI-powered recommendation platform**.

---

# 🔒 Security Considerations

The application architecture considers:

* OTP-based authentication
* Input validation
* Session management
* API validation
* Separation of frontend and backend responsibilities
* Secure handling of user preferences

For production deployment, additional security measures should be implemented, including:

* HTTPS
* Secure session/token storage
* Rate limiting for OTP requests
* Passwordless authentication safeguards
* API authorization
* Input sanitization
* Environment variables for secrets

---

# 📱 Responsive Design

CoHabit is designed to work across different screen sizes.

```text
Desktop
   ↓
Tablet
   ↓
Mobile
```

Responsive design considerations include:

* Flexible layouts
* Responsive cards
* Mobile navigation
* Scalable typography
* Touch-friendly buttons
* Adaptive spacing

---

# 🌱 Future Scope

CoHabit can be expanded into a complete roommate discovery platform.

### 🤖 AI-Based Matching

Develop a machine-learning recommendation engine that learns from:

* User preferences
* Likes
* Saves
* Successful matches
* Interaction history

### 💬 In-App Messaging

Allow matched users to communicate directly through the platform.

### 📍 Location-Based Matching

Allow users to discover roommates based on:

* College
* Workplace
* City
* Preferred locality
* Distance

### 🧠 Compatibility Insights

Instead of showing only a match percentage:

```text
92% Compatible

✓ Similar sleep schedule
✓ Similar cleanliness preferences
✓ Similar study routine
⚠ Different social preferences
```

This would make recommendations easier to understand.

### 🔔 Smart Notifications

Personalized notifications can be generated based on user activity and matches.

### 📊 User Dashboard

A personalized dashboard could provide:

* Match statistics
* Saved profiles
* Likes
* Compatibility insights
* Interaction history

---

# 🎓 Skills Demonstrated

This project provided hands-on experience in:

* Full-stack web development
* REST API development
* FastAPI
* Python
* JavaScript
* HTML/CSS
* Authentication workflows
* Session management
* Recommendation systems
* API integration
* Responsive UI/UX
* Product design
* Modular application architecture

---
# 🚧 Project Status

**Status:** Active Development 🚀

The core application architecture includes:

* ✅ Responsive frontend
* ✅ Multi-step profile creation
* ✅ Preference collection
* ✅ Backend API architecture
* ✅ Authentication flow
* ✅ Recommendation interface
* ✅ Like/Save interactions
* ✅ Notification architecture

Additional production-level functionality can be added as the project evolves.

---

# 👩‍💻 Author

**Siddhi Hiralkar**

Computer Science & Engineering — Artificial Intelligence & Machine Learning

---

## ⭐ Support

If you find this project interesting, consider giving the repository a ⭐ on GitHub.

**CoHabit — Find a roommate who fits your lifestyle, not just your location.**
