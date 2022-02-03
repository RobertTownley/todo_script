# TODO

A simple python script for keeping track of TODO items in a single markdown file. This script borrows heavily from the offline art of bullet journaling.

## Requirements

- Python3 installed somewhere on your system path

## Installation

Clone this repo to somewhere locally

```
mkdir -p ~/Projects/todo
cd ~/Projects/todo
git clone https://github.com/RobertTownley/todo_script.git .
```

Then add it to your path via a symlink

```
ln -s ~/Projects/todo/main.py ~/bin/TODO
```

## Usage

As long as it's been added to your path, you can now run `TODO` (or case-insensitive `todo` if you're on mac) and it will open your editor to a newly-generated `~/TODO.md` file.

## Configuration

- If you don't use `nvim`, you'll want to set your EDITOR environment variable.
- The script defaults to using `~/TODO.md` as the filepath for the created file. You can change this by setting your `TODO_FILEPATH` environment variable.
