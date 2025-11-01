# Multi Project Excel To Gantt

A powerful Python script that generates interactive, professional Gantt charts from CSV data using Plotly. Perfect for project managers, teams, and anyone needing to visualize project timelines and task dependencies.

## Features

- 🎨 **Interactive Charts** - Zoom, pan, and hover for detailed task information
- 🌙 **Dark/Light Mode** - Choose your preferred theme
- 🎯 **Smart Color Coding** - Automatic color assignment with shaded variants for tasks within projects
- 📱 **Responsive Design** - Adjustable chart height and mobile-friendly output
- 📅 **Intelligent Date Formatting** - Clear date labels with ordinal numbers (1st, 2nd, 3rd)
- 💾 **HTML Export** - Share interactive charts with stakeholders
- 🔧 **Customizable** - Command-line options for theme and sizing

## Script Overview

The repository contains four specialized scripts for different Gantt chart needs:

| Script | Description | Best For |
|--------|-------------|----------|
| `chart.py` | Basic Gantt chart without task labels | Clean, high-level overview |
| `chartlabel.py` | Basic chart with task labels inside each bar | Detailed task visualization |
| `dates.py` | Enhanced chart with more date labels | Precise timeline tracking |
| `dateslabel.py` | Comprehensive chart with both extra dates and labels | Complete project visibility |

## Quick Start

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd gantt-chart-generator

# Install dependencies
pip install pandas plotly
```
### Usage
After install you can run the script with
```bash
python chart.py input.csv
```
### Extra Options
There are a few extra command line options you can include
| Argument | Description |
|--------|-------------|
|`--dark`| Generates the graph in dark mode |
|`30` | Height of the rows is 30% bigger, you can use any integer|

So you can do 
```bash
python chart.py input.py 50
```
To get a chart with 50% larger rows!
