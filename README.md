
# Development Tutor Agent

The **Development Tutor Agent** is an AI-powered virtual assistant designed to help developers solve technical problems and provide assistance on programming topics. The agent consists of specialized sub-agents, such as the **Researcher**, which performs web searches to ensure that the information provided is always up-to-date. This project was developed using Google ADK (Agent Development Kit).

##  What is ADK?

The Agent Development Kit (ADK) is a flexible and modular framework for developing and deploying AI agents. ADK can be used with popular LLMs and open-source generative AI tools, and was designed with a focus on integration with the Google ecosystem and Gemini models. ADK makes it easy to get started with simple agents powered by Gemini models and Google AI tools, while providing the control and structure needed for more complex agent architectures and orchestrations.

Learn more: https://google.github.io/adk-docs/

## Features

- **Researcher**: Performs real-time web searches on topics related to development and programming, ensuring that responses are always based on the most recent information.
- **Development Tutor**: Instructs the user, guiding them on a technical learning journey focused on programming languages, frameworks, and tools.

## Architecture

The project consists of a set of agents that collaborate with each other to provide complete and detailed responses. The main agent's workflow includes:

1. **Greetings**: The agent introduces itself to the user in a playful manner and collects information about the request.
2. **Search**: The agent performs a real-time search using the **Researcher** sub-agent to ensure that the information provided is up-to-date.
3. **Tone**: Adjusts the response tone to a technical, friendly, and jovial style.
4. **Key Constraints**: Responses aimed at solving problems in a practical and efficient manner.

## How to Run

### Prerequisites

- Python 3.8 or higher
- Dependencies listed in the `requirements.txt` file

### Execution Steps

1. Clone the repository:

   ```bash
   git clone git@github.com:ju4nv1e1r4/agents-with-adk.git
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv env
   source env/bin/activate  # Linux/macOS
   env\Scripts\activate     # Windows
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure the environment variables in the `.env` file:

   ```bash
      # If using Gemini via Google AI Studio
    GOOGLE_GENAI_USE_VERTEXAI="False"
    GOOGLE_API_KEY="paste-your-actual-key-here"

    # # If using Gemini via Vertex AI on Google Cloud
    # GOOGLE_CLOUD_PROJECT="your-project-id"
    # GOOGLE_CLOUD_LOCATION="your-location" #e.g. us-central1
    # GOOGLE_GENAI_USE_VERTEXAI="True"

   ```

   > If you are using Google Cloud, uncomment and configure the appropriate variables for Vertex AI.

5. To run the agent in the terminal, use the following command:

   ```bash
   adk run development_tutor/
   ```

6. To run the web interface locally:

   ```bash
   adk web
   ```

   Access the application at [http://localhost:8000](http://localhost:8000).

## How It Works

1. The **Development Tutor** starts a conversation with the user, asking how it can help.
2. The **Researcher** sub-agent performs a web search to ensure that responses are always up-to-date.
3. The **Development Tutor** provides responses with examples and detailed explanations.
4. The agent adjusts its tone to be technical, friendly, and jovial, ensuring a light and informative learning experience.

Screenshots of the system in action can be found in the img/ directory.

## Project Structure

```
.
├── development_tutor/
│   ├── agent.py              # main agent
│   ├── prompt.py             # Prompt base for main agent
│   ├── shared_libraries/     # Constants
│   ├── sub_agents/           # SubAgents
│   │   └── researcher/       # Researcher Agent
│   │       ├── agent.py
│   │       ├── prompt.py
│   └── tools/                # Tools
│       └── search.py         # Google Search Tool
└── README.md
```

## Deployment

This project includes a complete CI/CD pipeline using GitHub Actions for automated testing and deployment to Google Cloud Run.

### Quick Deploy

**For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)**

1. **Set up Google Cloud**: Create service account and enable APIs
2. **Configure GitHub Secrets**: Add GCP credentials to repository secrets
3. **Push to deploy**:
   - Push to `staging` branch → deploys to staging environment
   - Push to `main` branch → deploys to production
   - Create tag `v*.*.*` → deploys and creates GitHub release

### Local Development

Use the provided Makefile for common tasks:

```bash
make setup      # Initial setup (install dependencies, create .env template)
make web        # Run web interface locally
make check-all  # Run all CI checks locally (lint, security, test)
make format     # Format code with black and isort
```

### CI/CD Workflows

- **Continuous Integration**: Runs on every push - linting, security scans, tests
- **Staging Deployment**: Auto-deploys when pushing to `staging` or `develop` branches
- **Production Deployment**: Auto-deploys when pushing to `main` or creating version tags

For complete documentation, see `.github/workflows/README.md`

---

This project was developed with a focus on helping developers from all areas find quick and accurate solutions to their programming problems.
