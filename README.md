# nba-prop-prediction-model
An NBA player props prediction tool using Python and nba_api to calculate averages and project stats.
# NBA Prop Prediction Tool 🏀

This Python script fetches NBA player game logs using the `nba_api` library and calculates projected stats for points, rebounds, assists, and their combinations. It’s ideal for NBA player props research, fantasy sports, or general analysis.

---

## 🚀 Features

- **Player Name Search**:
  - Supports partial name searches (e.g., "Tatum" for Jayson Tatum).
  - Filters results to show **only active NBA players** for cleaner results.
  - Handles common names (e.g., "Brown") by limiting the search to manageable results.

- **Stat Projections**:
  - Calculates player averages for:
    - Points (PTS)
    - Rebounds (REB)
    - Assists (AST)
    - Combo Stats: P+R, P+A, R+A, P+R+A
  - Based on the last **N games** (user-specified, default = 5).

- **Data Export**:
  - Saves projected stats to a CSV file for easy analysis.

---

## 🛠 Installation

### Prerequisites
Ensure you have Python 3.7+ installed. Install the required libraries using `pip`:

```bash
pip install nba_api pandas
