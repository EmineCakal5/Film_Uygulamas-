import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  
DB_NAME = "example.db"

def fetch_movie_details(title):
    API_KEY = "be09f913" 
    url = f"http://www.omdbapi.com/?t={title}&apikey={API_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("Response") == "True":
            try:
                return {
                    "title": data["Title"],
                    "year": int(data["Year"]),
                    "score": float(data.get("imdbRating", 0.0)),
                    "poster": data.get("Poster", None)
                }
            except:
                return None
    return None


# Veritabanını başlat ve örnek verileri ekle
def init_db():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS movie (
            title TEXT,
            year INTEGER,
            score REAL,
            poster TEXT
        )
    """)

    cur.execute("""             
        CREATE TABLE IF NOT EXISTS favorites (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         title TEXT,
         year INTEGER,
         score REAL,
         poster TEXT          
        )
    """)

    cur.execute("DELETE FROM movie")
    con.commit()
    con.close()





# FAVORİ EKLE
@app.route("/favorites", methods=["POST"])
def add_favorite():
    data = request.json
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO favorites (title, year, score, poster)
        VALUES (?, ?, ?, ?)
    """, (data["title"], data["year"], data["score"], data["poster"]))
    conn.commit()
    conn.close()
    return jsonify({"message": "Favorilere eklendi!"})

# FAVORİLERİ GETİR
@app.route("/favorites", methods=["GET"])
def get_favorites():
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM favorites")
    rows = cursor.fetchall()
    conn.close()
    favorites = [{
        "id": row[0],
        "title": row[1],
        "year": row[2],
        "score": row[3],
        "poster": row[4]
    } for row in rows]
    return jsonify(favorites)


# Ana endpoint: Tüm filmleri getir (yıla göre sıralı)
@app.route("/", methods=["GET"])
def get_all_movies():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("SELECT title, year, score, poster FROM movie ORDER BY year ASC")
    rows = cur.fetchall()
    con.close()
    result = [{"title": title, "year": year, "score": score, "poster": poster} for  title, year, score, poster in rows]
    return jsonify(result)

# Belirli bir yıl için film getir: /movies?year=1983
@app.route("/movies", methods=["GET"])
def get_movies_by_year():
    year = request.args.get("year")
    if not year:
        return jsonify({"error": "Lütfen bir yıl belirtin. Örnek: /movies?year=1983"}), 400

    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("SELECT title, score FROM movie WHERE year = ?", (year,))
    rows = cur.fetchall()
    con.close()

    if not rows:
        return jsonify({"message": f"{year} yılına ait film bulunamadı."}), 404

    result = [{"title": title, "score": score} for title, score in rows]
    return jsonify(result)

# POST: Yeni film ekle
@app.route("/movies", methods=["POST"])
def add_movie():
    data = request.get_json()
    title = data.get("title")

    if not title:
        return jsonify({"error": "Lütfen sadece 'title' alanını gönderin."}), 400

    movie = fetch_movie_details(title)

    if not movie:
        return jsonify({"error": "Film bilgisi bulunamadı ya da çekilemedi."}), 404

    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("INSERT INTO movie (title, year, score, poster) VALUES (?, ?, ?, ?)",
                (movie["title"], movie["year"], movie["score"],movie["poster"]))
    con.commit()
    con.close()

    return jsonify({
        "message": "Film başarıyla eklendi.",
        "title": movie["title"],
        "year": movie["year"],
        "score": movie["score"]
    }), 201




# DELETE: Belirli bir yıldaki tüm filmleri sil (path param ile)
@app.route("/movies/<int:year>", methods=["DELETE"])
def delete_movies_by_year(year):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM movie WHERE year = ?", (year,))
    count = cur.fetchone()[0]

    if count == 0:
        con.close()
        return jsonify({"message": f"{year} yılına ait silinecek film bulunamadı."}), 404

    cur.execute("DELETE FROM movie WHERE year = ?", (year,))
    con.commit()
    con.close()

    return jsonify({"message": f"{count} film başarıyla silindi.", "year": year}), 200

# GET: Başlığa göre film ara
@app.route("/search", methods=["GET"])
def search_movie_by_title():
    title_query = request.args.get("title")

    if not title_query:
        return jsonify({"error": "Lütfen 'title' query parametresi girin. Örnek: /search?title=life"}), 400

    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    # LIKE ile arama (case-insensitive)
    cur.execute("SELECT title, year, score FROM movie WHERE title LIKE ?", (f"%{title_query}%",))
    rows = cur.fetchall()
    con.close()

    if not rows:
        return jsonify({"message": "Eşleşen film bulunamadı."}), 404

    result = [{"title": title, "year": year, "score": score} for title, year, score in rows]
    return jsonify(result), 200


# PUT: Film güncelle (title'a göre yıl değiştir)
@app.route("/movies", methods=["PUT"])
def update_movie():
    data = request.get_json()
    title = data.get("title")
    year = data.get("year")

    if not title or not year:
        return jsonify({"error": "Eksik bilgi: 'title' ve 'year' gereklidir."}), 400

    try:
        year = int(year)
    except ValueError:
        return jsonify({"error": "Yıl sayısal olmalıdır."}), 400

    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM movie WHERE title = ?", (title,))
    exists = cur.fetchone()[0]

    if exists == 0:
        con.close()
        return jsonify({"error": f"'{title}' başlıklı film bulunamadı."}), 404

    cur.execute("UPDATE movie SET year = ? WHERE title = ?", (year, title))
    con.commit()
    con.close()

    return jsonify({"message": f"'{title}' filmi güncellendi.", "year": year}), 200


# Uygulamayı çalıştır
if __name__ == "__main__":
    init_db()
    app.run(port=5001, debug=True)