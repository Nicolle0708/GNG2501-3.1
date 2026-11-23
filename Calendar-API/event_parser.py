import re
from datetime import datetime, timezone

# The parser scans each bullet point form top to bottom against these
# parsing rules and stops at the FIRST match (so stuff thats more specific
# must be at the top, like for exceptions).
PARSING_RULES = [
    # --- CATEGORY 1: EXAMS & QUIZZES (Highest Priority) ---
    {
        "keywords": ["quiz", "exam", "test", "midterm", "examen", "interro"],
        "icon": "exclamationmark.triangle.fill",
        "speech_template": "Heads up, you have an evaluation: {item}."
    },
    {
        "keywords": ["submit", "hand in", "turn in", "homework", "assignment", "essay", "remettre", "devoir"],
        "icon": "pencil.and.list.clipboard",
        "speech_template": "Make sure to submit your work: {item}."
    },

    # --- CATEGORY 2: DIGITAL APPS & LINKS ---
    {
        "keywords": ["zoom", "teams", "meet", "call", "appel"],
        "icon": "video.fill",
        "speech_template": "Join your online meeting: {item}."
    },
    {
        "keywords": ["moodle", "classroom", "omnivox", "léa", "open", "app", "brightspace", "website", "ouvrir"],
        "icon": "arrow.up.forward.app.fill",
        "speech_template": "Digital action needed: {item}."
    },

    # --- CATEGORY 3: SPECIFIC MATERIALS ---
    {
        "keywords": ["laptop", "macbook", "pc", "computer", "ordinateur"],
        "icon": "laptopcomputer",
        "speech_template": "Pack your computer: {item}."
    },
    {
        "keywords": ["tablet", "ipad", "tablette"],
        "icon": "ipad",
        "speech_template": "Bring your tablet: {item}."
    },
    {
        "keywords": ["textbook", "book", "novel", "manual", "livre", "manuel"],
        "icon": "book.closed.fill",
        "speech_template": "Bring your book: {item}."
    },
    {
        "keywords": ["notebook", "binder", "folder", "cahier", "cartable"],
        "icon": "folder.fill",
        "speech_template": "Pack your folder or notebook: {item}."
    },
    {
        "keywords": ["calculator", "ti-84", "calculatrice"],
        "icon": "function",
        "speech_template": "Don't forget your calculator: {item}."
    },

    # --- CATEGORY 4: GENERIC CATCH-ALL (Always Last!) ---
    {
        "keywords": ["bring", "pack", "forget", "apporter", "prendre"],
        "icon": "backpack.fill",
        "speech_template": "Remember to bring your {item}."
    }
]

# Glue words to drop when building max 3-word text to display on the watch
STOP_WORDS = {
    "a", "an", "the", "my", "your", "our", "to", "for", "on", "in", "at", "with", "of",
    "don't", "forget", "remember", "make", "sure", "need", "please", "pack", "bring", "take", "grab",
    "le", "la", "les", "un", "une", "des", "du", "de", "d'", "mon", "ma", "mes", "ton", "ta", "tes",
    "votre", "vos", "pour", "sur", "dans", "avec", "et", "apporter", "apportez", "prendre", "prenez",
    "oublier", "penser", "pense", "à"
}

def make_short_title(raw_item: str, matched_keyword: str | None = None, max_words: int = 3) -> str:
    """
    Condenses a bullet point into at most `max_words` meaningful words so text never
    gets cut off mid-word on an Apple Watch screen.

    Strategy:
        1. Extract whole words (preserving hyphenated terms like "TI-84" or "B-204").
        2. Remove filler words listed in STOP_WORDS.
        3. If more than 3 words remain, center a 3-word window around `matched_keyword`
           (e.g., keeping "blue" right next to "binder").

    Args :
        raw_item (str): What was written in the calendar notes, what was sent by the app.
        matched_keyword (str): One of the glue words to drop
    
    Returns :
        str : Le nouveau texte de 3 mots maximum à afficher sur la montre.
    """
    # 1. Split into clean word tokens (keeping hyphenated terms like TI-84 intact)
    words = re.findall(r"[A-Za-zÀ-ÿ0-9\-']+", raw_item)
    
    # 2. Filter out glue/filler words (unless the whole note is tiny)
    meaningful = [w for w in words if w.lower() not in STOP_WORDS]
    if not meaningful:
        meaningful = words

    # 3. If it's already 3 words or fewer, we're done!
    if len(meaningful) <= max_words:
        chosen = meaningful
    elif matched_keyword:
        # Find where the matched keyword sits and grab a tight window around it
        kw_lower = matched_keyword.lower()
        idx = next((i for i, w in enumerate(meaningful) if kw_lower in w.lower()), 0)
        
        # Grab 1 word before the keyword (e.g. "blue" before "binder") + keyword + 1 after
        start = max(0, idx - 1)
        end = min(len(meaningful), start + max_words)
        # Adjust start if we hit the end of the list so we still get up to max_words
        start = max(0, end - max_words)
        chosen = meaningful[start:end]
    else:
        chosen = meaningful[:max_words]

    # 4. Join and capitalize the first letter cleanly (preserving acronyms like TI-84)
    title = " ".join(chosen)
    if title:
        title = title[0].upper() + title[1:]
    return f"{title}"

# Regex pattern that matches repetitive command verbs at the start of a note bullet point.
# like, "Don't forget to bring your blue binder" becomes just "blue binder" thanks to this pattern.
LEADING_FILLERS = re.compile(
    r"^(?:"
    r"don't forget to|remember to|make sure to|need to|please|"
    r"bring|pack|take|grab|open|launch|check|submit|hand in|turn in|"
    r"ne pas oublier de|n'oublie pas de|penser à|pense à|"
    r"apporter|apportez|prendre|prenez|ouvrir|ouvrez|remettre|remettez|rendre"
    r")\s+(?:your|my|the|a|an|ton|ta|tes|votre|vos|le|la|les|un|une|des)?\s*",
    re.IGNORECASE
)

def clean_item_text(raw_item: str) -> str:
    """
    Strips leading command verbs and articles from a note so spoken sentences don't
    sound repetitive (e.g., avoiding "Bring your book: Bring math book").
    """
    cleaned = LEADING_FILLERS.sub("", raw_item).strip()
    
    # Safety check: If stripping left almost nothing (e.g., note was just "Open"), keep original
    if len(cleaned) < 2:
        return raw_item.strip()
        
    return cleaned

def get_icon_and_speech(raw_item: str) -> tuple[str, str, str | None]:
    lower_raw = raw_item.lower()
    cleaned = clean_item_text(raw_item)
    
    for rule in PARSING_RULES:
        for kw in rule["keywords"]:
            # \b enforces whole-word matching so "pc" doesn't falsely match inside "topic"
            if re.search(rf"\b{re.escape(kw)}\b", lower_raw):
                # Avoid awkward repetition if the note was literally just the keyword itself
                # (e.g., "- Calculator" -> "Don't forget your calculator." instead of "...calculator: calculator.")
                if cleaned.lower() == kw.lower():
                    speech = rule["speech_template"].split(":")[0] + "."
                else:
                    speech = rule["speech_template"].format(item=cleaned)
                    
                return rule["icon"], speech, kw

    # Default fallback if no specific school keyword matched      
    return "checklist", f"{cleaned}.", None


def parse_class_event(title: str, location: str, start_time: str, notes: str) -> list[dict]:
    """
    Main API entry point

    This method seperates the main information of a Apple Calendar Event (title, location, date and notes)
    into a list of dictionnairies representing Apple Watch pages indicating :
    - The text that should be on the screen (maximum 3 words);
    - The text that should be spoken if the user wishes to have a Voice Over;
    - The name or an idicator of the icon that should appear on the screen;

    The format for each dictionnary (page) is :
    ```python
    {
        "displayedText" : "Example class",
        "systemIcon" : "this_is_an_icon",
        "spokenText" : "You have your Example class in 5 minutes."
    }
    ```

    Args :
        title (string): The title of the event.
        location (string): The location of the event.
        start_time (string): The starting time of the event, in ISO format (ex: "2026-11-22T21:36:00Z").
        notes (string): What is written in the "notes" section of the event.

    Returns :
        list[dict]: A list of the information each page (represented by a dictionnary) should hold.

    """
    pages = []

    #Page 1 : event announcement, shows the event icon (that the user chose) and in how much time the event is in.
    start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
    mins_left = int((start_dt - datetime.now(timezone.utc)).total_seconds() / 60)

    if mins_left > 0 :
        pages.append({
            "displayedText" : f"{mins_left} mins",
            "systemIcon" : "chosen_event_icon",
            "spokenText" : f"You have {title} in {mins_left} minutes."
        })
    else :
        pages.append({
            "displayedText" : "NOW",
            "systemIcon" : "chosen_event_icon",
            "spokenText" : f"Hurry. You have {title} right now."
        })

    #Page 2 : event location.
    if location and location.strip() : #adds a page if there is a location (location != none and location dosn't just contain spaces)
        clean_location = location.strip()
        if len(clean_location.split()) <= 3:
            pages.append({
                "displayedText" : f"{clean_location}",
                "systemIcon" : "mappin",
                "spokenText" : f"Go to {clean_location}."
            })
        else :
            print("Hello World!")
            # This is the scenario where the event location was a real location that was transformed
            # into an EKStructuredLocation object by the calendar.
            # Or the scenario where they put too much info about the location, or the building has a real
            # long name or something.
            # idk what to do with this yet...


    #Pages 3+ (the most important pages) : event notes, each distinct information (bullet point) in the event notes is seperated in pages.
    if notes and notes.strip():
        raw_items = re.split(r'(?:\r?\n|\s*[•\-*]\s+|\s*\d+[.;)]\s*)', notes)
        
        for raw in raw_items:
            raw_stripped = raw.strip(" .")
            if len(raw_stripped) < 2:
                continue
            
            icon, spoken, matched_kw = get_icon_and_speech(raw_stripped)
            short_display = make_short_title(raw_stripped, matched_keyword=matched_kw, max_words=3)
            
            pages.append({
                "displayedText" : short_display,
                "systemIcon" : icon,
                "spokenText" : spoken
            })

    #Page n : end of announcement, shows a checkmark to show the user that they have seen everything in the event.
    pages.append({
        "displayedText": "Done",
        "systemIcon" : "checkmark.circle.fill",
        "spokenText" : "That was all of the information about this event."
    })


    return pages
