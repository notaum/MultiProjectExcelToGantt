import csv
import random
from datetime import datetime, timedelta

def create_sample_csv(filename="sample_projects.csv"):
    # Define 8 project names
    projects = [
        "Website Redesign", 
        "Mobile App Development", 
        "Data Migration", 
        "Marketing Campaign", 
        "Product Launch", 
        "Infrastructure Upgrade",
        "Customer Portal", 
        "Analytics Dashboard"
    ]
    
    # Set date range: 6 months period from Jan to Jun 2025
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 6, 30)
    total_days = (end_date - start_date).days
    
    # Prepare data for each project
    all_tasks = []
    
    for project in projects:
        num_tasks = random.randint(3, 8)
        project_tasks = []
        
        # Project starts within first 2 months
        project_start = start_date + timedelta(days=random.randint(0, 60))
        current_date = project_start
        
        for i in range(num_tasks):
            # Task duration between 5-20 days
            task_duration = random.randint(5, 20)
            task_end = current_date + timedelta(days=task_duration)
            
            # Ensure we don't go beyond end date
            if task_end > end_date:
                break
            
            task_name = f"T{i+1}" if i < 26 else f"T{chr(65+i%26)}"  # T1, T2, ... or TA, TB, ...
            
            project_tasks.append({
                'name': task_name,
                'start': current_date,
                'end': task_end
            })
            
            # Next task starts after current task ends + random gap (1-5 days)
            gap = random.randint(1, 5)
            current_date = task_end + timedelta(days=gap)
            
            if current_date > end_date:
                break
        
        all_tasks.append(project_tasks)
    
    # Write to CSV
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header row
        header = []
        for project in projects:
            header.extend([project, 'Start', 'End'])
        writer.writerow(header)
        
        # Find maximum number of tasks in any project
        max_tasks = max(len(tasks) for tasks in all_tasks)
        
        # Write task rows
        for row_index in range(max_tasks):
            row = []
            for project_index in range(len(projects)):
                tasks = all_tasks[project_index]
                if row_index < len(tasks):
                    task = tasks[row_index]
                    row.extend([
                        task['name'],
                        task['start'].strftime('%d/%m/%Y'),  # Changed to D/M/Y
                        task['end'].strftime('%d/%m/%Y')     # Changed to D/M/Y
                    ])
                else:
                    row.extend(['', '', ''])  # Empty cells for projects with fewer tasks
            writer.writerow(row)
    
    print(f"Sample CSV generated: {filename}")
    print(f"Format: {projects[0]},Start,End,{projects[1]},Start,End,...")
    print(f"Total projects: {len(projects)}")
    
    # Show task count per project
    for i, (project, tasks) in enumerate(zip(projects, all_tasks)):
        print(f"  {project}: {len(tasks)} tasks")

# Generate the sample CSV
create_sample_csv()