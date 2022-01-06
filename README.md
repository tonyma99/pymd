# pymd

## Description

Processes all notes written in `markdown` using [pandoc](https://pandoc.org/) and serves the processed notes on a server for viewing.

Valid markdown files stored in the specified directory structure will be processed, creating a table of contents for every semester directory that contains all of its courses and notes.

Allows for math expressions to be processed using [LaTeX](https://www.latex-project.org/) syntax through [KaTeX](https://katex.org/).

## Usage

### Prerequisites 

Ubuntu

```
sudo apt install python3 pandoc
```

Mac

```
brew install python3 pandoc 
```

### Instructions

```
python3 server.py [-h] [-s] [-p PORT]
```

The server runs in **dynamic** mode by default.

- This allows for updates from the markdown files without restarting the server
- **Static** mode can be enabled with the `-s` flag for improved performance

Markdown files **must** be stored in the specified directory layout below.

- The semester directories must follow Simon Fraser University's 4-digit [term code system](https://www.sfu.ca/students/calendar/2019/fall/fees-and-regulations/enrolment/enrolment-definitions.html)
    - 1 represents the 2**1**st century
    - 19 = year (e.g. 20**19**)
    - The final digit is the term: **1** for spring, **4** for summer and **7** for fall
- The course directories must start with alphabetical characters followed by numerical characters
- The file names for the notes must start with a number followed by a hyphen
    - Spaces for the file names must also be hyphens

An optional file (`courses.json`) can be provided to add additional details to the table of contents.

- The `courses.json` file allows for the instructor's name and links to the course page(s) to be added
- If no `courses.json` file is provided, the name of the course will be the file name

#### Example Directory Layout

```
pymd
├── 1217
│   ├── cs50
│   │   ├── 1-title-name.md
│   │   ├── 2-title-name.md
│   │   └── ...
│   └── cs120 ...
├── 1221 ...
├── base.html
├── server.py
├── metadata.yaml
└── courses.json (optional)
```

#### Example `courses.json`

``` json
[
    {
        "semester": 1217,
        "courses": [
            {
                "course": "cs50",
                "name": "Introduction to Computer Science",
                "instructor": "David J. Malan",
                "websites": [
                    {
                        "name": "Harvard",
                        "link": "https://cs50.harvard.edu/college/2021/fall/"
                    }
                ]
            }
        ]
    }
]
```
