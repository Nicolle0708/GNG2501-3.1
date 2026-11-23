import json
from datetime import datetime, timedelta, timezone
from event_parser import parse_class_event

def run_test(test_name: str, title: str, location: str, minutes_from_now: int, notes: str):
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")
    
    fake_start = (datetime.now(timezone.utc) + timedelta(minutes=minutes_from_now)).isoformat()
    
    result = parse_class_event(
        title=title,
        location=location,
        start_time=fake_start,
        notes=notes
    )
    
    # Print a quick visual check of word counts + full JSON
    for i, page in enumerate(result, 1):
        # Strip < > brackets and count words on screen
        clean_screen = page["displayedText"].strip("<>")
        word_count = len(clean_screen.split())
        status = "OK" if word_count <= 3 else f"TOO LONG ({word_count} words!)"
        print(f"Page {i} [{status}]: {page['displayedText']}  |  Icon: {page['systemIcon']}")
        print(f"   Audio: \"{page['spokenText']}\"")


if __name__ == "__main__":
    # 1. Standard Math Class + Acronyms
    run_test(
        test_name="1. Math Class (Mixed bullets + TI-84 acronym)",
        title="Calculus I",
        location="Room B-204",
        minutes_from_now=10,
        notes="""
        • Bring TI-84 calculator
        - Don't forget to pack the blue binder
        1. Open Moodle for practice sheet
        2) Chapter 4 quiz today
        """
    )

    # 2. Bilingual / French Class Notes (Testing the 'dictionary' fix!)
    run_test(
        test_name="2. French Class (Bilingual commands + Omnivox + Dictionary)",
        title="Français 101",
        location="Pavillon C - 312",
        minutes_from_now=5,
        notes="""
        - Apporter le cahier bleu
        - Remettre le devoir sur Omnivox
        * Bring dictionary
        """
    )

    # 3. Unknown Nouns (Testing the catch-all 'bring' grammar fix)
    run_test(
        test_name="3. Unlisted Materials (Headphones, USB key, lab coat)",
        title="Chemistry Lab",
        location="Lab 402",
        minutes_from_now=15,
        notes="""
        - Bring noise-canceling headphones
        - Don't forget lab coat
        - Pack USB drive
        """
    )

    # 4. Very Long Event Title & Location (Checking 3-word screen limit)
    run_test(
        test_name="4. Long Title & Location Overflow Check",
        title="Introduction to Linear Algebra and Matrices",
        location="Alexandre-Taché Building Room 1045",
        minutes_from_now=20,
        notes="1. Bring textbook"
    )

    # 5. Online / Remote Class (Zoom & Teams)
    run_test(
        test_name="5. Remote Class (Zoom + Léa)",
        title="Sociology",
        location="Online - Zoom",
        minutes_from_now=2,
        notes="""
        1. Join Zoom meeting link
        2. Check Léa for reading PDF
        """
    )

    # 6. Single-Word Notes (Ensuring 'Open' or 'Calculator' doesn't break)
    run_test(
        test_name="6. Minimalist One-Word Notes",
        title="Physics",
        location="G-110",
        minutes_from_now=30,
        notes="""
        - Calculator
        - Notebook
        - Quiz
        """
    )

    # 7. Messy Whitespace & Empty Lines
    run_test(
        test_name="7. Messy Formatting & Blank Lines",
        title="History",
        location="A-201",
        minutes_from_now=12,
        notes="\n\n   •   Bring   the   red   folder.   \n\n   *   \n   2)   Submit essay   \n"
    )

    # 8. Empty Event (No location, no notes, starting right now)
    run_test(
        test_name="8. Bare Minimum Event (Starting Now)",
        title="Study Hall",
        location="",
        minutes_from_now=0,
        notes=""
    )
