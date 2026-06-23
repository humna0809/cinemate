from flask import Flask, render_template, request, redirect, url_for, session , jsonify
import os
from supabase import create_client
from dotenv import load_dotenv
import requests
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-2.0-flash')

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # needed for sessions

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)



@app.route('/search-movies')
def search_movies():
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    
    response = requests.get(f"http://www.omdbapi.com/?s={query}&apikey={os.getenv('OMDB_API_KEY')}")
    data = response.json()
    
    results = []
    if data.get('Search'):
        for movie in data['Search'][:6]:  # limit to 6 suggestions
            results.append({
                "title": movie['Title'],
                "year": movie['Year'],
                "poster": movie['Poster']
            })
    return jsonify(results)

@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    tab = request.args.get('tab', 'watched')  # default tab
    
    response = supabase.table('movies').select('*').eq('user_id', session['user_id']).eq('status', tab).order('created_at', desc=True).execute()
    movies = response.data
    return render_template('index.html', movies=movies, user=session['user'], active_tab=tab) 

@app.route('/add', methods=['GET', 'POST'])
def add_movie():
    if request.method == 'POST':
        poster_url = get_poster(request.form['title'])
        rating = request.form.get('rating')
        supabase.table('movies').insert({
            "title": request.form['title'],
            "genre": request.form['genre'],
            "rating": int(rating) if rating else None,
            "status": request.form['status'],
            "notes": request.form['notes'],
            "user_id": session['user_id'],
            "poster_url": poster_url
        }).execute()
        return redirect(url_for('home'))
    return render_template('add.html')

@app.route('/delete/<int:id>')
def delete_movie(id):
    supabase.table('movies').delete().eq('id', id).eq('user_id', session['user_id']).execute()
    return redirect(url_for('home'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_movie(id):
    if request.method == 'POST':
        rating = request.form.get('rating')
        supabase.table('movies').update({
            "title": request.form['title'],
            "genre": request.form['genre'],
            "rating": int(rating) if rating else None,
            "status": request.form['status'],
            "notes": request.form['notes']
        }).eq('id', id).eq('user_id', session['user_id']).execute()
        return redirect(url_for('home'))
    
    movie = supabase.table('movies').select('*').eq('id', id).eq('user_id', session['user_id']).execute().data[0]
    return render_template('edit.html', movie=movie)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            return render_template('signup.html', message="Check your email to verify your account!")
        except Exception as e:
            return render_template('signup.html', error=str(e))
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            session['user'] = response.user.email
            session['user_id'] = response.user.id
            return redirect(url_for('home'))
        except Exception as e:
            return render_template('login.html', error="Invalid email or password")
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    supabase.auth.sign_out()
    return redirect(url_for('login'))

def get_poster(title):
    try:
        response = requests.get(f"http://www.omdbapi.com/?t={title}&apikey={os.getenv('OMDB_API_KEY')}")
        data = response.json()
        if data.get('Poster') and data['Poster'] != 'N/A':
            return data['Poster']
    except:
        pass
    return "https://via.placeholder.com/300x445/161b22/888?text=No+Poster"



def get_ai_recommendation(mood, watched_movies, watchlist_movies):
    watched_titles = ", ".join([m['title'] for m in watched_movies]) or "none yet"
    watchlist_titles = ", ".join([m['title'] for m in watchlist_movies]) or "none yet"

    prompt = f"""You are a movie recommendation assistant.

User's watched movies: {watched_titles}
User's watchlist (already wants to watch): {watchlist_titles}

User's mood/request: "{mood}"

Based on their taste from watched movies, suggest ONE movie or show that fits their mood.
Don't suggest anything already in their watched list or watchlist.
Respond in this exact format:

TITLE: [movie/show name]
REASON: [2-3 sentence friendly explanation of why this fits, referencing their taste]
"""

    response = gemini_model.generate_content(prompt)
    return response.text

@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    recommendation = None
    
    if request.method == 'POST':
        mood = request.form['mood']
        
        watched = supabase.table('movies').select('title').eq('user_id', session['user_id']).eq('status', 'watched').execute().data
        watchlist = supabase.table('movies').select('title').eq('user_id', session['user_id']).eq('status', 'watchlist').execute().data
        
        ai_response = get_ai_recommendation(mood, watched, watchlist)
        
        lines = ai_response.split('\n')
        title = ""
        reason = ""
        for line in lines:
            if line.startswith('TITLE:'):
                title = line.replace('TITLE:', '').strip()
            elif line.startswith('REASON:'):
                reason = line.replace('REASON:', '').strip()
        
        poster_url = get_poster(title)
        
        recommendation = {
            "title": title,
            "reason": reason,
            "poster": poster_url
        }
    
    return render_template('recommend.html', recommendation=recommendation)

if __name__ == '__main__':
    app.run(debug=True)