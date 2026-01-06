#!/usr/bin/env python3
"""
Verse Categorization System
Classifies biblical passages related to celestial phenomena using a layered approach:
1. Scholarly baseline (cross-references, commentaries)
2. Category schema (prophetic, historical, metaphorical, etc.)
3. AI context analysis
4. Transparency with reasoning
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class CelestialCategory(Enum):
    PROPHETIC_SIGN = "prophetic_sign"
    HISTORICAL_EVENT = "historical_event"
    CALENDAR_MARKER = "calendar_marker"
    METAPHORICAL = "metaphorical"
    WORSHIP_PRAISE = "worship_praise"
    CONDEMNED_PRACTICE = "condemned_practice"
    CREATION_ACCOUNT = "creation_account"
    UNCERTAIN = "uncertain"


CATEGORY_DESCRIPTIONS = {
    CelestialCategory.PROPHETIC_SIGN: {
        "name": "Prophetic Sign",
        "description": "Future celestial event described as a sign of divine action or end times",
        "astronomically_relevant": True,
        "examples": ["Blood moons", "Sun darkening", "Stars falling"],
        "can_be_dated": True,
    },
    CelestialCategory.HISTORICAL_EVENT: {
        "name": "Historical Astronomical Event",
        "description": "Past celestial occurrence marking a significant biblical event",
        "astronomically_relevant": True,
        "examples": ["Star of Bethlehem", "Joshua's long day", "Hezekiah's sundial"],
        "can_be_dated": True,
    },
    CelestialCategory.CALENDAR_MARKER: {
        "name": "Calendar/Seasonal Marker",
        "description": "Celestial bodies used for timekeeping, festivals, or agricultural seasons",
        "astronomically_relevant": True,
        "examples": ["New moon festivals", "Sabbath years", "Jubilee calculations"],
        "can_be_dated": False,
    },
    CelestialCategory.METAPHORICAL: {
        "name": "Metaphorical/Symbolic",
        "description": "Celestial imagery used symbolically, not describing literal astronomical events",
        "astronomically_relevant": False,
        "examples": ["Joseph's dream", "Jesus as morning star", "Saints shining like stars"],
        "can_be_dated": False,
    },
    CelestialCategory.WORSHIP_PRAISE: {
        "name": "Worship/Praise",
        "description": "Poetic references to celestial bodies glorifying God as Creator",
        "astronomically_relevant": False,
        "examples": ["Heavens declare glory", "Stars praise Him", "Moon and sun worship"],
        "can_be_dated": False,
    },
    CelestialCategory.CONDEMNED_PRACTICE: {
        "name": "Condemned Practice",
        "description": "Warnings against astrology, star worship, or divination by celestial signs",
        "astronomically_relevant": False,
        "examples": ["Host of heaven worship", "Astrologers condemned", "Mazzaroth warnings"],
        "can_be_dated": False,
    },
    CelestialCategory.CREATION_ACCOUNT: {
        "name": "Creation Account",
        "description": "Description of celestial bodies being created and their intended purposes",
        "astronomically_relevant": True,
        "examples": ["Sun and moon created", "Stars set in firmament"],
        "can_be_dated": False,
    },
    CelestialCategory.UNCERTAIN: {
        "name": "Uncertain/Debated",
        "description": "Passages where scholars disagree on literal vs symbolic interpretation",
        "astronomically_relevant": None,
        "examples": ["Revelation imagery", "Daniel's visions"],
        "can_be_dated": None,
    },
}


@dataclass
class ScholarlySource:
    name: str
    type: str
    reference: str
    notes: Optional[str] = None


@dataclass
class CategorizedVerse:
    reference: str
    text: str
    category: CelestialCategory
    confidence: float
    reasoning: str
    celestial_objects: list = field(default_factory=list)
    cross_references: list = field(default_factory=list)
    scholarly_sources: list = field(default_factory=list)
    alternative_categories: list = field(default_factory=list)
    astronomical_date_candidates: list = field(default_factory=list)
    hebrew_greek_notes: Optional[str] = None
    genre: Optional[str] = None
    book_context: Optional[str] = None


CATEGORIZED_VERSES = [
    CategorizedVerse(
        reference="Joel 2:31",
        text="The sun shall be turned into darkness, and the moon into blood, before the great and terrible day of the LORD come.",
        category=CelestialCategory.PROPHETIC_SIGN,
        confidence=0.95,
        reasoning="Apocalyptic prophecy describing future celestial signs preceding the Day of the Lord. Genre is prophetic oracle. Language is predictive ('shall be'). Quoted by Peter in Acts 2:20 as prophecy being fulfilled.",
        celestial_objects=["sun", "moon"],
        cross_references=["Acts 2:20", "Matthew 24:29", "Revelation 6:12", "Isaiah 13:10"],
        scholarly_sources=[
            ScholarlySource("Treasury of Scripture Knowledge", "cross-reference", "Joel 2:31"),
            ScholarlySource("Strong's H1818", "lexicon", "dam (blood) - literal blood color"),
            ScholarlySource("Strong's H2822", "lexicon", "choshek (darkness) - literal darkness"),
        ],
        astronomical_date_candidates=["Lunar eclipses (blood moon)", "Solar eclipses"],
        hebrew_greek_notes="Hebrew 'dam' (blood) suggests red coloration; 'choshek' (darkness) is same word used for plague of darkness in Exodus",
        genre="Prophetic Oracle",
        book_context="Joel prophesying about Day of the Lord judgments and restoration",
    ),
    CategorizedVerse(
        reference="Matthew 24:29",
        text="Immediately after the tribulation of those days shall the sun be darkened, and the moon shall not give her light, and the stars shall fall from heaven, and the powers of the heavens shall be shaken.",
        category=CelestialCategory.PROPHETIC_SIGN,
        confidence=0.95,
        reasoning="Jesus's Olivet Discourse describing end-times signs. Direct prophetic statement about future celestial events. Echoes Joel 2:31 and Isaiah 13:10. Context is answering disciples' question about signs of His coming.",
        celestial_objects=["sun", "moon", "stars", "heavens"],
        cross_references=["Joel 2:31", "Isaiah 13:10", "Mark 13:24-25", "Luke 21:25-26", "Revelation 6:12-13"],
        scholarly_sources=[
            ScholarlySource("Treasury of Scripture Knowledge", "cross-reference", "Matt 24:29"),
            ScholarlySource("Strong's G4655", "lexicon", "skotizo (darkened) - literal darkening"),
        ],
        astronomical_date_candidates=["Future fulfillment", "70 AD (partial/typological)"],
        genre="Prophetic Discourse",
        book_context="Olivet Discourse - Jesus answering questions about end times",
    ),
    CategorizedVerse(
        reference="Revelation 12:1-2",
        text="And there appeared a great wonder in heaven; a woman clothed with the sun, and the moon under her feet, and upon her head a crown of twelve stars: And she being with child cried, travailing in birth, and pained to be delivered.",
        category=CelestialCategory.UNCERTAIN,
        confidence=0.60,
        reasoning="Apocalyptic vision with celestial imagery. Scholars debate: (1) Purely symbolic - woman represents Israel/Church, (2) Astronomical sign - Virgo constellation alignment, (3) Both literal and symbolic. Genre is apocalyptic vision which frequently uses symbolic imagery.",
        celestial_objects=["sun", "moon", "stars (twelve)"],
        cross_references=["Genesis 37:9", "Isaiah 66:7", "Micah 5:3"],
        scholarly_sources=[
            ScholarlySource("Treasury of Scripture Knowledge", "cross-reference", "Rev 12:1"),
            ScholarlySource("Strong's G4592", "lexicon", "semeion (wonder/sign) - can be literal or symbolic"),
        ],
        alternative_categories=[
            (CelestialCategory.PROPHETIC_SIGN, 0.40, "If interpreted as literal astronomical alignment"),
            (CelestialCategory.METAPHORICAL, 0.50, "If interpreted as symbolic of Israel/Mary/Church"),
        ],
        astronomical_date_candidates=["September 23, 2017 (Virgo alignment)", "3 BC (at Christ's birth)", "Future fulfillment"],
        hebrew_greek_notes="Greek 'semeion mega' (great sign) - same word used for miraculous signs",
        genre="Apocalyptic Vision",
        book_context="John's vision on Patmos - highly symbolic apocalyptic literature",
    ),
    CategorizedVerse(
        reference="Genesis 1:14-16",
        text="And God said, Let there be lights in the firmament of the heaven to divide the day from the night; and let them be for signs, and for seasons, and for days, and years: And let them be for lights in the firmament of the heaven to give light upon the earth: and it was so. And God made two great lights; the greater light to rule the day, and the lesser light to rule the night: he made the stars also.",
        category=CelestialCategory.CREATION_ACCOUNT,
        confidence=0.98,
        reasoning="Creation narrative establishing purpose of celestial bodies. Key word 'signs' (Hebrew 'owth') indicates celestial bodies have legitimate sign function ordained by God. This is foundational text for understanding biblical astronomy.",
        celestial_objects=["sun", "moon", "stars"],
        cross_references=["Psalm 104:19", "Jeremiah 31:35", "Psalm 136:7-9"],
        scholarly_sources=[
            ScholarlySource("Strong's H226", "lexicon", "owth (signs) - signal, distinguishing mark, miraculous sign"),
            ScholarlySource("Strong's H4150", "lexicon", "moed (seasons) - appointed times, festivals"),
        ],
        hebrew_greek_notes="'Owth' (signs) is same word used for rainbow sign, circumcision sign, Sabbath sign. 'Moed' (seasons) means appointed times/festivals, not just weather seasons.",
        genre="Creation Narrative",
        book_context="Genesis creation account - foundational cosmology",
    ),
    CategorizedVerse(
        reference="Matthew 2:2",
        text="Saying, Where is he that is born King of the Jews? for we have seen his star in the east, and are come to worship him.",
        category=CelestialCategory.HISTORICAL_EVENT,
        confidence=0.90,
        reasoning="Historical narrative of Magi observing astronomical phenomenon. Gospel presents this as actual historical event, not symbolic. Star guided them to specific location. Multiple astronomical theories exist for identification.",
        celestial_objects=["star (his star)"],
        cross_references=["Numbers 24:17", "Isaiah 60:3", "Matthew 2:7-10"],
        scholarly_sources=[
            ScholarlySource("Strong's G792", "lexicon", "aster (star) - literal star or celestial object"),
            ScholarlySource("Nave's Topical Bible", "topical", "Star of Bethlehem"),
        ],
        alternative_categories=[
            (CelestialCategory.PROPHETIC_SIGN, 0.30, "If fulfilling Numbers 24:17 prophecy"),
        ],
        astronomical_date_candidates=[
            "7 BC - Jupiter-Saturn conjunction",
            "6 BC - Chinese/Korean nova records",
            "3-2 BC - Jupiter-Regulus conjunctions",
            "2 BC - Jupiter-Venus conjunction (June 17)",
        ],
        hebrew_greek_notes="Greek 'aster' is generic term for any celestial light source - star, planet, comet, or nova",
        genre="Historical Narrative",
        book_context="Matthew's nativity account - historical gospel narrative",
    ),
    CategorizedVerse(
        reference="Genesis 37:9",
        text="And he dreamed yet another dream, and told it his brethren, and said, Behold, I have dreamed a dream more; and, behold, the sun and the moon and the eleven stars made obeisance to me.",
        category=CelestialCategory.METAPHORICAL,
        confidence=0.95,
        reasoning="Joseph's dream using celestial imagery symbolically. Context makes clear: sun=Jacob, moon=Rachel/Leah, stars=brothers. Not describing astronomical event but family relationships. Father Jacob interprets it this way in v.10.",
        celestial_objects=["sun", "moon", "stars (eleven)"],
        cross_references=["Revelation 12:1", "Genesis 37:10"],
        scholarly_sources=[
            ScholarlySource("Treasury of Scripture Knowledge", "cross-reference", "Gen 37:9"),
        ],
        hebrew_greek_notes="Same celestial vocabulary but clearly symbolic in context",
        genre="Narrative (Dream Account)",
        book_context="Joseph narrative - dreams that foreshadow his rise to power",
    ),
    CategorizedVerse(
        reference="Deuteronomy 4:19",
        text="And lest thou lift up thine eyes unto heaven, and when thou seest the sun, and the moon, and the stars, even all the host of heaven, shouldest be driven to worship them, and serve them, which the LORD thy God hath divided unto all nations under the whole heaven.",
        category=CelestialCategory.CONDEMNED_PRACTICE,
        confidence=0.98,
        reasoning="Direct prohibition against worshipping celestial bodies. Part of Mosaic law. Distinguishes between observing celestial signs (permitted, Gen 1:14) and worshipping them (forbidden). Important boundary for biblical astronomy.",
        celestial_objects=["sun", "moon", "stars", "host of heaven"],
        cross_references=["Deuteronomy 17:3", "2 Kings 21:3", "Jeremiah 8:2", "Acts 7:42"],
        scholarly_sources=[
            ScholarlySource("Strong's H6635", "lexicon", "tsaba (host) - army, used for stars as heavenly army"),
        ],
        hebrew_greek_notes="'Tsaba hashamayim' (host of heaven) becomes technical term for astral worship throughout OT",
        genre="Legal/Covenant",
        book_context="Deuteronomic law - Moses's final instructions before entering Promised Land",
    ),
    CategorizedVerse(
        reference="Isaiah 47:13",
        text="Thou art wearied in the multitude of thy counsels. Let now the astrologers, the stargazers, the monthly prognosticators, stand up, and save thee from these things that shall come upon thee.",
        category=CelestialCategory.CONDEMNED_PRACTICE,
        confidence=0.98,
        reasoning="Prophetic mockery of Babylonian astrologers. Context is judgment on Babylon. Sarcastically challenges astrologers to save Babylon - they cannot. Condemns divination/fortune-telling by stars, not astronomical observation.",
        celestial_objects=["stars (for divination)"],
        cross_references=["Daniel 2:27", "Isaiah 44:25", "Jeremiah 10:2"],
        scholarly_sources=[
            ScholarlySource("Strong's H1895", "lexicon", "habar (astrologers) - divide heavens for omens"),
            ScholarlySource("Strong's H2374", "lexicon", "chozeh (stargazers) - seers of stars"),
        ],
        hebrew_greek_notes="Hebrew terms describe divination practices: dividing sky into sections, making monthly predictions based on star positions",
        genre="Prophetic Oracle (Judgment)",
        book_context="Isaiah's oracle against Babylon",
    ),
    CategorizedVerse(
        reference="Job 38:31-32",
        text="Canst thou bind the sweet influences of Pleiades, or loose the bands of Orion? Canst thou bring forth Mazzaroth in his season? or canst thou guide Arcturus with his sons?",
        category=CelestialCategory.WORSHIP_PRAISE,
        confidence=0.85,
        reasoning="God questioning Job about celestial objects to demonstrate divine sovereignty. Not prophetic but demonstrates God's authority over constellations. Names specific star groups showing ancient Hebrew astronomical knowledge.",
        celestial_objects=["Pleiades", "Orion", "Mazzaroth (zodiac/constellations)", "Arcturus (Bear)"],
        cross_references=["Job 9:9", "Amos 5:8", "Isaiah 40:26"],
        scholarly_sources=[
            ScholarlySource("Strong's H3598", "lexicon", "Kimah (Pleiades) - cluster, heap"),
            ScholarlySource("Strong's H3685", "lexicon", "Kesil (Orion) - fool, hunter constellation"),
            ScholarlySource("Strong's H4216", "lexicon", "Mazzaroth - possibly zodiac constellations"),
            ScholarlySource("Strong's H5906", "lexicon", "Ayish/Ash (Arcturus) - Great Bear/Ursa Major"),
        ],
        alternative_categories=[
            (CelestialCategory.CALENDAR_MARKER, 0.30, "If Mazzaroth refers to seasonal constellations"),
        ],
        hebrew_greek_notes="Mazzaroth is debated - possibly zodiac signs, possibly specific constellation. Some link to 'mazzaloth' in 2 Kings 23:5 (astrology context).",
        genre="Wisdom Literature (Divine Speech)",
        book_context="God's response to Job from the whirlwind",
    ),
    CategorizedVerse(
        reference="Psalm 19:1-4",
        text="The heavens declare the glory of God; and the firmament sheweth his handywork. Day unto day uttereth speech, and night unto night sheweth knowledge. There is no speech nor language, where their voice is not heard. Their line is gone out through all the earth, and their words to the end of the world.",
        category=CelestialCategory.WORSHIP_PRAISE,
        confidence=0.95,
        reasoning="Poetic praise describing celestial bodies as testimony to God's glory. Not predicting events but celebrating creation. Paul quotes v.4 in Romans 10:18. Genre is worship poetry (hymn).",
        celestial_objects=["heavens", "firmament"],
        cross_references=["Romans 10:18", "Psalm 8:3", "Psalm 97:6"],
        scholarly_sources=[
            ScholarlySource("Treasury of Scripture Knowledge", "cross-reference", "Psalm 19:1"),
        ],
        genre="Wisdom Poetry (Hymn)",
        book_context="Davidic psalm praising God through creation and Torah",
    ),
    CategorizedVerse(
        reference="Revelation 6:12-13",
        text="And I beheld when he had opened the sixth seal, and, lo, there was a great earthquake; and the sun became black as sackcloth of hair, and the moon became as blood; And the stars of heaven fell unto the earth, even as a fig tree casteth her untimely figs, when she is shaken of a mighty wind.",
        category=CelestialCategory.PROPHETIC_SIGN,
        confidence=0.85,
        reasoning="Apocalyptic vision of sixth seal judgment. Echoes Joel 2:31 language. Describes cosmic disturbances as divine judgment signs. Debate exists on literal vs symbolic interpretation, but presented as future events.",
        celestial_objects=["sun", "moon", "stars"],
        cross_references=["Joel 2:31", "Isaiah 13:10", "Matthew 24:29", "Acts 2:20"],
        scholarly_sources=[
            ScholarlySource("Treasury of Scripture Knowledge", "cross-reference", "Rev 6:12"),
        ],
        alternative_categories=[
            (CelestialCategory.METAPHORICAL, 0.35, "If apocalyptic imagery is purely symbolic"),
        ],
        astronomical_date_candidates=["Future fulfillment", "Symbolic of judgment (non-datable)"],
        genre="Apocalyptic Vision",
        book_context="Seven seals judgments in Revelation",
    ),
    CategorizedVerse(
        reference="Acts 2:19-20",
        text="And I will shew wonders in heaven above, and signs in the earth beneath; blood, and fire, and vapour of smoke: The sun shall be turned into darkness, and the moon into blood, before the great and notable day of the Lord come.",
        category=CelestialCategory.PROPHETIC_SIGN,
        confidence=0.95,
        reasoning="Peter quoting Joel 2:30-31 at Pentecost, declaring prophetic fulfillment beginning. Apostolic interpretation confirms Joel's prophecy as describing actual celestial signs. 'Last days' framework indicates ongoing relevance.",
        celestial_objects=["sun", "moon", "heavens"],
        cross_references=["Joel 2:30-31", "Matthew 24:29", "Revelation 6:12"],
        scholarly_sources=[
            ScholarlySource("Treasury of Scripture Knowledge", "cross-reference", "Acts 2:19"),
        ],
        astronomical_date_candidates=["Ongoing 'last days' period", "Specific future fulfillment"],
        genre="Apostolic Sermon",
        book_context="Peter's Pentecost sermon - interpreting Joel's prophecy",
    ),
    CategorizedVerse(
        reference="Luke 21:25-26",
        text="And there shall be signs in the sun, and in the moon, and in the stars; and upon the earth distress of nations, with perplexity; the sea and the waves roaring; Men's hearts failing them for fear, and for looking after those things which are coming on the earth: for the powers of heaven shall be shaken.",
        category=CelestialCategory.PROPHETIC_SIGN,
        confidence=0.95,
        reasoning="Luke's parallel to Olivet Discourse. Jesus explicitly says 'signs in sun, moon, stars' - using same 'semeion' (sign) vocabulary as Genesis 1:14. Predicts observable celestial phenomena causing fear.",
        celestial_objects=["sun", "moon", "stars", "powers of heaven"],
        cross_references=["Matthew 24:29", "Mark 13:24-25", "Joel 2:31"],
        scholarly_sources=[
            ScholarlySource("Strong's G4592", "lexicon", "semeion (signs) - same as Gen 1:14 LXX"),
        ],
        astronomical_date_candidates=["Future fulfillment", "70 AD (partial)"],
        genre="Prophetic Discourse",
        book_context="Luke's Olivet Discourse parallel",
    ),
    CategorizedVerse(
        reference="Amos 5:8",
        text="Seek him that maketh the seven stars and Orion, and turneth the shadow of death into the morning, and maketh the day dark with night: that calleth for the waters of the sea, and poureth them out upon the face of the earth: The LORD is his name.",
        category=CelestialCategory.WORSHIP_PRAISE,
        confidence=0.90,
        reasoning="Prophetic doxology calling Israel to seek God as Creator of constellations. Names Pleiades (seven stars) and Orion. Not predicting events but praising God's sovereignty over stars. Similar to Job 38.",
        celestial_objects=["Pleiades (seven stars)", "Orion"],
        cross_references=["Job 9:9", "Job 38:31", "Isaiah 40:26"],
        scholarly_sources=[
            ScholarlySource("Strong's H3598", "lexicon", "Kimah (seven stars/Pleiades)"),
            ScholarlySource("Strong's H3685", "lexicon", "Kesil (Orion)"),
        ],
        alternative_categories=[
            (CelestialCategory.PROPHETIC_SIGN, 0.20, "If 'day dark with night' refers to judgment"),
        ],
        genre="Prophetic Doxology",
        book_context="Amos calling Israel to repentance",
    ),
    CategorizedVerse(
        reference="Numbers 24:17",
        text="I shall see him, but not now: I shall behold him, but not nigh: there shall come a Star out of Jacob, and a Sceptre shall rise out of Israel, and shall smite the corners of Moab, and destroy all the children of Sheth.",
        category=CelestialCategory.PROPHETIC_SIGN,
        confidence=0.80,
        reasoning="Balaam's oracle prophesying future ruler from Israel. 'Star' is debated: (1) Metaphor for king/ruler, (2) Literal star sign at Messiah's birth (Star of Bethlehem connection), (3) Both. Messianic interpretation is ancient (Bar Kokhba = 'Son of Star').",
        celestial_objects=["star (out of Jacob)"],
        cross_references=["Matthew 2:2", "Revelation 22:16", "2 Peter 1:19"],
        scholarly_sources=[
            ScholarlySource("Strong's H3556", "lexicon", "kokab (star) - literal star or metaphor for ruler"),
            ScholarlySource("Targum Onkelos", "ancient translation", "Interprets as Messiah"),
        ],
        alternative_categories=[
            (CelestialCategory.METAPHORICAL, 0.45, "If 'star' is purely metaphor for king"),
        ],
        astronomical_date_candidates=["Star of Bethlehem candidates (3-2 BC)"],
        hebrew_greek_notes="'Kokab' used literally and metaphorically in OT. Parallelism with 'sceptre' suggests royal metaphor, but Magi may have interpreted astronomically.",
        genre="Prophetic Oracle",
        book_context="Balaam's oracles blessing Israel",
    ),
    CategorizedVerse(
        reference="Revelation 22:16",
        text="I Jesus have sent mine angel to testify unto you these things in the churches. I am the root and the offspring of David, and the bright and morning star.",
        category=CelestialCategory.METAPHORICAL,
        confidence=0.95,
        reasoning="Jesus self-identifying as 'morning star' (Venus). Metaphorical title, not astronomical prediction. Connects to Numbers 24:17 messianic 'star'. Also see 2 Peter 1:19. Title of glory, not celestial event.",
        celestial_objects=["morning star (Venus)"],
        cross_references=["Numbers 24:17", "2 Peter 1:19", "Revelation 2:28"],
        scholarly_sources=[
            ScholarlySource("Strong's G792+G4407", "lexicon", "aster proinos (morning star) - Venus"),
        ],
        hebrew_greek_notes="'Phosphoros' (light-bearer) in 2 Peter 1:19 is Latin 'Lucifer' - appropriated by Christ as rightful title",
        genre="Apocalyptic Epilogue",
        book_context="Jesus's final self-identification in Revelation",
    ),
    CategorizedVerse(
        reference="2 Peter 1:19",
        text="We have also a more sure word of prophecy; whereunto ye do well that ye take heed, as unto a light that shineth in a dark place, until the day dawn, and the day star arise in your hearts.",
        category=CelestialCategory.METAPHORICAL,
        confidence=0.95,
        reasoning="'Day star' (phosphoros) as metaphor for Christ's return/illumination in believers. Not predicting astronomical event but using celestial imagery for spiritual reality. Connected to Rev 22:16 morning star title.",
        celestial_objects=["day star (morning star/Venus)"],
        cross_references=["Revelation 22:16", "Malachi 4:2", "Numbers 24:17"],
        scholarly_sources=[
            ScholarlySource("Strong's G5459", "lexicon", "phosphoros (day star) - light-bearer, Venus"),
        ],
        hebrew_greek_notes="Greek 'phosphoros' = Latin 'lucifer' - the light-bearer (Venus). Peter applies to Christ.",
        genre="Epistle (Exhortation)",
        book_context="Peter encouraging believers to heed prophetic Scripture",
    ),
    CategorizedVerse(
        reference="Daniel 12:3",
        text="And they that be wise shall shine as the brightness of the firmament; and they that turn many to righteousness as the stars for ever and ever.",
        category=CelestialCategory.METAPHORICAL,
        confidence=0.95,
        reasoning="Simile comparing righteous people to stars - 'as the stars'. Not describing celestial events but future glorification of saints. Apocalyptic promise, not astronomical prophecy.",
        celestial_objects=["stars (as comparison)", "firmament"],
        cross_references=["Matthew 13:43", "1 Corinthians 15:41-42", "Philippians 2:15"],
        scholarly_sources=[
            ScholarlySource("Treasury of Scripture Knowledge", "cross-reference", "Dan 12:3"),
        ],
        hebrew_greek_notes="Comparative 'ke' (as/like) indicates simile, not identification",
        genre="Apocalyptic Vision",
        book_context="Daniel's vision of end times and resurrection",
    ),
]


def get_verses_by_category(category: CelestialCategory) -> list:
    return [v for v in CATEGORIZED_VERSES if v.category == category]


def get_astronomically_relevant_verses() -> list:
    relevant_categories = [
        CelestialCategory.PROPHETIC_SIGN,
        CelestialCategory.HISTORICAL_EVENT,
        CelestialCategory.CALENDAR_MARKER,
        CelestialCategory.CREATION_ACCOUNT,
    ]
    return [v for v in CATEGORIZED_VERSES if v.category in relevant_categories]


def get_datable_verses() -> list:
    return [v for v in CATEGORIZED_VERSES if v.astronomical_date_candidates]


def get_high_confidence_verses(min_confidence: float = 0.80) -> list:
    return [v for v in CATEGORIZED_VERSES if v.confidence >= min_confidence]


def format_verse_analysis(verse: CategorizedVerse) -> str:
    lines = [
        f"=== {verse.reference} ===",
        f"Category: {CATEGORY_DESCRIPTIONS[verse.category]['name']}",
        f"Confidence: {verse.confidence * 100:.0f}%",
        f"Astronomically Relevant: {CATEGORY_DESCRIPTIONS[verse.category]['astronomically_relevant']}",
        "",
        f"Text: \"{verse.text}\"",
        "",
        f"Genre: {verse.genre or 'Unknown'}",
        f"Context: {verse.book_context or 'N/A'}",
        "",
        "REASONING:",
        verse.reasoning,
        "",
    ]

    if verse.celestial_objects:
        lines.append(f"Celestial Objects: {', '.join(verse.celestial_objects)}")

    if verse.hebrew_greek_notes:
        lines.append(f"\nOriginal Language Notes: {verse.hebrew_greek_notes}")

    if verse.cross_references:
        lines.append(f"\nCross-References: {', '.join(verse.cross_references)}")

    if verse.alternative_categories:
        lines.append("\nAlternative Interpretations:")
        for alt_cat, conf, reason in verse.alternative_categories:
            lines.append(f"  - {CATEGORY_DESCRIPTIONS[alt_cat]['name']} ({conf*100:.0f}%): {reason}")

    if verse.astronomical_date_candidates:
        lines.append(f"\nCandidate Dates for Stellarium:")
        for date in verse.astronomical_date_candidates:
            lines.append(f"  - {date}")

    if verse.scholarly_sources:
        lines.append("\nScholarly Sources:")
        for src in verse.scholarly_sources:
            lines.append(f"  - {src.name} ({src.type}): {src.reference}")

    return "\n".join(lines)
