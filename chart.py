import sys
import csv
import re
import colorsys
import pandas as pd
import plotly.express as px
from datetime import date, timedelta

def parse_date(date_str):
    date_str = date_str.strip().rstrip('.')
    match = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', date_str)
    if not match:
        raise ValueError(f"Cannot parse date: {date_str}")
    d, m, y = map(int, match.groups())
    try:
        return date(y, m, d)
    except ValueError as e:
        raise ValueError(f"Invalid date: {date_str}") from e

def ordinal(n):
    if 11 <= (n % 100) <= 13:
        s = 'th'
    else:
        s = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + s

def create_shade(hex_color, shade_factor):
    """Create a shade by adjusting lightness of a hex color"""
    if hex_color.startswith('#'):
        hex_color = hex_color[1:]
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    # Adjust lightness to create shade (darker)
    l_adjusted = l * (1 - shade_factor * 0.6)
    l_adjusted = max(0.3, l_adjusted)  # Prevent too dark
    r, g, b = colorsys.hls_to_rgb(h, l_adjusted, s)
    r = int(r * 255 + 0.5)
    g = int(g * 255 + 0.5)
    b = int(b * 255 + 0.5)
    return f'#{r:02x}{g:02x}{b:02x}'

if len(sys.argv) < 2:
    print("Usage: python chart.py name.csv (optional) --dark (optional) Height Multiplier")
    sys.exit(1)

input_file = sys.argv[1]
dark_mode = False
height_multiplier = 1.0

if len(sys.argv) > 2:
    if sys.argv[2] == '--dark':
        dark_mode = True
        if len(sys.argv) > 3:
            try:
                height_multiplier = 1 + int(sys.argv[3]) / 100
            except ValueError:
                print("Height percent must be an integer.")
                sys.exit(1)
    else:
        try:
            height_multiplier = 1 + int(sys.argv[2]) / 100
        except ValueError:
            print("Height percent must be an integer.")
            sys.exit(1)

try:
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        raise ValueError("Empty file")
    header = [col.strip() for col in rows[0]]
    data_rows = [[cell.strip() for cell in row] for row in rows[1:]]

    # Find projects
    projects = []
    for col in header:
        if col not in ['Start', 'End']:
            projects.append(col)
    num_projs = len(projects)
    if len(header) != num_projs * 3:
        print("Header format mismatch. Expected format: ProjectName,Start,End,...")
        sys.exit(1)

    # Now parse data
    parsed_data = []
    for row in data_rows:
        for k in range(num_projs):
            task_col = k * 3
            if task_col >= len(row):
                break
            task = row[task_col]
            if not task:
                continue
            start_str = row[task_col + 1] if task_col + 1 < len(row) else ''
            end_str = row[task_col + 2] if task_col + 2 < len(row) else ''
            if not start_str or not end_str:
                continue
            try:
                start = parse_date(start_str)
                end = parse_date(end_str)
                parsed_data.append((projects[k], task, start, end))
            except ValueError as e:
                print(f"Skipping invalid date in row {row}: {e}")
                continue

    # Build DataFrame
    data = []
    for proj, task, st, en in parsed_data:
        data.append({'Project': proj, 'Task': task, 'Start': st, 'Finish': en})

    if not data:
        print("No valid tasks found.")
        sys.exit(1)

    df = pd.DataFrame(data)

    # Prepare colors - FIXED: Create unique task identifiers
    unique_projs = sorted(df['Project'].unique())
    n_projs = len(unique_projs)
    color_sets = px.colors.qualitative.Plotly
    base_colors_list = (color_sets * ((n_projs // len(color_sets)) + 1))[:n_projs]
    base_colors = dict(zip(unique_projs, base_colors_list))

    # Create a unique identifier for each task by combining project and task
    df['Task_Unique'] = df['Project'] + ' - ' + df['Task']

    # Create color mapping for each unique task
    color_discrete_map = {}
    
    # Group by project and sort tasks by start date within each project
    for project in unique_projs:
        project_tasks = df[df['Project'] == project].sort_values('Start')
        tasks = project_tasks['Task_Unique'].tolist()
        n_tasks = len(tasks)
        
        base_color = base_colors[project]
        
        # Assign shades to tasks based on their order
        for i, task_unique in enumerate(tasks):
            # Calculate shade factor (0 for first task, 1 for last task)
            shade_factor = i / max(n_tasks - 1, 1) if n_tasks > 1 else 0
            color = create_shade(base_color, shade_factor)
            color_discrete_map[task_unique] = color

    # Sort for ordering
    df_sorted = df.sort_values(['Project', 'Start'])

    # Create figure - use the unique task identifier for coloring
    fig = px.timeline(
        df_sorted,
        x_start='Start',
        x_end='Finish',
        y='Project',
        color='Task_Unique',
        color_discrete_map=color_discrete_map
    )

    # Update layout for good looks
    template = 'plotly_dark' if dark_mode else 'plotly_white'
    output_suffix = '_dark' if dark_mode else ''
    grid_color = "#4D4D4D" if dark_mode else "#D2D5D9"
    daily_line_color = "#4D4D4D" if dark_mode else "#C7C7C7"
    text_color = "white" if dark_mode else "black"
    paper_bgcolor = "#1e1e1e" if dark_mode else "white"
    plot_bgcolor = "#2d2d2d" if dark_mode else "white"

    default_height = max(400, len(unique_projs) * 100)
    height = int(default_height * height_multiplier)

    # Extend x-axis by 1 month on both sides
    start_date = df['Start'].min()
    end_date = df['Finish'].max()
    extended_start = start_date - timedelta(days=30)
    extended_end = end_date + timedelta(days=30)

    fig.update_layout(
        title='Project Timeline Gantt Chart',
        xaxis_title='Date',
        yaxis_title='Projects',
        height=height,
        showlegend=True,
        xaxis=dict(
            rangeslider=dict(visible=True),
            range=[extended_start, extended_end]
        ),
        template=template,
        font=dict(color=text_color),
        paper_bgcolor=paper_bgcolor,
        plot_bgcolor=plot_bgcolor
    )

    # Create date labels: 1st and 15th of each month
    current = extended_start.replace(day=1)
    tickvals = []
    ticktext = []
    
    while current <= extended_end:
        # Add 1st of month
        if current.day == 1:
            tickvals.append(current)
            day_str = ordinal(current.day)
            month_abbr = current.strftime('%b')
            ticktext.append(f"{day_str} {month_abbr}")
        
        # Add 15th of month
        current_15th = current.replace(day=15)
        if current_15th >= extended_start and current_15th <= extended_end:
            tickvals.append(current_15th)
            day_str = ordinal(15)
            month_abbr = current_15th.strftime('%b')
            ticktext.append(f"{day_str} {month_abbr}")
        
        # Move to next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1, day=1)
        else:
            current = current.replace(month=current.month + 1, day=1)

    fig.update_xaxes(
        tickvals=tickvals,
        ticktext=ticktext,
        tickangle=-45,
        gridcolor=grid_color,
        gridwidth=0.5
    )

    # Order y-axis
    fig.update_yaxes(categoryorder='array', categoryarray=unique_projs)

    # Style traces - make bars fully solid with slight rounding
    fig.update_traces(
        marker=dict(
            line_width=1,
            opacity=1.0,
            cornerradius=5
        )
    )

    # Add daily vertical lines behind the bars, now over extended range
    min_date = extended_start
    max_date = extended_end
    current_date = min_date
    shapes = []
    while current_date <= max_date:
        shapes.append(dict(
            type="line",
            x0=current_date,
            x1=current_date,
            y0=0,
            y1=1,
            xref="x",
            yref="paper",
            line=dict(
                color=daily_line_color,
                width=0.5,
            ),
            layer="below"
        ))
        current_date += timedelta(days=1)
    fig.update_layout(shapes=shapes)

    fig.show()

    # Export to HTML
    outputname = str(sys.argv[1])
    output_file = f'{outputname}{output_suffix}.html'
    fig.write_html(output_file, include_plotlyjs='cdn')
    print(f"Chart exported to {output_file}")
except FileNotFoundError:
    print(f"File not found: {input_file}")
    sys.exit(1)
except Exception as e:
    print(f"Error reading file: {e}")
    sys.exit(1)