"""
This script generates a list of credits from the project files and updates
the README file with the credit information.
"""

import os
import urllib.parse

# Initialize an empty list to hold the credit lines
credit_lines = []
credit_lines.append(
    "All the Credits and hyperlinks can be found in the respective files on the indicated lines.\n\n"  # noqa
    "Note that the list of credits below is automatically generated from the project files using the [copy-credits.py](copy-credits.py) script.\n"  # noqa
    "The script was written by me, with much help from the Microsoft Edge Copilot.\n"  # noqa
    "| File | Notes | Source |\n"
    "| --- | --- | --- |"
)

# Define comment symbols for different file types
comment_symbols = {
    ".py": ["#"],
    ".html": ["<!--", "//"],
    ".js": ["//"],
    ".css": ["/*"],
}

# Define the base URL for the files in your GitHub repository
base_url = "https://github.com/benschaf/gipfel-tutor/blob/main/"

# Walk through all files in the project directory
for root, dirs, files in os.walk("."):

    # Exclude 'staticfiles' directory as it is a duplicate of the 'static'
    # directory
    if "staticfiles" in dirs:
        dirs.remove("staticfiles")

    for file in files:
        # Get the file extensioned
        ext = os.path.splitext(file)[1]
        # If the file extension is in the comment symbols dictionary
        if ext in comment_symbols:
            # Try to open the file
            try:
                with open(os.path.join(root, file), "r") as f:
                    # Read the file line by line
                    lines = f.read().splitlines()
            except UnicodeDecodeError:
                print(f"Skipping file {file} due to encoding issues.")
                continue
            # Iterate over the lines with an index
            for i in range(len(lines)):
                # Check against all comment symbols for the current file
                # extension
                for symbol in comment_symbols[ext]:
                    # If a line starts with a comment symbol,
                    # followed by " -> Credit"
                    if lines[i].strip().startswith(symbol + " -> Credit"):
                        # Split the credit line into description and URL
                        credit_parts = (
                            lines[i]
                            .strip()
                            .replace(" -> Credits for ", "")
                            .replace(" -> Credits ", "")
                            .replace(" -> Credit for ", "")
                            .replace(" -> Credit ", "")
                            .replace("-->", "")
                            .replace("*/", "")
                            .replace("# noqa", "")
                            .strip()[len(symbol):]
                            .split(": ")
                        )
                        description = credit_parts[0]
                        url = credit_parts[1] if len(credit_parts) > 1 else ""

                        # Parse the URL to get the website name
                        website_name = urllib.parse.urlparse(
                            url).netloc if url else ""

                        # Format the credit line as a row in the markdown table
                        credit_line = (
                            f"| [{file}: Line {i+1}]({base_url + os.path.join(root, file).replace('./', '')}#L{i+1}) | {description} | [{website_name if website_name else 'Link'}]({url}) |"  # noqa
                            if url
                            else f"| [{file}: Line {i+1}]({base_url + os.path.join(root, file).replace('./', '')}#L{i+1}) | {description} |"  # noqa
                        )
                        credit_lines.append(credit_line)

# Open the README file
with open("README.md", "r") as readme_file:
    # Read the file line by line
    readme_lines = readme_file.read().splitlines()

# Find the index of the line with the "<!-- CREDITS_START -->" comment
credits_index = next(
    i for i, line in enumerate(readme_lines)
    if "<!-- CREDITS_START -->" in line
)

# Find the index of the line with the "<!-- CREDITS_END -->" comment
acknowledgements_index = next(
    i for i, line in enumerate(readme_lines) if "<!-- CREDITS_END -->" in line
)

# Replace the lines between these two indices with the new content
updated_content = (
    readme_lines[: credits_index + 1]
    + credit_lines
    + readme_lines[acknowledgements_index:]
)

# Write the updated content back to the README file
with open("README.md", "w") as readme_file:
    readme_file.write("\n".join(updated_content))

print("Credit lines written to README file.")
