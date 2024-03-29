from flask_app import app
from flask import render_template, redirect, request, session
from flask_app.models import models_game
from pprint import pprint
import requests
import os
from playsound import playsound

# API Keys
header = os.environ.get('KEY')
header2 = os.environ.get('rapid_api_key')

# Helper function for changing the "games" page
def make_request(url):
    headers = {
        "X-RapidAPI-Key": f"{header2}",
        "X-RapidAPI-Host": "rawg-video-games-database.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers)
    return response.json()

# Route for rendering the "games" page.
@app.get('/games')
def render_games_page():
    if 'user_id' not in session:
        return redirect('/logout')

    # Default games page url.
    if not 'url' in session:
        session['url'] = f"https://rawg-video-games-database.p.rapidapi.com/games?key={header}"

    json = make_request(session['url'])
    results = json['results']
    # pprint(results)

    # Data dictionary that is getting a page's url from the API.
    info = {
        "previous_page": json['previous'],
        "next_page": json['next']
    }

    # Empty games list
    games = []

    """For loop that creates a game object and appends that
    game object to the games list."""

    for result in results:
        game = {
            "id": result['id'],
            "name": result['name'],
            "background_image": result['background_image'],
            "playtime": result['playtime'],
            "ratings_count": result['ratings_count'],
            # "released": result['released'],
            # "platforms": result['platforms'][0]['platform']['name'],
            "rating": result['rating'],
            # "esrb_rating": result['esrb_rating']['name'],
            "genres": result['genres'][0]['name'],
            # "description": result['description_raw']
        }
        games.append(game)

    return render_template('games.html', games=games, info=info)


# Route for rendering the Show game details page.
@app.get('/show_game/details')
def show_game_details():
    if 'user_id' not in session:
        return redirect('/logout')
    return render_template('show_game_details.html')


# POST ROUTES
# Route for changing the "Games" page.
@app.post('/url/set')
def set_url():
    if 'user_id' not in session:
        return redirect('/logout')
    session['url'] = request.form['url']
    return redirect('/games')

# Route for searching for a game.
@app.post('/search_game/details')
def search_game_details():
    if 'user_id' not in session:
        return redirect('/')

    id = request.form['name']
    # API requires the id.
    url = f"https://api.rawg.io/api/games/{id}?key={header}"
    response = requests.get(url)

    session['game_id'] = response.json()['id']
    session['image'] = response.json()['background_image']
    session['name'] = response.json()['name']
    session['developer'] = response.json()['developers'][0]['name']
    session['release_date'] = response.json()['released']
    session['play_time'] = response.json()['playtime']
    genres = response.json()['genres']
    session['genres'] = []
    for i in range(len(genres)):
        session['genres'].append(response.json()['genres'][i]['name'])
    session['rating'] = response.json()['rating']
    if response.json()['esrb_rating'] == None:
        session['esrb_rating'] = 'Not Available'
    else:
        session['esrb_rating'] = response.json()['esrb_rating']['name']
    session['achievements_count'] = response.json()['achievements_count']
    platforms = response.json()['platforms']
    session['platforms'] = []
    for i in range(len(platforms)):
        session['platforms'].append(response.json()['platforms'][i]['platform']['name'])
    print(session['platforms'])
    session['description'] = response.json()['description_raw']

    # return response.json()
    return redirect('/show_game/details')

# Route for clicking game details.
@app.post('/click_game/details/')
def click_game_details():
    if 'user_id' not in session:
        return redirect('/')

    id = request.form['game_id']
    url = f"https://api.rawg.io/api/games/{id}?key={header}"
    response = requests.get(url)

    session['game_id'] = response.json()['id']
    session['image'] = response.json()['background_image']
    session['name'] = response.json()['name']
    session['developer'] = response.json()['developers'][0]['name']
    session['release_date'] = response.json()['released']
    session['play_time'] = response.json()['playtime']
    genres = response.json()['genres']
    session['genres'] = []
    for i in range(len(genres)):
        session['genres'].append(response.json()['genres'][i]['name'])
    session['rating'] = response.json()['rating']
    if response.json()['esrb_rating'] == None:
        session['esrb_rating'] = 'Not Available'
    else:
        session['esrb_rating'] = response.json()['esrb_rating']['name']
    session['achievements_count'] = response.json()['achievements_count']
    platforms = response.json()['platforms']
    session['platforms'] = []
    for i in range(len(platforms)):
        session['platforms'].append(response.json()['platforms'][i]['platform']['name'])
    print(session['platforms'])
    session['description'] = response.json()['description_raw']

    return redirect('/show_game/details')

# Route for adding a new game to the user's collection.
@app.post('/add_game/collection')
def add_game_to_collection():
    if 'user_id' not in session:
        return redirect('/logout')

    id = request.form['id']
    url = f"https://api.rawg.io/api/games/{id}?key={header}"
    response = requests.get(url)

    game = {
        "game_id": response.json()['id'],
        "name": response.json()['name'],
        "background_image": response.json()['background_image'],
        "playtime": response.json()['playtime'],
        "released": response.json()['released'],
        "rating": response.json()['rating'],
        "esrb_rating": response.json()['esrb_rating']['name'],
        "genre": response.json()['genres'][0]['name'],
        "platform": response.json()['platforms'][0]['platform']['name'],
        "description": response.json()['description_raw'],
        "user_id": session['user_id']
    }
    models_game.Game.save_game(game)
    session['collection_count'] += 1
    playsound('flask_app/static/audio/game_start.mp3', block=False)
    return redirect('/games')