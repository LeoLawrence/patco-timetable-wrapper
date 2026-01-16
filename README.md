# PATCO Scheduler Generator

This project automates the creation of a static HTML schedule for PATCO trains by parsing the official PDF timetable. The result is a single-file HTML application containing the schedule data, robust enough to run without a backend server.

## Features

- **Automated PDF Parsing**: Extracts train times from the PATCO timetable PDF (`PATCO_Timetable.pdf`).
- **Static Building**: Inlines schedule data directly into the HTML file.
- **Offline Capable**: The generated `index.html` requires no internet connection or server to run.
- **Smart Scheduling**:
  - Automatically detects Weekday, Saturday, or Sunday schedules.
  - Handles train directions (Westbound/Eastbound) based on station selection.
  - Highlights the "Next Train" in real-time.

## Prerequisites

- Python 3.8+
- `pip` (Python package manager)

## Setup and Usage

1. **Clone/Download** this repository.
2. **Set up Virtual Environment** (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Build the Site**:
   Ensure `PATCO_Timetable.pdf` is in the root directory.
   ```bash
   python3 build.py
   ```
   This will:
   - Run the extractor (`extract_schedule.py`).
   - Generate `schedule.json`.
   - Inject the JSON into `index.html`.
   - Output the final site to the `dist/` directory.

5. **Run**:
   Open `dist/index.html` in any web browser.

## File Structure

- `build.py`: Main build script. Orchestrates extraction and packaging.
- `extract_schedule.py`: Logic to parse the PDF and normalize data.
- `index.html`: The frontend template.
- `requirements.txt`: Python dependencies (`pdfplumber`).
- `dist/`: Output directory containing the ready-to-use site.
