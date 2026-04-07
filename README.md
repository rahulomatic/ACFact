Autonomous Content Factory (ACFact)

Project Title
Autonomous Content Factory using AI Agents

---

The Problem

Creating high-quality content consistently is time-consuming, resource-intensive, and difficult to scale. Individuals and organizations often struggle to maintain content quality while increasing production across multiple platforms.

---

The Solution

The Autonomous Content Factory (ACFact) solves this problem by using a system of AI agents that collaboratively generate content.

Instead of relying on a single AI model, the system breaks down content creation into multiple stages such as idea generation, drafting, refinement, and formatting. Each stage is handled by a specialized AI agent, creating a pipeline that mimics a real-world content production workflow.

This modular and agent-based approach enables:
- Scalable content generation
- Improved quality through task specialization
- Reduced manual effort
- Flexibility to customize workflows

#Tech Stack

Programming Language
- Python

Frameworks & Libraries
- Flask
- LangChain (or similar agent orchestration tools)
- python-dotenv

AI APIs
- Claude API (Anthropic)

Database
- SQLite

Frontend
- HTML
- Bootstrap

Tools
- Git & GitHub
- VS Code

Setup Instructions (Quick Start)

Clone the Repository
git clone https://github.com/rahulomatic/ACFact.git
cd ACFact

Create Virtual Environment
python -m venv venv

Activate Virtual Environment

Windows
venv\Scripts\activate

Mac/Linux
# source venv/bin/activate

Install Dependencies
pip install -r requirements.txt

Configure Environment Variables
# Create a .env file in the root directory and add:
# ANTHROPIC_API_KEY=your_api_key_here

Run the Application
python app.py

Open in Browser
# http://127.0.0.1:5000/
