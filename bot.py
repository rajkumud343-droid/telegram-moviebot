import sqlite3
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_ID = 33059989
API_HASH = "03b62232611a24a9dd55ca6739cb8647"
BOT_TOKEN = "8445816050:AAHOkPa6fHplNP1n3rnyw6ek13EWoHzoLos"

ADMIN_ID = 6200452523

app = Client(
    "moviebot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

conn = sqlite3.connect("movies.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS links (
    movie_id INTEGER,
    quality TEXT,
    url TEXT
)
""")

conn.commit()

@app.on_message(filters.command("add") & filters.user(ADMIN_ID))
async def add_movie(client, message):
    try:
        lines = message.text.split("\n")
        movie_name = lines[1]

        cur.execute("INSERT INTO movies (name) VALUES (?)", (movie_name,))
        movie_id = cur.lastrowid

        for line in lines[2:]:
            quality, url = line.split(" ", 1)
            cur.execute(
                "INSERT INTO links (movie_id, quality, url) VALUES (?, ?, ?)",
                (movie_id, quality, url)
            )

        conn.commit()
        await message.reply("Movie added successfully.")

    except:
        await message.reply(
            "Wrong format.\n\n"
            "/add\n"
            "Movie Name\n"
            "720p https://link\n"
            "1080p https://link"
        )

@app.on_message(filters.private & filters.text)
async def search_movie(client, message):
    cur.execute(
        "SELECT id, name FROM movies WHERE name LIKE ?",
        (f"%{message.text}%",)
    )
    movie = cur.fetchone()

    if not movie:
        return

    movie_id, movie_name = movie

    cur.execute(
        "SELECT quality, url FROM links WHERE movie_id=?",
        (movie_id,)
    )
    rows = cur.fetchall()

    buttons = [
        [InlineKeyboardButton(text=q, url=u)] for q, u in rows
    ]

    await message.reply(
        f"🎬 {movie_name}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

app.run()
