# 🌟 Allam Challenge 2024 🌟

This project demonstrates the capabilities of SDAIA's Arabic language model, **Allam**, in understanding and reasoning in Arabic through an interactive poetry showcase. The challenge highlights Allam's ability to mimic Arabic poets, analyze verses, and engage in poetic debates, showcasing advanced natural language processing in Arabic.

## 📝 Project Overview

The application offers three main features centered around Arabic poetry:

1. **📜 Arabic Poetry Generation**: 
   - Select a poet and a theme, and Allam generates original verses, mimicking the poet's style with the chosen theme.
   
2. **🔍 Poetry Analysis and Critique**: 
   - Using machine learning and Allam's reasoning, this feature analyzes user-provided verses. It detects poetic elements like meter and rhyme, offering critiques and insights into the verse's artistry.

3. **⚔️ Poetic Debate**:
   - Engage in a poetic duel with two poets, each represented by Allam. A third "judge" agent (also powered by Allam) scores each round, ultimately declaring a winner based on the verses generated around a chosen theme.

## 🚀 Features

- **Automated Setup**: `start.sh` script handles directory creation, model downloading, and Docker container setup.
- **Dockerized Environment**: The project runs in a Dockerized setup for easy deployment and consistency.

## 📋 Prerequisites

Before running this project, make sure you have:
- 🐳 Docker
- 🐳 Docker Compose
- 🐍 Python 3.x

## 🛠️ How to Run the Project

1. **Clone the Repository**:

    ```bash
    git clone Allam-challenge-2024
    cd Allam-challenge-2024
    ```

2. **Make the `start.sh` Script Executable**:

    Ensure the `start.sh` file has execution permissions.

    ```bash
    chmod +x start.sh
    ```

3. **Run the `start.sh` Script**:

    This script will:
    - 📂 Create the required `models` folder.
    - ⬇️ Download the `paraphrase-multilingual-mpnet-base-v2` model from SentenceTransformers.

    ```bash
    ./start.sh
    ```

4. **Start the Frontend**:

    Navigate to the frontend folder and run:

    ```bash
    cd frontend
    npm ci
    npm run start
    ```

5. **Optional: Manually Start Docker Compose**:

    If you prefer to control Docker Compose yourself, use:

    ```bash
    docker compose up --build
    ```

---
