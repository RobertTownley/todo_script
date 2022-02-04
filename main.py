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


def get_existing_contents(remove_header=False) -> str:
    if not os.path.isfile(FILEPATH):
        return ""

    with open(FILEPATH) as f:
        contents = f.read()
    if remove_header:
        contents = "\n".join(contents.split("\n")[1:])
    return contents


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

def resolve_previous_weeks_items():
    """Move items without a marking to the top of the week for resolution"""
    contents = get_existing_contents()
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

def add_line_to_today(line):
    contents = get_existing_contents(remove_header=True)
    today = format_date(datetime.now())
    for index, current_line in enumerate(contents.split("\n")):
        if today in current_line:
            lines = contents.split("\n")
            lines.insert(index + 2, line)
            contents = "\n".join(lines)
            save_contents(contents)

def mark_line(line: str, symbol: str):
    lines = get_existing_contents().split("\n")
    for index, current_line in enumerate(lines):
        if line == current_line:
            lines[index] = line.replace("[ ]", f"[{symbol}]")
            break
    contents = "\n".join(lines)
    save_contents(contents)


def resolve_this_week_items():
    # Remove header from contents in case today appears in header
    contents = get_existing_contents(remove_header=True)

    this_week = contents.split(END_OF_WEEK_MARKER)[0]
    today = format_date(datetime.now())
    before_today = this_week.split(today)[0]

    # Move outstanding items to today
    for line in before_today.split("\n"):
        if "- [ ] " in line:
            print(line)
            add_line_to_today(line)
            mark_line(line, "->")


def get_opening_line_number():
    contents = get_existing_contents()
    formatted = format_date(datetime.now())
    for index, line in enumerate(contents.split("\n")):
        if formatted in line:
            return index + 3
    return 0

def save_contents(contents: str):
    header = get_new_week_header_row()
    if header not in contents:
        # Add back header, in case `get_existing_contents` was called with
        # remove_header=True
        contents = header + "\n" + contents
    with open(FILEPATH, "w+") as f:
        f.write(contents)


if __name__ == "__main__":
    # Change file contents as needed
    contents = get_existing_contents()
    if needs_new_week(contents):
        existing_contents = contents
        contents = get_new_week_header_row()
        contents += "\n\n"
        contents += get_new_day_rows()
        contents += existing_contents
        save_contents(contents)

    resolve_previous_weeks_items()
    resolve_this_week_items()

    # Open Editor
    EDITOR = os.environ.get('TODO_EDITOR','vim')
    line_number = get_opening_line_number()
    call([EDITOR, f"+{line_number}", FILEPATH])
