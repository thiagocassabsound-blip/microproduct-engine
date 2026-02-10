# Base templates for microproducts

CHECKLIST_TEMPLATE = """# {title}

## Overview
{description}

## Checklist
{items}

## Next Steps
{next_steps}
"""

SCRIPT_TEMPLATE = """# {title}
# {description}

import os
import sys

def main():
    print("Starting {title}...")
    # Logic goes here
    {code_logic}
    print("Done!")

if __name__ == "__main__":
    main()
"""

SPREADSHEET_TEMPLATE = """
Title: {title}
Description: {description}
Columns: {columns}
Rows: {rows}
"""
