import pdfplumber
import json
import re

# Station lists in order of appearance in the table columns
STATIONS_WEST = [
    "Lindenwold", "Ashland", "Woodcrest", "Haddonfield", "Westmont", "Collingswood",
    "Ferry Avenue", "Broadway", "City Hall", "Franklin Square",
    "8th & Market", "9/10th & Locust", "12/13th & Locust", "15/16th & Locust"
]

STATIONS_EAST = [
    "15/16th & Locust", "12/13th & Locust", "9/10th & Locust", "8th & Market",
    "Franklin Square", "City Hall", "Broadway", "Ferry Avenue",
    "Collingswood", "Westmont", "Haddonfield", "Woodcrest", "Ashland", "Lindenwold"
]

def parse_time(t_str):
    """
    Parses '4:30A', '12:00P' into minutes from midnight.
    Returns None for invalid/skip.
    """
    t_str = t_str.strip()
    if not t_str or 'à' in t_str or 'a' in t_str.lower():
        if t_str == 'à':
            return None
            
    # Normalize
    t_str = t_str.upper().replace('.', '')
    match = re.match(r'(\d+):(\d+)([AP])', t_str)
    if not match:
        return None
    
    h = int(match.group(1))
    m = int(match.group(2))
    meridiem = match.group(3)
    
    if meridiem == 'P' and h != 12:
        h += 12
    if meridiem == 'A' and h == 12:
        h = 0
        
    return h * 60 + m

def format_minutes(mins):
    if mins is None:
        return "-"
    h = (mins // 60) % 24
    m = mins % 60
    mer = "AM"
    if h >= 12:
        mer = "PM"
        if h > 12: h -= 12
    if h == 0: h = 12
    return f"{h}:{m:02d} {mer}"

schedule = {
    "weekday": {"westbound": [], "eastbound": []},
    "saturday": {"westbound": [], "eastbound": []},
    "sunday": {"westbound": [], "eastbound": []}
}

def process_page(page, day_types):
    """
    day_types: list of keys to assign tables to. 
    E.g. ["weekday"] for page 1 (both tables).
    ["saturday", "sunday"] for page 2 (tables 0/1 sat, 2/3 sun).
    """
    words = page.extract_words()
    words.sort(key=lambda w: w['top'])
    rows = []
    current_row = []
    last_top = -100
    
    for w in words:
        if w['top'] > last_top + 5: # New row
            if current_row:
                rows.append(current_row)
            current_row = [w]
            last_top = w['top']
        else:
            current_row.append(w)
    if current_row:
        rows.append(current_row)
    
    sunday_label_y = 9999
    for w in words:
        if "SUNDAY" in w['text']:
            sunday_label_y = w['top']
            break
            
    for row in rows:
        row.sort(key=lambda w: w['x0'])
        time_words = [w for w in row if (":" in w['text'] or "à" in w['text']) and len(w['text']) < 8]
        
        if len(time_words) < 8: # Not enough data for a schedule row
            continue
            
        # Determine Day based on Y
        current_day = day_types[0]
        if len(day_types) > 1:
            row_y = row[0]['top']
            if row_y > sunday_label_y:
                current_day = day_types[1]
        
        west_items = [w for w in row if w['x0'] < 305]
        east_items = [w for w in row if w['x0'] > 305]
        
        west_times = [w for w in west_items if (":" in w['text'] or "à" in w['text'])]
        
        if len(west_times) >= 10:
             entry = {}
             count = min(len(west_times), len(STATIONS_WEST))
             for i in range(count):
                 t_val = parse_time(west_times[i]['text'])
                 entry[STATIONS_WEST[i]] = t_val
             
             if any(entry.values()):
                 schedule[current_day]["westbound"].append(entry)
                 
        east_times = [w for w in east_items if (":" in w['text'] or "à" in w['text'])]
        if len(east_times) >= 10:
             entry = {}
             count = min(len(east_times), len(STATIONS_EAST))
             for i in range(count):
                 t_val = parse_time(east_times[i]['text'])
                 entry[STATIONS_EAST[i]] = t_val
             
             if any(entry.values()):
                 schedule[current_day]["eastbound"].append(entry)

with pdfplumber.open("PATCO_Timetable.pdf") as pdf:
    print("Processing Page 1 (Weekday)...")
    process_page(pdf.pages[0], ["weekday"])
    print("Processing Page 2 (Sat/Sun)...")
    process_page(pdf.pages[1], ["saturday", "sunday"])

with open("schedule.json", "w") as f:
    json.dump(schedule, f, indent=2)

print("Extraction complete. Summary:")
for day in schedule:
    for direction in schedule[day]:
        print(f"  {day} {direction}: {len(schedule[day][direction])} trains")
