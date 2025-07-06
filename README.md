# 🎭 LangGraph Joke Bot

A fun, interactive joke bot built with LangGraph that demonstrates agentic state flow without traditional LLMs. The bot can fetch jokes in multiple languages and categories, with support for both OpenAI GPT and pyjokes as fallback.

## ✨ Features

- **Interactive Menu System**: Easy-to-use command-line interface with emoji-rich menus
- **Multiple Languages**: Support for English, German, and Spanish jokes
- **Various Categories**: Choose from neutral, Chuck Norris, or all categories
- **Joke History**: Track all jokes from your session with reset functionality
- **OpenAI Integration**: Uses ChatGPT for personalized, comedian-style jokes
- **Fallback System**: Automatically falls back to pyjokes if OpenAI API fails
- **State Management**: Powered by LangGraph for robust state flow management

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (optional, will use pyjokes as fallback)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd langgraph-joke-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up OpenAI API key** (required)
    in a .env file:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   
   Or set it directly in your code:
   ```python
   api_key = "your-api-key-here"
   ```

### Usage

Run the bot with:
```bash
python main.py
```

## 🎮 How to Use

Once you start the bot, you'll see an interactive menu with the following options:

- **[n] 🎭 Next Joke**: Get a new joke in your selected category and language
- **[c] 📂 Change Category**: Switch between different joke categories
- **[l] 🌐 Change Language**: Switch between supported languages
- **[r] 🔁 Reset Joke History**: Clear your joke history counter
- **[q] 🚪 Quit**: Exit the bot

### Available Categories

- **🎯 Neutral**: Clean, family-friendly jokes
- **🥋 Chuck**: Chuck Norris jokes
- **🌟 All**: Random jokes from all categories
- **🌟 Programmer**: Programmer jokes
- **🌟 Dad**: Dad jokes

### Supported Languages

- **🇺🇸 English (en)**
- **🇩🇪 German (de)**
- **🇪🇸 Spanish (es)**

## 🏗️ Architecture

The bot is built using **LangGraph**, a library for building stateful, multi-agent applications. Key components include:

### State Management
- **JokeState**: Pydantic model managing bot state including jokes history, category, language, and user choices
- **Custom Reducer**: Handles joke list operations (append vs reset) based on user actions

### Node Functions
- **show_menu**: Displays interactive menu and captures user input
- **fetch_joke**: Retrieves jokes from OpenAI API or pyjokes fallback
- **update_category**: Handles category selection
- **change_language**: Manages language switching
- **reset_jokes**: Clears joke history
- **exit_bot**: Graceful shutdown

### Flow Control
- **Conditional Routing**: Routes user choices to appropriate nodes
- **State Transitions**: Manages flow between different bot states
- **Error Handling**: Robust error handling with fallback mechanisms

## 🔧 Configuration

### OpenAI Settings
The bot uses the following OpenAI configuration:
- **Model**: `chatgpt-4o-latest`
- **Max Tokens**: 400
- **Temperature**: 0.7 (for creative but controlled responses)

## 📦 Dependencies

The bot requires the following packages (see `requirements.txt`):

- `langgraph`: State graph management
- `pydantic`: Data validation and state modeling
- `openai`: OpenAI API integration
- `pyjokes`: Fallback joke provider
- `typing-extensions`: Enhanced type hints

## 🛠️ Development

### Project Structure
```
langgraph-joke-bot/
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── .env                # Environment variables (optional)
```

### Extending the Bot

To add new features:

1. **New Languages**: Add language codes to the `languages` list in `change_language()`
2. **New Categories**: Extend the `categories` list in `update_category()`
3. **New Nodes**: Create new node functions and add them to the workflow
4. **Custom Reducers**: Modify the `joke_list_reducer()` for different state behaviors

### Error Handling

The bot includes comprehensive error handling:
- **API Failures**: Automatic fallback to pyjokes
- **Invalid Input**: Input validation with retry prompts
- **Network Issues**: Graceful degradation
- **State Corruption**: Robust state management

## 🎯 Example Session

```
🎉============================================================🎉
    WELCOME TO THE LANGGRAPH JOKE BOT!
    This example demonstrates agentic state flow with LLMs
============================================================

🎭 Menu | Category: NEUTRAL | Jokes: 0
--------------------------------------------------
Pick an option:
[n] 🎭 Next Joke  [c] 📂 Change Category [r] 🔁 Reset Joke History  [l]  🌐  Change Language  [q] 🚪 Quit
User Input: n

😂 Why don't scientists trust atoms? Because they make up everything!

============================================================

🎭 Menu | Category: NEUTRAL | Jokes: 1
--------------------------------------------------
```

## 🤝 Contributing

Contributions are welcome! Please feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph) for state management
- Powered by [OpenAI](https://openai.com) for AI-generated jokes
- Fallback jokes provided by [pyjokes](https://github.com/pyjokes/pyjokes)
- Emoji support for enhanced user experience

---

**Happy Joking! 🎭✨**