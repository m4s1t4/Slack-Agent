# Slack AI Chatbot 🤖

An intelligent Slack chatbot with local AI capabilities using Ollama. Integrates Trello/GitHub, RAG, and custom tools.

![Architecture Diagram](https://via.placeholder.com/800x400.png?text=Architecture+Diagram)

## ✨ Main Features
- **Local AI** with Ollama (llama3.2 model)
- **Trello** Integration (board management)
- **GitHub** repository exploration
- **RAG** System (Retrieval Augmented Generation)
- Persistent conversation history
- Tools system with function calling

## 🛠️ Technology Stack
- **AI Engine**: Ollama (Local LLM)
- **Framework**: Slack Bolt
- **Tools**:
  - Trello API (py-trello)
  - PyGithub for GitHub interactions
  - LangChain for RAG pipelines
- **Storage**: ChromaDB (vectors)

## 🚀 Quick Installation

```bash
# Clone and setup environment
git clone https://github.com/your-repository/slack-ai-chatbot.git
cd slack-ai-chatbot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# REQUIRED environment variables
export SLACK_BOT_TOKEN="xoxb-your-token"
export SLACK_APP_TOKEN="xapp-your-token"
export TRELLO_API_KEY="your-key"
export TRELLO_TOKEN="your-token"
export BOARD_ID="your-board-id"
export GITHUB_TOKEN="ghp-your-token"

# Start Ollama server (in separate terminal)
ollama serve

# Run application
python3 app.py
```

## 🧠 AI Configuration
```python
# From ai/providers/openai.py
base_url = "http://localhost:11434/v1/"  # Ollama local server
api_key = "ollama"  # Special value for authentication
model = "llama3.2"  # Custom fine-tuned model
```

## 🔧 Project Structure
```
├── app.py                 # Main entry point
├── listeners/             # Slack event handlers
├── ai/
│   ├── providers/        # AI provider implementations
│   ├── tools/            # Integration tools
│   └── constants.py      # AI configurations
├── data/
│   ├── knowledge/        # Knowledge base for RAG
│   └── vectors/          # Vector storage
├── state_store/          # User preferences
└── tests/                # Integration tests
```

## 🛠️ Tools System
Main implemented functions:
```python
# From ai/providers/openai.py
{
    "get_trello_board_info": Trello board management,
    "add_card_to_list": Add cards to lists,
    "list_user_repos": List GitHub repositories,
    "query_rag": RAG system queries,
    "show_commit_history": Commit history
}
```

## 📌 Key Dependencies (requirements.txt)
```
ollama          # Local LLM server
slack_bolt      # Slack Framework
py-trello       # Trello Integration
PyGithub        # GitHub Interaction
langchain-ollama # Local models
langchain-chroma # Vector storage
```

## ⚠️ Important Notes
1. Requires Ollama running (`ollama serve`)
2. RAG knowledge files go in `data/knowledge/`
3. Conversation history is kept in memory
4. Credentials must be environment variables
5. Uses try/except with detailed error messages

## 📄 License
MIT License - See [LICENSE](LICENSE)
