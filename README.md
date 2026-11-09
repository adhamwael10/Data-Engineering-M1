# NYC Housing & Transportation Analytics Explorer

## Project Overview

The NYC Housing & Transportation Analytics Explorer is a data engineering project that integrates NYC construction permit records with motor vehicle collision records.

The project explores geographic and temporal patterns across New York City using ZIP codes and years. It provides an interactive dashboard for filtering, visualizing, and exploring relationships between construction activity and traffic collisions.

## Team Members

| Name           | Student ID |
| -------------- | ---------: |
| Adham Wael     |   16005914 |
| Habiba Ahmed   |   16010159 |
| Youssef Khaled |   16007290 |
| Eyad Elmoataz  |   16007389 |
| Hamza Feras    |   16002652 |

## Datasets

**1. DOB NOW: Build Approved Permits**

- Source: [NYC Open Data](https://data.cityofnewyork.us/resource/rbx6-tga4.csv)
- Dataset ID: `rbx6-tga4`
- Category: `work_type`

**2. Motor Vehicle Collisions**

- Source: [NYC Open Data](https://data.cityofnewyork.us/resource/h9gi-nx95.csv)
- Dataset ID: `h9gi-nx95`
- Category: `contributing_factor_vehicle_1`

## Data Integration

The datasets are cleaned and aggregated using:

- Geographic key: ZIP code
- Temporal key: Year
- Integration method: Outer join

The resulting integrated dataset contains:

- 1,747 rows
- 5 columns

Additional category-level datasets:

- Housing category dataset: 9,669 rows
- Transportation category dataset: 8,766 rows

## Team Contributions

The project was completed collaboratively, with each team member responsible for specific aspects of the data engineering workflow and dashboard development.

| Team Member | Student ID | Contributions |
|---|---:|---|
| **Adham Wael** | 16005914 | Website and dashboard development, frontend design, interactive filters, dashboard callbacks, visual integration, map implementation, and website testing. |
| **Habiba Ahmed** | 16010159 | Housing dataset research, data collection, exploratory data analysis (EDA), and housing data cleaning. |
| **Youssef Khaled** | 16007290 | Transportation dataset research, data collection, exploratory data analysis (EDA), and transportation data cleaning. |
| **Eyad Elmoataz** | 16007389 | Data integration using ZIP codes and years, post-integration cleaning, and data validation. |
| **Hamza Feras** | 16002652 | Research question development, analytical visualizations, interpretation of findings, and project documentation. |

All team members contributed to reviewing the project results and ensuring that the final deliverables met the milestone requirements.

## Project Structure

```text
Data-Engineering-M1/
│
├── assets/
│   └── style.css
│
├── callbacks/
│   ├── dashboard_callbacks.py
│   └── search_callbacks.py
│
├── components/
│   ├── charts.py
│   ├── filters.py
│   ├── insights.py
│   ├── kpi_cards.py
│   ├── layout.py
│   └── map.py
│
├── Data/
│   ├── integrated_data.csv
│   ├── housing_category_data.csv
│   ├── transport_category_data.csv
│   └── nyc_zip_codes.geojson
│
├── Notebook/
│   └── Data_Engineering_Milestone_1.ipynb
│
├── utils/
│
├── app.py
└── requirements.txt
```

## Dashboard Features

- Interactive borough and year filters
- Housing work-type filtering
- Transportation contributing-factor filtering
- Natural-language search
- Generate Report functionality
- Interactive charts and visualizations
- NYC ZIP-code geographic map
- Automated analytical insights
- Integrated dataset explorer
- Data story section

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/adhamwael10/Data-Engineering-M1.git
cd Data-Engineering-M1
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the dashboard

```bash
python app.py
```

Open the local address displayed in the terminal.

## Notebook

The complete data engineering workflow is available in:

`Notebook/Data_Engineering_Milestone_1.ipynb`

It includes dataset exploration, cleaning, integration, validation, visualizations, and CSV exports.

## Limitations

The integrated dataset is aggregated at ZIP-code and year level. The analysis identifies descriptive relationships and patterns, not causal relationships between construction activity and traffic collisions.

## Repository

[GitHub — Data-Engineering-M1](https://github.com/adhamwael10/Data-Engineering-M1)

## Deployment

Deployment URL: https://nyc-housing-transport-dashboard.onrender.com
