#!/usr/bin/env python3
"""
Scripture MCP Server
Provides semantic search capabilities for Bible verses with focus on prophetic texts.
Uses ChromaDB with sentence-transformers for finding thematically related passages.

Categorization System:
- Layered approach: Scholarly sources → Category schema → AI analysis → Transparency
- Categories: PROPHETIC_SIGN, HISTORICAL_EVENT, CALENDAR_MARKER, METAPHORICAL,
              WORSHIP_PRAISE, CONDEMNED_PRACTICE, CREATION_ACCOUNT, UNCERTAIN
"""

import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Optional
from mcp.server.fastmcp import FastMCP

sys.path.insert(0, str(Path(__file__).parent.parent))
from database.categories import (
    CelestialCategory,
    CATEGORY_DESCRIPTIONS,
    CATEGORIZED_VERSES,
    get_verses_by_category,
    get_astronomically_relevant_verses,
    get_datable_verses,
    get_high_confidence_verses,
    format_verse_analysis,
)

mcp = FastMCP("scripture-prophecy")

DATA_DIR = Path(__file__).parent.parent.parent / "data"
BIBLE_DB_PATH = DATA_DIR / "bible.db"
CHROMA_DB_PATH = DATA_DIR / "chroma_db"

PROPHETIC_BOOKS = {
    "old_testament": [
        "Isaiah", "Jeremiah", "Ezekiel", "Daniel",
        "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah",
        "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi"
    ],
    "new_testament": ["Matthew", "Revelation"]
}

CELESTIAL_THEMES = {
    "cosmic_signs": [
        "sun", "moon", "star", "stars", "heaven", "heavens",
        "sky", "darkened", "blood", "eclipse", "light"
    ],
    "astronomical": [
        "constellation", "pleiades", "orion", "arcturus",
        "morning star", "day star", "wandering stars"
    ],
    "prophetic_imagery": [
        "sign", "wonder", "portent", "vision", "revelation",
        "beast", "dragon", "woman", "child", "angel"
    ]
}

COSMIC_VERSES = [
    {"ref": "Joel 2:31", "text": "The sun shall be turned into darkness, and the moon into blood, before the great and terrible day of the LORD come."},
    {"ref": "Matthew 24:29", "text": "Immediately after the tribulation of those days shall the sun be darkened, and the moon shall not give her light, and the stars shall fall from heaven, and the powers of the heavens shall be shaken."},
    {"ref": "Revelation 6:12-13", "text": "And I beheld when he had opened the sixth seal, and, lo, there was a great earthquake; and the sun became black as sackcloth of hair, and the moon became as blood; And the stars of heaven fell unto the earth."},
    {"ref": "Isaiah 13:10", "text": "For the stars of heaven and the constellations thereof shall not give their light: the sun shall be darkened in his going forth, and the moon shall not cause her light to shine."},
    {"ref": "Luke 21:25-26", "text": "And there shall be signs in the sun, and in the moon, and in the stars; and upon the earth distress of nations, with perplexity; the sea and the waves roaring; Men's hearts failing them for fear."},
    {"ref": "Revelation 12:1", "text": "And there appeared a great wonder in heaven; a woman clothed with the sun, and the moon under her feet, and upon her head a crown of twelve stars."},
    {"ref": "Amos 5:8", "text": "Seek him that maketh the seven stars and Orion, and turneth the shadow of death into the morning, and maketh the day dark with night."},
    {"ref": "Job 38:31-32", "text": "Canst thou bind the sweet influences of Pleiades, or loose the bands of Orion? Canst thou bring forth Mazzaroth in his season? or canst thou guide Arcturus with his sons?"},
    {"ref": "2 Peter 1:19", "text": "We have also a more sure word of prophecy; whereunto ye do well that ye take heed, as unto a light that shineth in a dark place, until the day dawn, and the day star arise in your hearts."},
    {"ref": "Revelation 22:16", "text": "I Jesus have sent mine angel to testify unto you these things in the churches. I am the root and the offspring of David, and the bright and morning star."},
    {"ref": "Numbers 24:17", "text": "I shall see him, but not now: I shall behold him, but not nigh: there shall come a Star out of Jacob, and a Sceptre shall rise out of Israel."},
    {"ref": "Ezekiel 32:7-8", "text": "And when I shall put thee out, I will cover the heaven, and make the stars thereof dark; I will cover the sun with a cloud, and the moon shall not give her light. All the bright lights of heaven will I make dark over thee."},
    {"ref": "Acts 2:19-20", "text": "And I will shew wonders in heaven above, and signs in the earth beneath; blood, and fire, and vapour of smoke: The sun shall be turned into darkness, and the moon into blood."},
    {"ref": "Mark 13:24-25", "text": "But in those days, after that tribulation, the sun shall be darkened, and the moon shall not give her light, And the stars of heaven shall fall, and the powers that are in heaven shall be shaken."},
    {"ref": "Genesis 1:14-16", "text": "And God said, Let there be lights in the firmament of the heaven to divide the day from the night; and let them be for signs, and for seasons, and for days, and years."},
]


def get_db_connection():
    if BIBLE_DB_PATH.exists():
        return sqlite3.connect(BIBLE_DB_PATH)
    return None


def get_chroma_client():
    try:
        import chromadb
        return chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
    except ImportError:
        return None


def get_embedding_function():
    try:
        from chromadb.utils import embedding_functions
        return embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-mpnet-base-v2"
        )
    except ImportError:
        return None


def simple_keyword_search(query: str, verses: list) -> list:
    query_terms = query.lower().split()
    results = []
    for verse in verses:
        text_lower = verse["text"].lower()
        ref_lower = verse["ref"].lower()
        score = sum(1 for term in query_terms if term in text_lower or term in ref_lower)
        if score > 0:
            results.append({**verse, "score": score})
    return sorted(results, key=lambda x: x["score"], reverse=True)


@mcp.tool()
async def search_cosmic_prophecies(query: str, max_results: int = 10) -> str:
    """
    Search for prophetic verses about cosmic/celestial events.
    Uses semantic similarity to find verses matching the query theme.

    query: Descriptive search (e.g., "sun turning dark", "stars falling", "blood moon")
    max_results: Maximum number of verses to return
    """
    chroma = get_chroma_client()
    if chroma:
        try:
            ef = get_embedding_function()
            collection = chroma.get_or_create_collection(
                name="cosmic_prophecies",
                embedding_function=ef
            )

            if collection.count() == 0:
                collection.add(
                    documents=[v["text"] for v in COSMIC_VERSES],
                    metadatas=[{"ref": v["ref"]} for v in COSMIC_VERSES],
                    ids=[f"cosmic_{i}" for i in range(len(COSMIC_VERSES))]
                )

            results = collection.query(
                query_texts=[query],
                n_results=min(max_results, len(COSMIC_VERSES))
            )

            formatted = []
            for i, (doc, meta, dist) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )):
                similarity = round(1 - dist, 3)
                formatted.append(f"{i+1}. {meta['ref']} (similarity: {similarity})\n   \"{doc}\"")

            return f"Semantic search results for '{query}':\n\n" + "\n\n".join(formatted)

        except Exception as e:
            pass

    results = simple_keyword_search(query, COSMIC_VERSES)[:max_results]
    formatted = []
    for i, verse in enumerate(results):
        formatted.append(f"{i+1}. {verse['ref']} (keyword score: {verse['score']})\n   \"{verse['text']}\"")

    if formatted:
        return f"Keyword search results for '{query}':\n\n" + "\n\n".join(formatted)
    return f"No verses found matching '{query}'"


@mcp.tool()
async def get_verse(book: str, chapter: int, verse: int, translation: str = "KJV") -> str:
    """
    Get a specific Bible verse by reference.

    book: Book name (e.g., "Genesis", "Revelation")
    chapter: Chapter number
    verse: Verse number
    translation: Bible translation (default KJV)
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.execute(
                """
                SELECT text FROM verses v
                JOIN books b ON v.book_id = b.book_id
                WHERE b.book_name = ? AND v.chapter = ? AND v.verse = ?
                """,
                (book, chapter, verse)
            )
            row = cursor.fetchone()
            conn.close()
            if row:
                return f"{book} {chapter}:{verse} ({translation})\n\"{row[0]}\""
        except Exception:
            pass

    for v in COSMIC_VERSES:
        if v["ref"].lower().startswith(f"{book.lower()} {chapter}:{verse}"):
            return f"{v['ref']} (KJV)\n\"{v['text']}\""

    return f"Verse not found: {book} {chapter}:{verse}"


@mcp.tool()
async def get_verse_range(book: str, chapter: int, start_verse: int, end_verse: int) -> str:
    """
    Get a range of Bible verses.

    book: Book name
    chapter: Chapter number
    start_verse: Starting verse number
    end_verse: Ending verse number
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.execute(
                """
                SELECT v.verse, v.text FROM verses v
                JOIN books b ON v.book_id = b.book_id
                WHERE b.book_name = ? AND v.chapter = ?
                AND v.verse BETWEEN ? AND ?
                ORDER BY v.verse
                """,
                (book, chapter, start_verse, end_verse)
            )
            rows = cursor.fetchall()
            conn.close()
            if rows:
                verses = [f"{verse}. {text}" for verse, text in rows]
                return f"{book} {chapter}:{start_verse}-{end_verse}\n" + "\n".join(verses)
        except Exception:
            pass

    return f"Verse range not found. Ensure database is set up at {BIBLE_DB_PATH}"


@mcp.tool()
async def find_cross_references(book: str, chapter: int, verse: int) -> str:
    """
    Find cross-references for a given verse.
    Cross-references connect related passages across the Bible.
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.execute(
                """
                SELECT DISTINCT
                    tb.book_name, cr.to_chapter, cr.to_verse_start, cr.to_verse_end
                FROM cross_references cr
                JOIN books fb ON cr.from_book = fb.book_id
                JOIN books tb ON cr.to_book = tb.book_id
                WHERE fb.book_name = ? AND cr.from_chapter = ? AND cr.from_verse = ?
                LIMIT 20
                """,
                (book, chapter, verse)
            )
            rows = cursor.fetchall()
            conn.close()
            if rows:
                refs = []
                for to_book, to_chapter, to_start, to_end in rows:
                    if to_start == to_end:
                        refs.append(f"- {to_book} {to_chapter}:{to_start}")
                    else:
                        refs.append(f"- {to_book} {to_chapter}:{to_start}-{to_end}")
                return f"Cross-references for {book} {chapter}:{verse}:\n" + "\n".join(refs)
        except Exception:
            pass

    hardcoded_refs = {
        "joel 2:31": ["Acts 2:20", "Revelation 6:12", "Matthew 24:29", "Mark 13:24"],
        "revelation 12:1": ["Genesis 37:9", "Isaiah 66:7", "Matthew 2:1-2"],
        "matthew 24:29": ["Joel 2:31", "Isaiah 13:10", "Ezekiel 32:7", "Mark 13:24-25"],
    }

    key = f"{book.lower()} {chapter}:{verse}"
    if key in hardcoded_refs:
        refs = [f"- {ref}" for ref in hardcoded_refs[key]]
        return f"Cross-references for {book} {chapter}:{verse}:\n" + "\n".join(refs)

    return f"No cross-references found for {book} {chapter}:{verse}"


@mcp.tool()
async def search_by_celestial_theme(theme: str) -> str:
    """
    Search verses by celestial/astronomical theme.
    Available themes: cosmic_signs, astronomical, prophetic_imagery
    Or specify a custom theme keyword.
    """
    if theme.lower() in CELESTIAL_THEMES:
        keywords = CELESTIAL_THEMES[theme.lower()]
        query = " ".join(keywords)
    else:
        query = theme

    return await search_cosmic_prophecies(query, max_results=15)


@mcp.tool()
async def analyze_prophetic_passage(reference: str) -> str:
    """
    Analyze a prophetic passage for astronomical references.
    Returns the verse text and identifies celestial imagery.

    reference: Verse reference (e.g., "Revelation 12:1-6" or "Joel 2:30-31")
    """
    parts = reference.replace(":", " ").replace("-", " ").split()
    if len(parts) < 3:
        return "Invalid reference format. Use: Book Chapter:Verse or Book Chapter:Start-End"

    book_words = []
    remaining = []
    for p in parts:
        if p.isdigit():
            remaining.append(p)
        else:
            book_words.append(p)

    book = " ".join(book_words)
    chapter = int(remaining[0]) if remaining else 1
    start_verse = int(remaining[1]) if len(remaining) > 1 else 1
    end_verse = int(remaining[2]) if len(remaining) > 2 else start_verse

    verse_text = await get_verse_range(book, chapter, start_verse, end_verse)

    all_keywords = []
    for theme_keywords in CELESTIAL_THEMES.values():
        all_keywords.extend(theme_keywords)

    text_lower = verse_text.lower()
    found_keywords = [kw for kw in all_keywords if kw in text_lower]

    astronomical_objects = []
    if any(kw in text_lower for kw in ["sun", "darkened"]):
        astronomical_objects.append("Solar event (eclipse or darkening)")
    if any(kw in text_lower for kw in ["moon", "blood"]):
        astronomical_objects.append("Lunar event (blood moon / eclipse)")
    if any(kw in text_lower for kw in ["star", "stars", "falling"]):
        astronomical_objects.append("Stellar event (meteor shower or constellation)")
    if any(kw in text_lower for kw in ["pleiades", "orion", "arcturus"]):
        astronomical_objects.append("Specific constellation reference")
    if "twelve stars" in text_lower or "crown" in text_lower:
        astronomical_objects.append("Zodiac constellation (possibly Leo/Virgo)")

    analysis = [
        f"=== Prophetic Passage Analysis ===",
        f"Reference: {reference}",
        "",
        verse_text,
        "",
        f"Celestial Keywords Found: {', '.join(found_keywords) if found_keywords else 'None'}",
        "",
        "Possible Astronomical Interpretations:",
    ]

    if astronomical_objects:
        for obj in astronomical_objects:
            analysis.append(f"  • {obj}")
    else:
        analysis.append("  • No specific astronomical references identified")

    analysis.extend([
        "",
        "To visualize in Stellarium:",
        "  1. Use set_biblical_location() for relevant location",
        "  2. Use find_possible_dates_for_prophecy() to identify candidate dates",
        "  3. Use set_time_gregorian() or set_time_julian() to set the date",
        "  4. Use focus_on_object() to center on relevant celestial object",
    ])

    return "\n".join(analysis)


@mcp.tool()
async def list_prophetic_books() -> str:
    """List all prophetic books in the Bible that often contain astronomical imagery."""
    return f"""
Prophetic Books with Astronomical Imagery:

Old Testament Prophets:
{chr(10).join(f'  • {book}' for book in PROPHETIC_BOOKS['old_testament'])}

New Testament Prophecy:
{chr(10).join(f'  • {book}' for book in PROPHETIC_BOOKS['new_testament'])}

Key themes to search:
  • cosmic_signs: sun, moon, stars, darkening, blood
  • astronomical: Pleiades, Orion, Arcturus, constellations
  • prophetic_imagery: signs, wonders, visions, beasts
"""


@mcp.tool()
async def get_all_cosmic_verses() -> str:
    """Get all pre-loaded verses about cosmic/celestial events."""
    formatted = []
    for i, verse in enumerate(COSMIC_VERSES, 1):
        formatted.append(f"{i}. {verse['ref']}\n   \"{verse['text']}\"")
    return "All Cosmic Prophecy Verses:\n\n" + "\n\n".join(formatted)


@mcp.tool()
async def setup_database() -> str:
    """
    Provide instructions for setting up the full Bible database.
    This enables comprehensive verse search beyond the pre-loaded cosmic verses.
    """
    return f"""
=== Bible Database Setup Instructions ===

The scripture server can work in two modes:
1. Lightweight mode: Uses pre-loaded cosmic prophecy verses (current)
2. Full mode: Complete Bible database with semantic search

To enable full mode:

Step 1: Download SQLite Bible Database
  git clone https://github.com/scrollmapper/bible_databases.git
  cp bible_databases/bible-sqlite.db {BIBLE_DB_PATH}

Step 2: Install ChromaDB for semantic search
  pip install chromadb sentence-transformers

Step 3: Index verses for semantic search
  python -c "from scripture_server import index_full_bible; index_full_bible()"

Step 4: (Optional) Download Kaggle semantic similarity dataset
  pip install kaggle
  kaggle datasets download nileedixon/paired-bible-verses-for-semantic-similarity
  unzip paired-bible-verses-for-semantic-similarity.zip -d {DATA_DIR}/kaggle

Current status:
  - Bible DB exists: {BIBLE_DB_PATH.exists()}
  - ChromaDB path: {CHROMA_DB_PATH}
  - Pre-loaded verses: {len(COSMIC_VERSES)} cosmic prophecy verses
"""


@mcp.tool()
async def list_categories() -> str:
    """
    List all verse categories used to classify celestial passages.
    Shows which categories are astronomically relevant and can be dated.
    """
    lines = ["=== Verse Categories ===\n"]
    for cat, info in CATEGORY_DESCRIPTIONS.items():
        lines.append(f"**{info['name']}** ({cat.value})")
        lines.append(f"  {info['description']}")
        lines.append(f"  Astronomically Relevant: {info['astronomically_relevant']}")
        lines.append(f"  Can Be Dated: {info['can_be_dated']}")
        lines.append(f"  Examples: {', '.join(info['examples'])}")
        lines.append("")
    return "\n".join(lines)


@mcp.tool()
async def get_verses_by_category_tool(category: str) -> str:
    """
    Get all verses in a specific category.

    category: One of: prophetic_sign, historical_event, calendar_marker,
              metaphorical, worship_praise, condemned_practice,
              creation_account, uncertain
    """
    try:
        cat = CelestialCategory(category.lower())
    except ValueError:
        available = [c.value for c in CelestialCategory]
        return f"Invalid category. Available: {', '.join(available)}"

    verses = get_verses_by_category(cat)
    if not verses:
        return f"No verses found in category: {category}"

    cat_info = CATEGORY_DESCRIPTIONS[cat]
    lines = [
        f"=== {cat_info['name']} ===",
        f"{cat_info['description']}",
        f"Astronomically Relevant: {cat_info['astronomically_relevant']}",
        f"\nVerses ({len(verses)}):\n"
    ]

    for v in verses:
        lines.append(f"• {v.reference} (confidence: {v.confidence*100:.0f}%)")
        lines.append(f"  \"{v.text[:100]}...\"" if len(v.text) > 100 else f"  \"{v.text}\"")
        lines.append("")

    return "\n".join(lines)


@mcp.tool()
async def get_datable_prophecies() -> str:
    """
    Get all verses that can potentially be dated and visualized in Stellarium.
    These are astronomically relevant prophecies with candidate dates.
    """
    verses = get_datable_verses()

    lines = [
        "=== Datable Prophetic Verses ===",
        "These verses describe celestial events that may correspond to",
        "specific astronomical phenomena viewable in Stellarium.\n"
    ]

    for v in verses:
        cat_name = CATEGORY_DESCRIPTIONS[v.category]['name']
        lines.append(f"**{v.reference}** [{cat_name}]")
        lines.append(f"  Confidence: {v.confidence*100:.0f}%")
        lines.append(f"  Objects: {', '.join(v.celestial_objects)}")
        lines.append(f"  Candidate Dates:")
        for date in v.astronomical_date_candidates:
            lines.append(f"    - {date}")
        lines.append("")

    return "\n".join(lines)


@mcp.tool()
async def analyze_verse_detailed(reference: str) -> str:
    """
    Get detailed scholarly analysis of a categorized verse.
    Shows category, reasoning, cross-references, Hebrew/Greek notes,
    alternative interpretations, and candidate dates for Stellarium.

    reference: Verse reference (e.g., "Joel 2:31", "Revelation 12:1-2")
    """
    ref_lower = reference.lower().strip()

    for verse in CATEGORIZED_VERSES:
        if verse.reference.lower() == ref_lower or ref_lower in verse.reference.lower():
            return format_verse_analysis(verse)

    available = [v.reference for v in CATEGORIZED_VERSES]
    return f"Verse not in categorized database.\n\nAvailable verses:\n" + "\n".join(f"  - {r}" for r in available)


@mcp.tool()
async def get_astronomically_relevant() -> str:
    """
    Get all verses that are astronomically relevant (not metaphorical or condemned).
    These are suitable for Stellarium visualization attempts.
    """
    verses = get_astronomically_relevant_verses()

    lines = [
        "=== Astronomically Relevant Verses ===",
        "These verses describe celestial phenomena that may be literal",
        "astronomical events (not purely metaphorical or condemned practices).\n"
    ]

    by_category = {}
    for v in verses:
        cat_name = CATEGORY_DESCRIPTIONS[v.category]['name']
        if cat_name not in by_category:
            by_category[cat_name] = []
        by_category[cat_name].append(v)

    for cat_name, cat_verses in by_category.items():
        lines.append(f"\n**{cat_name}** ({len(cat_verses)} verses):")
        for v in cat_verses:
            lines.append(f"  • {v.reference}")
            lines.append(f"    Objects: {', '.join(v.celestial_objects)}")

    return "\n".join(lines)


@mcp.tool()
async def get_condemned_practices() -> str:
    """
    Get verses that warn against astrology and star worship.
    Important for understanding the biblical distinction between
    astronomy (observing God's signs) and astrology (divination).
    """
    verses = get_verses_by_category(CelestialCategory.CONDEMNED_PRACTICE)

    lines = [
        "=== Biblical Warnings Against Astrology ===",
        "These verses distinguish forbidden practices (divination, star worship)",
        "from legitimate observation of celestial signs (Genesis 1:14).\n"
    ]

    for v in verses:
        lines.append(f"**{v.reference}**")
        lines.append(f"  \"{v.text}\"")
        lines.append(f"  Context: {v.book_context}")
        if v.hebrew_greek_notes:
            lines.append(f"  Language Notes: {v.hebrew_greek_notes}")
        lines.append("")

    lines.append("KEY DISTINCTION:")
    lines.append("  ✓ Permitted: Observing celestial signs for times/seasons (Gen 1:14)")
    lines.append("  ✓ Permitted: Recognizing prophetic celestial events (Joel 2:31)")
    lines.append("  ✗ Forbidden: Worshipping celestial bodies (Deut 4:19)")
    lines.append("  ✗ Forbidden: Divination/fortune-telling by stars (Isa 47:13)")

    return "\n".join(lines)


@mcp.tool()
async def search_by_confidence(min_confidence: float = 0.8) -> str:
    """
    Get verses with high categorization confidence.
    Higher confidence means less scholarly debate about interpretation.

    min_confidence: Minimum confidence threshold (0.0 to 1.0, default 0.8)
    """
    verses = get_high_confidence_verses(min_confidence)

    lines = [
        f"=== High Confidence Verses (≥{min_confidence*100:.0f}%) ===",
        "These categorizations have strong scholarly consensus.\n"
    ]

    for v in sorted(verses, key=lambda x: x.confidence, reverse=True):
        cat_name = CATEGORY_DESCRIPTIONS[v.category]['name']
        lines.append(f"• {v.reference} ({v.confidence*100:.0f}%) - {cat_name}")

    return "\n".join(lines)


@mcp.tool()
async def get_uncertain_verses() -> str:
    """
    Get verses where interpretation is debated among scholars.
    Shows alternative interpretations and confidence levels.
    """
    uncertain = get_verses_by_category(CelestialCategory.UNCERTAIN)
    debated = [v for v in CATEGORIZED_VERSES if v.alternative_categories]

    all_debated = list(set(uncertain + debated))

    lines = [
        "=== Debated/Uncertain Passages ===",
        "These verses have multiple valid scholarly interpretations.\n"
    ]

    for v in all_debated:
        cat_name = CATEGORY_DESCRIPTIONS[v.category]['name']
        lines.append(f"**{v.reference}**")
        lines.append(f"  Primary: {cat_name} ({v.confidence*100:.0f}%)")
        if v.alternative_categories:
            lines.append("  Alternatives:")
            for alt_cat, conf, reason in v.alternative_categories:
                alt_name = CATEGORY_DESCRIPTIONS[alt_cat]['name']
                lines.append(f"    - {alt_name} ({conf*100:.0f}%): {reason}")
        lines.append(f"  Reasoning: {v.reasoning[:150]}...")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
