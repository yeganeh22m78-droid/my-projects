# Multi-View Python Application

A comprehensive Python GUI application featuring user authentication, matrix calculations, and 3D visualizations.

## Features

- **User Authentication**: Secure login and registration system with password hashing
- **Matrix Calculator**: Perform addition, subtraction, and multiplication on 3x3 matrices
- **3D Visualizations**:
  - Rotating square in 3D space
  - Rotating cube with proper edge connections
  - Rocket launch simulation to the moon
- **Modern UI**: Dark theme with intuitive navigation

## Requirements

- Python 3.x
- tkinter (built-in)
- numpy
- matplotlib
- pygame (for audio in rocket simulation)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yeganeh22m78-droid/my-projects.git
cd my-projects
```

2. Install dependencies:
```bash
pip install numpy matplotlib pygame
```

## Usage

Run the application:
```bash
python "my project.py"
```

### First Time Setup
1. Register a new account or use existing credentials
2. Access different features from the main menu

### Features Guide
- **Login/Register**: Create account or sign in
- **Matrix Calculator**: Enter values in the 3x3 grids and select operation
- **3D Square**: Watch the animated rotating square
- **3D Cube**: View the rotating cube with connected edges
- **Rockets**: Interactive rocket launch simulation

## Database

The application uses SQLite for user data storage. The database file (`users.db`) is automatically created and should not be committed to version control.

## Contributing

Feel free to submit issues and enhancement requests!