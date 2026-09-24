# Internal Marks "What-If" Simulator 🎯

> **A modern, interactive academic performance forecasting dashboard and simulation tool designed for MCA and engineering students to model external exam outcomes, project GPA/grades, analyze backlog risks, and track attendance compliance.**

---

## 📌 1. Project Overview

The **Internal Marks "What-If" Simulator** is an academic decision-support web application built with **Python**, **Streamlit**, and **Plotly**. In university assessment frameworks (such as MCA, B.Tech, and M.Tech), semester grades are determined by combining **continuous internal assessments** (midterms, assignments, lab work, attendance) and **final external university examinations**.

Before sitting for external exams, students often experience uncertainty:
* *"What is the minimum mark I need in the external exam to secure an 'A' grade?"*
* *"Am I at risk of failing or having a backlog in my weaker subjects?"*
* *"Does my attendance shortage affect my exam eligibility?"*
* *"How does a safe vs. strong performance attempt impact my overall CGPA?"*

This application solves these challenges by providing real-time mathematical simulation via sliders, instant visual feedback, target grade calculators, multi-scenario comparisons, and automated academic performance report generation.

---

## ⚠️ 2. Problem Statement

1. **Lack of Transparent Performance Forecasting**: Students typically do not know how their internal marks combine with external exam scores until official results are published months later.
2. **Backlog Surprises**: Weak subjects often catch students unprepared because they don't know the exact passing cutoff threshold in advance.
3. **Attendance Eligibility Oversights**: Many universities enforce strict attendance minimums (typically 75%). Shortages often lead to exam debarment if not caught early.
4. **Suboptimal Exam Preparation Strategy**: Without knowing target score requirements, students allocate revision time inefficiently across subjects.

---

## 💡 3. Proposed Solution

The **Internal Marks "What-If" Simulator** empowers students with an interactive, data-driven dashboard:
* **Dynamic Simulation Sliders**: Adjust projected external exam scores and watch total scores, percentages, and letter grades update instantly without page reloads.
* **Target Grade Solver**: Select any desired letter grade (`O`, `A+`, `A`, `B+`, `B`, `C`) and discover the exact marks required in the external paper, with automatic detection of mathematically impossible targets.
* **Attendance Risk Detection**: Prominent automated warnings flagging subjects falling below the 75% attendance threshold.
* **Multi-Scenario Comparison**: Compare outcomes across **Safe (40%)**, **Average (60%)**, **Strong (80%)**, and custom saved scenarios side-by-side.
* **Visual Analytics**: Interactive Plotly charts for subject percentages, grade distributions, internal vs. external marks splits, and grade boundary gauges.
* **Multi-Format Export**: Download formal **PDF academic scorecards**, formatted **Excel workbooks**, and **CSV datasets**.

---

## ✨ 4. Key Features

| Category | Highlights |
|---|---|
| **📊 Executive Dashboard** | Real-time KPI summary cards (Projected %, Grade, Passing count, Backlog count, Attendance risk count, CGPA forecast). |
| **🎛️ What-If Simulator** | Real-time sliders (0 to External Max) for each subject with instant calculation of Total Marks, Percentage, Grade, and Next-Grade distance. Quick batch presets: Safe (40%), Average (60%), Strong (80%), Maximum (100%). |
| **🎯 Target Grade Calculator** | Reverse calculation of the exact minimum external marks needed to achieve a target letter grade, with feasibility status and full target matrix. |
| **⚖️ Scenario Comparison** | Benchmark attempt comparison with interactive grouped bar charts and matrix tables, plus SQLite persistence for custom scenario libraries. |
| **📚 Subject Setup** | Complete CRUD interface to add, edit, delete subjects, and restore standard MCA curriculum sample data with strict input validation. |
| **🔍 Weakest Subject Diagnosis** | Automatic identification of the lowest-performing subject with targeted academic advice and marks required to avoid backlogs. |
| **⏱️ Attendance Compliance** | Automated detection of attendance below university rules (default 75%) with clear warnings and shortfall analysis. |
| **📥 Report Generation** | Instant export to official PDF reports (using ReportLab), multi-sheet Excel files (using OpenPyXL), and raw CSV datasets. |

---

## 🛠️ 5. Technology Stack

* **Language**: Python 3.10+
* **Frontend Framework**: [Streamlit](https://streamlit.io/) (v1.30.0+)
* **Data Processing**: [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
* **Data Visualizations**: [Plotly Express & Graph Objects](https://plotly.com/python/), [Matplotlib](https://matplotlib.org/)
* **Local Persistence**: SQLite3 (Transactional ACID storage)
* **Report Generation**:
  * PDF: [ReportLab](https://www.reportlab.com/)
  * Excel: [OpenPyXL](https://openpyxl.readthedocs.io/)
* **Styling**: Vanilla CSS3 custom design system with Plus Jakarta Sans typography, card-based glassmorphism, and responsive layouts.

---

## 📁 6. Project Architecture

```text
internal-marks-what-if-simulator/
│
├── app.py                      # Main Streamlit application orchestrator
├── requirements.txt            # Python package dependencies
├── README.md                   # Comprehensive project documentation
├── .gitignore                  # Git tracking exclusion rules
│
├── data/                       # Local SQLite database directory
│   ├── .gitkeep
│   └── simulator.db            # SQLite database file (auto-generated)
│
├── modules/                    # Core business logic & calculation services
│   ├── __init__.py
│   ├── calculations.py         # Pure academic math, grading scales, target solver
│   ├── database.py             # SQLite persistence, CRUD, scenario management
│   ├── charts.py               # Plotly interactive visualization engine
│   ├── recommendations.py      # Rule-based academic advisory engine
│   └── export.py               # PDF, Excel, and CSV export generators
│
├── components/                 # Streamlit UI page components
│   ├── __init__.py
│   ├── sidebar.py              # Navigation menu, student profile, evaluation rules
│   ├── dashboard.py            # Primary executive KPI dashboard & scorecards
│   ├── subject_setup.py        # Curriculum management (Add/Edit/Delete/Reset)
│   ├── simulator.py            # Interactive sliders, target solver, scenario comparison
│   └── reports.py              # Export downloads & preview cards
│
└── assets/
    └── custom.css              # Custom dashboard CSS design system
```

---

## 🎓 7. University Grading Scale Reference

The simulator uses standard university grading boundaries (configurable via sidebar):

| Percentage Range | Letter Grade | Grade Point | Performance Level | Status |
|:---:|:---:|:---:|---|:---:|
| **90.0% – 100%** | **O** | 10 | Outstanding | PASS |
| **80.0% – 89.9%** | **A+** | 9 | Excellent | PASS |
| **70.0% – 79.9%** | **A** | 8 | Very Good | PASS |
| **60.0% – 69.9%** | **B+** | 7 | Good | PASS |
| **50.0% – 59.9%** | **B** | 6 | Above Average | PASS |
| **40.0% – 49.9%** | **C** | 5 | Pass | PASS |
| **0.0% – 39.9%** | **F** | 0 | Fail / Backlog | **FAIL** |

*Passing threshold is set to 40.0% by default and is dynamically adjustable.*

---

## 🚀 8. Installation & Setup

### Prerequisites
* Python 3.10, 3.11, or 3.12 installed on your machine.
* Git installed.

### 1. Clone the Repository
```bash
git clone https://github.com/jatavscript/what-if-ostf.git
cd what-if-ostf
```

### 2. Create a Virtual Environment (Recommended)
On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

On macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Required Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python -m streamlit run app.py
```

The application will start and open automatically in your browser at:
`http://localhost:8501`

---

## 📸 9. Application Screenshots & Interface

* **Executive Dashboard**: Real-time KPI scorecards, grade distributions, and performance gauges.
* **Interactive Simulator**: Real-time sliders with dynamic grade badges and progress bars.
* **Target Grade Matrix**: Feasibility indicators and required score calculations.
* **Multi-Scenario Comparison**: Bar charts comparing safe, average, and strong exam attempts.
* **Export Center**: One-click download of styled PDF reports and Excel workbooks.

---

## 🔮 10. Future Enhancements

* [ ] Multi-semester SGPA & cumulative CGPA trend tracking.
* [ ] Multi-user authentication & cloud database sync.
* [ ] Subject credit-weighting system (e.g., 3-credit vs. 4-credit courses).
* [ ] What-if Monte Carlo stochastic simulation for probabilistic grade estimation.
* [ ] Direct university portal syllabus & marks integration via API.

---

## 👨‍💻 11. Author & Academic Context

* **Project Title**: Internal Marks "What-If" Simulator
* **Developed For**: MCA Academic Mini-Project Demonstration & Evaluation
* **Developer**: Ajay Jatav ([@jatavscript](https://github.com/jatavscript))
* **Email**: [ajayjatav6282@gmail.com](mailto:ajayjatav6282@gmail.com)
* **GitHub Repository**: [what-if-ostf](https://github.com/jatavscript/what-if-ostf)

---

## 📄 12. License

This project is licensed under the **MIT License** — feel free to use and adapt it for academic and educational purposes.
