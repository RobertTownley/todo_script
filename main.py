#!/usr/local/bin/python3
import os

from datetime import datetime, timedelta
from pathlib import Path
from subprocess import call

DEFAULT_FILEPATH = f"{Path.home()}/TODO.md"
FILEPATH = os.environ.get("TODO_FILEPATH", DEFAULT_FILEPATH)
END_OF_WEEK_MARKER = "<!-- End of Week -->\n\n"
UNRESOLVED_ITEMS_HEADER = "## Unresolved Items:"

def suffix(day: int):
    if 4 <= day <= 20 or 24 <= day <= 30:
        return "th"
    else:
        return ["st", "nd", "rd"][day % 10 - 1]

def format_date(d: datetime) -> str:
    s = suffix(int(d.strftime("%d")))
    DATE_FORMAT = f"%A, %b %-d{s}, %Y"
    return d.strftime(DATE_FORMAT)


def get_existing_contents() -> str:
    if not os.path.isfile(FILEPATH):
        return ""

    with open(FILEPATH) as f:
        data = f.read()
    return data


def get_new_week_header_row() -> str:
    now = datetime.now()
    monday = datetime.now() - timedelta(days=now.weekday())
    friday = monday + timedelta(days=4)
    return f"# Week of {format_date(monday)} -> {format_date(friday)}"

def get_new_day_rows() -> str:
    now = datetime.now()
    start = datetime.now() - timedelta(days=now.weekday())
    rows = ""
    for i in range(0, 5):
        current = start + timedelta(days=i)
        rows += f"## {format_date(current)}\n\n"
        rows += "- [ ]\n\n"
    rows += END_OF_WEEK_MARKER
    return rows


def needs_new_week(contents: str) -> bool:
    header = get_new_week_header_row()
    first_row = contents.split("\n")[0]
    return first_row.strip() != header

def resolve_items(contents: str):
    """Move items without a marking to the top of the week for resolution"""
    unresolved_items = []

    # Get existing unresolved items
    if UNRESOLVED_ITEMS_HEADER in contents:
        existing_unresolved_content = contents.split(UNRESOLVED_ITEMS_HEADER)[1]
        existing_lines = existing_unresolved_content.split("##")[0].split("\n")
        unresolved_items = list(set(filter(lambda x: bool(x), existing_lines)))

    # Move items from prior weeks
    prior_weeks = contents.split(END_OF_WEEK_MARKER)[1:]
    for week in prior_weeks:
        for line in week.split("\n\n"):
            if line.startswith("- [ ] ") and line not in unresolved_items:
                unresolved_items.append(line)
                
                # Mark line as having been moved to unresolved
                new_line = line[:3] + "?" + line[4:]
                contents = contents.replace(line, new_line)

    lines = contents.split("\n")
    if unresolved_items:
        if lines[1] != UNRESOLVED_ITEMS_HEADER:
            lines.insert(1, UNRESOLVED_ITEMS_HEADER)
        for item in unresolved_items:
            if item not in lines:
                lines.insert(2, item)
    else:
        # Remove header
        if UNRESOLVED_ITEMS_HEADER in contents:
            lines = [lines[0], *lines[2:]]

    contents = "\n".join(lines)
    with open(FILEPATH, "w+") as f:
        f.write(contents)


def get_opening_line_number(contents: str):
    formatted = format_date(datetime.now())
    for index, line in enumerate(contents.split("\n")):
        if formatted in line:
            return index + 3
    return 0

if __name__ == "__main__":
    # Change file contents as needed
    contents = get_existing_contents()
    if needs_new_week(contents):
        existing_contents = contents
        contents = get_new_week_header_row()
        contents += "\n\n"
        contents += get_new_day_rows()
        contents += existing_contents
        with open(FILEPATH, "w+") as f:
            f.write(contents)

    resolve_items(contents)

    # Open Editor
    EDITOR = os.environ.get('EDITOR','nvim')
    line_number = get_opening_line_number(contents)
    call([EDITOR, f"+{line_number}", FILEPATH])
