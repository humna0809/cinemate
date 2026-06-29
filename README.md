# Cinemate 🎬

A personal movie & show watchlist app with AI-powered recommendations. Add what you've watched, track what you want to watch, and let AI suggest your next watch based on your actual taste.

## 📌 Overview

Cinemate is a full-stack web app built with Flask and Supabase. You sign up, build your watchlist by searching real movie titles (with posters pulled automatically), mark things as watched or want-to-watch, and rate what you've seen. When you don't know what to watch next, just describe your mood and an AI agent reads your watch history and recommends something that actually fits your taste.

## ✨ Features

🔐 **Email Auth** — Sign up with email verification, secure login/logout via Supabase Auth

🔍 **Live Movie Search** — Autocomplete search-as-you-type powered by OMDb, no typing exact titles

🖼️ **Auto Posters** — Real movie posters fetched and attached automatically when you add a title

📋 **Two-Tab Watchlist** — Clean separation between "Watched" and "Want to Watch," with ratings only shown for movies you've actually seen

✏️ **Full CRUD** — Add, edit, and delete entries anytime

🤖 **AI Recommendations** — Describe your mood, AI analyzes your watched + watchlist history and suggests one title with a personalized reason

👤 **Private Per-User Data** — Every account only sees its own watchlist, enforced at the database query level

## 🔁 App Architecture

```
[User Signup/Login] 
        │
        ├──→ [Supabase Auth: verify email, create session]
        │
        ▼
[Home: Watched / Want-to-Watch Tabs]
        │
        ├──→ [Add Movie]
        │         └──→ [OMDb Search API: live autocomplete]
        │                   └──→ [Fetch Poster] ──→ [Save to Supabase]
        │
        ├──→ [Edit / Delete Movie] ──→ [Supabase: scoped to user_id]
        │
        └──→ [Recommend Tab]
                  └──→ [Pull user's watched + watchlist titles]
                            └──→ [Groq LLM Agent: llama-3.3-70b-versatile]
                                      └──→ [Parse response] ──→ [Fetch poster] ──→ [Display recommendation]
```

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Flask | Backend web framework |
| Supabase (PostgreSQL) | Database + Auth (email verification, sessions) |
| Groq (Llama 3.3 70B) | AI-powered mood-based recommendations |
| OMDb API | Movie search, metadata, and poster fetching |
| Jinja2 | HTML templating |
| HTML / CSS / vanilla JS | Frontend UI, live search autocomplete |
| Render.com | Free hosting (deploy-ready) |

## 📋 Prerequisites

- Python 3.10+
- A Supabase project (free tier)
- A free Groq API key
- A free OMDb API key

## 🚀 Setup Instructions

### 1. Clone the repo
```
git clone https://github.com/humna0809/cinemate.git
cd cinemate
```

### 2. Install dependencies
```
pip install -r requirements.txt
```

### 3. Set up Supabase

Create a project at [supabase.com](https://supabase.com) and create a `movies` table with these columns:

```
id (auto) | title | genre | rating | status | notes | poster_url | user_id | created_at
```

Enable **Email** auth under Authentication → Providers (enabled by default).

### 4. Get your API keys

- **Supabase** → Project Settings → API → copy URL + anon key
- **Groq** → [console.groq.com](https://console.groq.com) → API Keys → Create Key
- **OMDb** → [omdbapi.com/apikey.aspx](https://omdbapi.com/apikey.aspx) → free tier

### 5. Create your `.env` file
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
GROQ_API_KEY=your_groq_key
OMDB_API_KEY=your_omdb_key
```

### 6. Run the app
```
python app.py
```
Visit `http://localhost:5000`

## 📝 How to Use

1. Sign up with your email → verify via the confirmation email → log in
2. Search for a movie title — pick from live suggestions, poster auto-attaches
3. Choose **Want to Watch** or **Watched** (rating field only appears once marked Watched)
4. Browse your list under the **Watched** / **Want to Watch** tabs
5. Click **Recommend** → describe your mood (e.g. *"something dark and slow-burn like Breaking Bad"*) → get one AI-picked suggestion with a reason and poster

## 🗂️ Database Schema

| Column | Source |
|---|---|
| id | Auto-generated |
| title | User input / OMDb search |
| genre | User input |
| rating | User input (only if status = watched) |
| status | `watched` or `watchlist` |
| notes | User input |
| poster_url | Auto-fetched from OMDb |
| user_id | Supabase Auth session |
| created_at | Auto-generated |

## ⚠️ Known Limitations

- **Render free tier** — sleeps after 15 mins of inactivity if deployed; first request after sleep takes ~30-50s to wake up
- **OMDb free tier** — 1,000 requests/day limit
- **Groq free tier** — rate-limited per minute; heavy back-to-back testing may briefly throttle
- **No password reset flow** — login/signup only, no "forgot password" yet

## 🔧 Customization

**Change the AI model:** in `get_ai_recommendation()`, swap `llama-3.3-70b-versatile` for any other Groq-supported model.

**Add more fields:** extend the `movies` table in Supabase and update the `add`/`edit` routes + templates accordingly.

**Switch poster source:** `get_poster()` can be swapped for TMDb's API if you want richer metadata (cast, trailers, etc).

## 📁 File Structure
```
cinemate/
├── app.py                 # Main Flask app — routes, auth, AI logic
├── requirements.txt       # Python dependencies
├── .env                   # Local secrets (not pushed to GitHub)
├── .gitignore
├── templates/
│   ├── base.html          # Navbar + shared layout
│   ├── index.html         # Watchlist home (tabs)
│   ├── add.html           # Add movie + live search
│   ├── edit.html          # Edit movie
│   ├── login.html
│   ├── signup.html
│   └── recommend.html     # AI recommendation page
└── static/
    └── style.css
```

## 🙏 Credits

Built with Flask, Supabase, Groq, and OMDb — a self-directed summer project to learn full-stack development and AI API integration.

## 📄 License

MIT — free to use, modify, and share.
