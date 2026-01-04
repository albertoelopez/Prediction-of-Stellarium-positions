#!/usr/bin/env python3
"""
Database Setup Script
Downloads and configures the Bible database and ChromaDB for semantic search.
"""

import os
import sqlite3
import urllib.request
import zipfile
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data"
BIBLE_DB_PATH = DATA_DIR / "bible.db"
CHROMA_DB_PATH = DATA_DIR / "chroma_db"

BIBLE_DATABASES = {
    "scrollmapper": {
        "url": "https://github.com/scrollmapper/bible_databases/raw/master/sqlite/bible-sqlite.db",
        "description": "ScrollMapper Bible Database with cross-references",
    },
}

COSMIC_VERSES = [
    {"book": "Joel", "chapter": 2, "verse": 31, "text": "The sun shall be turned into darkness, and the moon into blood, before the great and terrible day of the LORD come."},
    {"book": "Matthew", "chapter": 24, "verse": 29, "text": "Immediately after the tribulation of those days shall the sun be darkened, and the moon shall not give her light, and the stars shall fall from heaven, and the powers of the heavens shall be shaken."},
    {"book": "Revelation", "chapter": 6, "verse": 12, "text": "And I beheld when he had opened the sixth seal, and, lo, there was a great earthquake; and the sun became black as sackcloth of hair, and the moon became as blood."},
    {"book": "Revelation", "chapter": 6, "verse": 13, "text": "And the stars of heaven fell unto the earth, even as a fig tree casteth her untimely figs, when she is shaken of a mighty wind."},
    {"book": "Isaiah", "chapter": 13, "verse": 10, "text": "For the stars of heaven and the constellations thereof shall not give their light: the sun shall be darkened in his going forth, and the moon shall not cause her light to shine."},
    {"book": "Luke", "chapter": 21, "verse": 25, "text": "And there shall be signs in the sun, and in the moon, and in the stars; and upon the earth distress of nations, with perplexity; the sea and the waves roaring."},
    {"book": "Luke", "chapter": 21, "verse": 26, "text": "Men's hearts failing them for fear, and for looking after those things which are coming on the earth: for the powers of heaven shall be shaken."},
    {"book": "Revelation", "chapter": 12, "verse": 1, "text": "And there appeared a great wonder in heaven; a woman clothed with the sun, and the moon under her feet, and upon her head a crown of twelve stars."},
    {"book": "Revelation", "chapter": 12, "verse": 2, "text": "And she being with child cried, travailing in birth, and pained to be delivered."},
    {"book": "Amos", "chapter": 5, "verse": 8, "text": "Seek him that maketh the seven stars and Orion, and turneth the shadow of death into the morning, and maketh the day dark with night."},
    {"book": "Job", "chapter": 38, "verse": 31, "text": "Canst thou bind the sweet influences of Pleiades, or loose the bands of Orion?"},
    {"book": "Job", "chapter": 38, "verse": 32, "text": "Canst thou bring forth Mazzaroth in his season? or canst thou guide Arcturus with his sons?"},
    {"book": "Numbers", "chapter": 24, "verse": 17, "text": "I shall see him, but not now: I shall behold him, but not nigh: there shall come a Star out of Jacob, and a Sceptre shall rise out of Israel."},
    {"book": "Revelation", "chapter": 22, "verse": 16, "text": "I Jesus have sent mine angel to testify unto you these things in the churches. I am the root and the offspring of David, and the bright and morning star."},
    {"book": "2 Peter", "chapter": 1, "verse": 19, "text": "We have also a more sure word of prophecy; whereunto ye do well that ye take heed, as unto a light that shineth in a dark place, until the day dawn, and the day star arise in your hearts."},
    {"book": "Acts", "chapter": 2, "verse": 19, "text": "And I will shew wonders in heaven above, and signs in the earth beneath; blood, and fire, and vapour of smoke."},
    {"book": "Acts", "chapter": 2, "verse": 20, "text": "The sun shall be turned into darkness, and the moon into blood, before the great and notable day of the Lord come."},
    {"book": "Mark", "chapter": 13, "verse": 24, "text": "But in those days, after that tribulation, the sun shall be darkened, and the moon shall not give her light."},
    {"book": "Mark", "chapter": 13, "verse": 25, "text": "And the stars of heaven shall fall, and the powers that are in heaven shall be shaken."},
    {"book": "Ezekiel", "chapter": 32, "verse": 7, "text": "And when I shall put thee out, I will cover the heaven, and make the stars thereof dark; I will cover the sun with a cloud, and the moon shall not give her light."},
    {"book": "Ezekiel", "chapter": 32, "verse": 8, "text": "All the bright lights of heaven will I make dark over thee, and set darkness upon thy land, saith the Lord GOD."},
    {"book": "Genesis", "chapter": 1, "verse": 14, "text": "And God said, Let there be lights in the firmament of the heaven to divide the day from the night; and let them be for signs, and for seasons, and for days, and years."},
    {"book": "Genesis", "chapter": 37, "verse": 9, "text": "And he dreamed yet another dream, and told it his brethren, and said, Behold, I have dreamed a dream more; and, behold, the sun and the moon and the eleven stars made obeisance to me."},
    {"book": "Matthew", "chapter": 2, "verse": 2, "text": "Saying, Where is he that is born King of the Jews? for we have seen his star in the east, and are come to worship him."},
    {"book": "Daniel", "chapter": 12, "verse": 3, "text": "And they that be wise shall shine as the brightness of the firmament; and they that turn many to righteousness as the stars for ever and ever."},
]


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Data directory: {DATA_DIR}")


def create_local_bible_db():
    print("\nCreating local Bible database with cosmic prophecy verses...")

    conn = sqlite3.connect(BIBLE_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY,
            book_name TEXT UNIQUE NOT NULL,
            testament TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS verses (
            id INTEGER PRIMARY KEY,
            book_id INTEGER,
            chapter INTEGER,
            verse INTEGER,
            text TEXT,
            FOREIGN KEY (book_id) REFERENCES books(book_id),
            UNIQUE(book_id, chapter, verse)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS themes (
            id INTEGER PRIMARY KEY,
            verse_id INTEGER,
            theme TEXT,
            FOREIGN KEY (verse_id) REFERENCES verses(id)
        )
    """)

    books = {}
    testament_map = {
        "Genesis": "OT", "Exodus": "OT", "Leviticus": "OT", "Numbers": "OT", "Deuteronomy": "OT",
        "Job": "OT", "Psalms": "OT", "Proverbs": "OT", "Isaiah": "OT", "Jeremiah": "OT",
        "Ezekiel": "OT", "Daniel": "OT", "Hosea": "OT", "Joel": "OT", "Amos": "OT",
        "Obadiah": "OT", "Jonah": "OT", "Micah": "OT", "Nahum": "OT", "Habakkuk": "OT",
        "Zephaniah": "OT", "Haggai": "OT", "Zechariah": "OT", "Malachi": "OT",
        "Matthew": "NT", "Mark": "NT", "Luke": "NT", "John": "NT", "Acts": "NT",
        "Romans": "NT", "1 Corinthians": "NT", "2 Corinthians": "NT", "Galatians": "NT",
        "Ephesians": "NT", "Philippians": "NT", "Colossians": "NT", "1 Thessalonians": "NT",
        "2 Thessalonians": "NT", "1 Timothy": "NT", "2 Timothy": "NT", "Titus": "NT",
        "Philemon": "NT", "Hebrews": "NT", "James": "NT", "1 Peter": "NT", "2 Peter": "NT",
        "1 John": "NT", "2 John": "NT", "3 John": "NT", "Jude": "NT", "Revelation": "NT",
    }

    for verse in COSMIC_VERSES:
        book_name = verse["book"]
        if book_name not in books:
            testament = testament_map.get(book_name, "OT")
            cursor.execute(
                "INSERT OR IGNORE INTO books (book_name, testament) VALUES (?, ?)",
                (book_name, testament)
            )
            cursor.execute("SELECT book_id FROM books WHERE book_name = ?", (book_name,))
            books[book_name] = cursor.fetchone()[0]

    for verse in COSMIC_VERSES:
        book_id = books[verse["book"]]
        cursor.execute(
            "INSERT OR IGNORE INTO verses (book_id, chapter, verse, text) VALUES (?, ?, ?, ?)",
            (book_id, verse["chapter"], verse["verse"], verse["text"])
        )

        cursor.execute(
            "SELECT id FROM verses WHERE book_id = ? AND chapter = ? AND verse = ?",
            (book_id, verse["chapter"], verse["verse"])
        )
        verse_id = cursor.fetchone()[0]

        text_lower = verse["text"].lower()
        themes = []
        if any(kw in text_lower for kw in ["sun", "moon", "star", "heaven"]):
            themes.append("cosmic_signs")
        if any(kw in text_lower for kw in ["blood", "dark", "black"]):
            themes.append("judgment_signs")
        if any(kw in text_lower for kw in ["pleiades", "orion", "arcturus"]):
            themes.append("constellations")

        for theme in themes:
            cursor.execute(
                "INSERT INTO themes (verse_id, theme) VALUES (?, ?)",
                (verse_id, theme)
            )

    conn.commit()
    conn.close()

    print(f"Created database at {BIBLE_DB_PATH}")
    print(f"Inserted {len(COSMIC_VERSES)} cosmic prophecy verses")


def setup_chromadb():
    print("\nSetting up ChromaDB for semantic search...")

    try:
        import chromadb
        from chromadb.utils import embedding_functions
    except ImportError:
        print("ChromaDB not installed. Run: pip install chromadb sentence-transformers")
        return False

    CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))

    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-mpnet-base-v2"
    )

    collection = client.get_or_create_collection(
        name="cosmic_prophecies",
        embedding_function=sentence_transformer_ef,
        metadata={"description": "Biblical prophecy verses with cosmic/celestial themes"}
    )

    if collection.count() == 0:
        documents = []
        metadatas = []
        ids = []

        for i, verse in enumerate(COSMIC_VERSES):
            ref = f"{verse['book']} {verse['chapter']}:{verse['verse']}"
            documents.append(verse["text"])
            metadatas.append({
                "reference": ref,
                "book": verse["book"],
                "chapter": verse["chapter"],
                "verse": verse["verse"],
            })
            ids.append(f"verse_{i}")

        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        print(f"Indexed {len(documents)} verses in ChromaDB")
    else:
        print(f"ChromaDB already contains {collection.count()} verses")

    print("\nTesting semantic search...")
    results = collection.query(
        query_texts=["blood moon eclipse"],
        n_results=3
    )

    print("Query: 'blood moon eclipse'")
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        print(f"  - {meta['reference']}: {doc[:60]}...")

    return True


def download_full_bible():
    print("\nDownloading full Bible database...")
    print("This will download ~50MB of data.")

    response = input("Continue? [y/N] ")
    if response.lower() != "y":
        print("Skipped.")
        return False

    url = BIBLE_DATABASES["scrollmapper"]["url"]
    print(f"Downloading from {url}...")

    try:
        urllib.request.urlretrieve(url, BIBLE_DB_PATH)
        print(f"Downloaded to {BIBLE_DB_PATH}")
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        print("You can manually download from:")
        print("  https://github.com/scrollmapper/bible_databases")
        return False


def verify_setup():
    print("\n" + "=" * 50)
    print("Setup Verification")
    print("=" * 50)

    if BIBLE_DB_PATH.exists():
        conn = sqlite3.connect(BIBLE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM verses")
        count = cursor.fetchone()[0]
        conn.close()
        print(f"✓ Bible database: {count} verses")
    else:
        print("✗ Bible database not found")

    if CHROMA_DB_PATH.exists():
        try:
            import chromadb
            client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
            collection = client.get_collection("cosmic_prophecies")
            print(f"✓ ChromaDB: {collection.count()} indexed verses")
        except Exception:
            print("✗ ChromaDB collection not ready")
    else:
        print("✗ ChromaDB not set up")

    print("\nTo start using Prophecy Vision:")
    print("  python src/main.py --interactive")
    print("  python src/main.py --demo")


def main():
    print("=" * 50)
    print("  Prophecy Vision Database Setup")
    print("=" * 50)

    ensure_data_dir()

    create_local_bible_db()

    print("\nWould you like to set up ChromaDB for semantic search?")
    print("This requires: pip install chromadb sentence-transformers")
    response = input("Set up ChromaDB? [y/N] ")
    if response.lower() == "y":
        setup_chromadb()

    print("\nWould you like to download the full Bible database?")
    print("The local database only contains cosmic prophecy verses.")
    response = input("Download full Bible? [y/N] ")
    if response.lower() == "y":
        download_full_bible()

    verify_setup()


if __name__ == "__main__":
    main()
