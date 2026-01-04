import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_servers.scripture_server import (
    COSMIC_VERSES,
    PROPHETIC_BOOKS,
    CELESTIAL_THEMES,
    simple_keyword_search,
)


class TestCosmicVersesData:
    def test_cosmic_verses_not_empty(self):
        assert len(COSMIC_VERSES) > 0

    def test_cosmic_verses_have_required_fields(self):
        required_fields = {"ref", "text"}
        for verse in COSMIC_VERSES:
            for field in required_fields:
                assert field in verse, f"Verse missing {field}"

    def test_joel_blood_moon_verse_exists(self):
        joel_verses = [v for v in COSMIC_VERSES if "Joel" in v["ref"]]
        assert len(joel_verses) > 0

        blood_moon = [v for v in joel_verses if "blood" in v["text"].lower()]
        assert len(blood_moon) > 0

    def test_revelation_12_verse_exists(self):
        rev12 = [v for v in COSMIC_VERSES if "Revelation 12" in v["ref"]]
        assert len(rev12) > 0

        woman_sun = [v for v in rev12 if "sun" in v["text"].lower()]
        assert len(woman_sun) > 0


class TestPropheticBooks:
    def test_old_testament_prophets_exist(self):
        ot_prophets = PROPHETIC_BOOKS["old_testament"]
        assert "Isaiah" in ot_prophets
        assert "Daniel" in ot_prophets
        assert "Joel" in ot_prophets
        assert "Ezekiel" in ot_prophets

    def test_new_testament_prophecy_books(self):
        nt_books = PROPHETIC_BOOKS["new_testament"]
        assert "Revelation" in nt_books
        assert "Matthew" in nt_books


class TestCelestialThemes:
    def test_cosmic_signs_keywords(self):
        keywords = CELESTIAL_THEMES["cosmic_signs"]
        assert "sun" in keywords
        assert "moon" in keywords
        assert "star" in keywords or "stars" in keywords

    def test_astronomical_keywords(self):
        keywords = CELESTIAL_THEMES["astronomical"]
        assert "pleiades" in keywords
        assert "orion" in keywords

    def test_all_themes_have_keywords(self):
        for theme, keywords in CELESTIAL_THEMES.items():
            assert len(keywords) > 0, f"Theme {theme} has no keywords"


class TestSimpleKeywordSearch:
    def test_search_blood_moon(self):
        results = simple_keyword_search("blood moon", COSMIC_VERSES)
        assert len(results) > 0

        refs = [r["ref"] for r in results]
        assert any("Joel" in ref for ref in refs)

    def test_search_sun_darkened(self):
        results = simple_keyword_search("sun darkened", COSMIC_VERSES)
        assert len(results) > 0

    def test_search_stars(self):
        results = simple_keyword_search("stars", COSMIC_VERSES)
        assert len(results) > 0

    def test_search_returns_scores(self):
        results = simple_keyword_search("moon", COSMIC_VERSES)
        for result in results:
            assert "score" in result
            assert result["score"] > 0

    def test_search_results_sorted_by_score(self):
        results = simple_keyword_search("sun moon stars", COSMIC_VERSES)
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i]["score"] >= results[i + 1]["score"]

    def test_empty_search_returns_empty(self):
        results = simple_keyword_search("xyz123nonexistent", COSMIC_VERSES)
        assert len(results) == 0

    def test_search_pleiades_orion(self):
        results = simple_keyword_search("pleiades orion", COSMIC_VERSES)
        assert len(results) > 0

        refs = [r["ref"].lower() for r in results]
        assert any("job" in ref or "amos" in ref for ref in refs)


class TestVerseContent:
    def test_verses_mention_celestial_objects(self):
        celestial_objects = {
            "sun", "moon", "star", "stars", "heaven", "heavens",
            "pleiades", "orion", "arcturus", "mazzaroth", "constellation"
        }

        for verse in COSMIC_VERSES:
            text_lower = verse["text"].lower()
            has_celestial = any(obj in text_lower for obj in celestial_objects)
            assert has_celestial, f"Verse {verse['ref']} has no celestial reference"

    def test_verse_references_format(self):
        for verse in COSMIC_VERSES:
            ref = verse["ref"]
            assert " " in ref, f"Reference {ref} missing space"

            parts = ref.split()
            assert len(parts) >= 2, f"Reference {ref} incomplete"

            last_part = parts[-1]
            assert ":" in last_part, f"Reference {ref} missing chapter:verse format"
