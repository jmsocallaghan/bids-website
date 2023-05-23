"""
- rename files to YYYY-MM-DD-Steering-Group-minutes.*
- prettifies the html files
- process the markdown files by:
    - adding the front matter
    - removing the lines that are not relevant
    - using the html version of the tables instead of the markdown version
      because the pandoc version of the markdown tables is not very good
"""
from rich import print
from pathlib import Path
import datetime

input_folder = Path(__file__).parent


from bs4 import BeautifulSoup


def prettify_html(input_folder):
    for file in input_folder.glob("*.html"):
        # Read the HTML file
        with open(file, "r") as f:
            html = f.read()
        # Create BeautifulSoup object
        soup = BeautifulSoup(html, "html.parser")
        # Pretty print the HTML
        pretty_html = soup.prettify()
        with open(file, "w") as f:
            f.write(pretty_html)


def rename_files(input_folder):
    for file in input_folder.glob("*.md"):
        with open(file, "r") as f:
            text = f.readlines()

        for line in text:
            if "Date" in line:
                line = line.replace("\n", "")
                year = str(file.name).split("_")[0]
                if len(year) > 4:
                    year = str(file.name).split("-")[0]
                month, day = line.split(" ")[2:]
                mnum = datetime.datetime.strptime(month, "%B").month
                new_name = f"{year}-{mnum:02d}-{int(day):02d}-Steering-Group-minutes.md"
                print(file)
                print(new_name)
                file.rename(new_name)
                hmtl_file = file.with_suffix(".html")
                if hmtl_file.exists():
                    hmtl_file.rename(Path(new_name).with_suffix(".html"))
                break


def sanitize_md(input_folder):
    for file in input_folder.glob("*.md"):
        year = str(file.name).split("-")[0]
        month = str(file.name).split("-")[1]
        day = str(file.name).split("-")[2]

        with open(file, "r") as f:
            text = f.readlines()

        with open(file, "w") as f:
            add_front_matter_and_title(f, year, month, day)

            write_line = False

            for line in text:
                # skip lines that are not relevant
                if any(
                    x in line
                    for x in [
                        "Check your local time",
                        "arewemeetingyet",
                        "stanford.zoom",
                        "Password:",
                        "Time:",
                        "Room:",
                        "Attending:",
                    ]
                ):
                    continue

                # skip lines that are markdown tables
                if any(line.startswith(x) for x in ["|", "+-", "+="]):
                    continue

                if write_line:
                    f.write(line)

                if "Date" in line:
                    write_line = True
                    line = line.replace("\n", "")
                    f.write(f"{line}, {year}\n")
                    f.write("\n<!--more-->\n\n\n")
                    # add the table in html format for better rendering
                    print_table_from_html(file, f)


def add_front_matter_and_title(f, year, month, day):
    f.write(
        f"""---
title: Steering Group minutes
author:
display: true
---

# Steering Group minutes {year}/{month}/{day}

"""
    )


def print_table_from_html(input_file: Path, output_file):
    html_file = input_file.with_suffix(".html")
    if html_file.exists():
        with open(html_file, "r") as f:
            text = f.readlines()
            print_line = False
            for line in text:
                if "<table>" in line:
                    print_line = True
                if "</table>" in line:
                    output_file.write(line)
                    print_line = False
                if print_line:
                    output_file.write(line)


def main():
    rename_files(input_folder)
    prettify_html(input_folder)
    sanitize_md(input_folder)


if __name__ == "__main__":
    main()