from typing import Annotated, List, Union, Literal
from pydantic import BaseModel
import os
from pyjokes import get_joke
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from langchain_core.runnables.graph import MermaidDrawMethod 
from IPython.display import Image, display
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

openai = OpenAI(
    api_key=OPENAI_API_KEY
)




# define state

class Joke (BaseModel):
    text: str
    category: str
    language: str

#define custom reducer
def joke_list_reducer(current_jokes: List[Joke], update: Union[Joke, List[Joke], str]) -> List[Joke]:
    """
    Custom reducer for joke list that:
    - Appends new jokes normally
    - Clears the list if update is "reset" or if it's a reset signal
    """
    
    # If it's a reset signal, clear the list
    if update == "reset" or update == "r":
        return []
    
    # If it's a single joke, append it
    if isinstance(update, Joke):
        return current_jokes + [update]
    
    # For any other case, keep the current list
    return current_jokes

class JokeState (BaseModel):
    """
    Represents the evolving state of the joke bot
    """

    jokes: Annotated[List[Joke], joke_list_reducer] = []
    # jokes: Annotated[List[Joke], add] = []  # original jokes before custom reducer Using built-in add operator
    jokes_choice: Literal["n", "c", "q", "l", "r"] = "n" # next, change, quit
    category: str = "neutral"
    language: str = "en"
    quit: bool = False



# utilities

def get_user_input(prompt: str) -> str:
    return input(prompt).strip().lower()


def print_joke(joke: Joke):
    """Print a joke with nice formatting."""
    # print(f"\n📂 CATEGORY: {joke.category.upper()}\n")
    print(f"\n😂 {joke.text}\n")
    print("=" * 60)


def print_menu_header(category: str, total_jokes: int):
    """Print a compact menu header."""
    print(f"🎭 Menu | Category: {category.upper()} | Jokes: {total_jokes}")
    print("-" * 50)


def print_category_menu():
    """Print a nicely formatted category selection menu."""
    print("📂" + "=" * 58 + "📂")
    print("    CATEGORY SELECTION")
    print("=" * 60)

def print_language_menu():
    """Print a nicely formatted language selection menu."""
    print(" 🌐 " + "=" * 58 + " 🌐 ")
    print("    LANGUAGE SELECTION")
    print("=" * 60)

def graph_visualiser(graph):
    """
    Visualize the graph using Mermaid with Pyppeteer method
    """
    try:
        # Correct syntax for using MermaidDrawMethod.PYPPETEER
        display(Image(graph.get_graph().draw_mermaid_png(
            draw_method=MermaidDrawMethod.API
        )))
        
    except Exception as e:
        print(f"Error generating graph visualization: {e}")
        print("Falling back to text representation...")
        
        # Fallback to text-based mermaid diagram
        try:
            print("\n📊 === MERMAID DIAGRAM (TEXT) ===")
            print(display(Image(graph.get_graph().draw_mermaid())))
        except Exception as fallback_error:
            print(f"Fallback also failed: {fallback_error}")


# ===================
# Define Nodes
# ===================


def show_menu(state: JokeState) -> dict:
    print_menu_header(state.category, len(state.jokes))
    print("Pick an option:")
    user_input = get_user_input(
        "[n] 🎭 Next Joke  [c] 📂 Change Category [r] 🔁 Reset Joke History  [l]  🌐  Change Language  [q] 🚪 Quit\nUser Input: "
    )
    while user_input not in ["n", "c", "q", "l", "r"]:
        print("❌ Invalid input. Please try again.")
        user_input = get_user_input(
            "[n] 🎭 Next Joke  [c] 📂 Change Category [r] 🔁 Reset Joke History [l]  🌐  Change Language  [q] 🚪 Quit\n    User Input: "
        )
    return {"jokes_choice": user_input}

# new fetch joke with api call

def critic(state: JokeState, joke_text) -> dict:
    system_prompt = (
        "You are an experienced comedian critic with 25 years of criticizing standup comedy experience. "
        "You make sure the jokes are warm, friendly, and genuinely funny. "
        "You make sure the joke is easily understood."
        "you respond with a yes if the joke fits your criteria and with a no if the joke is not approved."
        "The end goal is to make sure the user doesnt get a bad joke."
    )
    
    user_prompt = (
        f"Please criticize this joke : {joke_text} "
    )
    
    try:
        response = openai.chat.completions.create(
            model='chatgpt-4o-latest',
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=400,
            temperature=0.7
        )
        
        approved = response.choices[0].message.content.strip()
        approval = "Yes" in approved
        if approval:
            new_joke = Joke(text=joke_text, category=state.category, language=state.language)
            print_joke(new_joke)

            return {"jokes": new_joke}
        else:
            print(f"joke not approved, writing another joke")
            return writer(state)
   
        
    except Exception as e:        
        print(f"error analyzing joke")


def writer(state: JokeState) -> dict:
    
    # Language mapping for better prompts
    language_names = {
        "en": "English",
        "de": "German", 
        "es": "Spanish"
    }
    
    # Category descriptions
    category_descriptions = {
        "neutral": "clean, family-friendly",
        "chuck": "Chuck Norris style",
        "all": "any category",
        "programmer": "programmer jokes",
        "dad": "dad jokes"
    }
    
    language_name = language_names.get(state.language, state.language)
    category_desc = category_descriptions.get(state.category, state.category)
    
    system_prompt = (
        "You are an experienced comedian with 25 years of standup comedy experience. "
        "Your specialty is crafting jokes that are warm, friendly, and genuinely funny. "
        "You avoid clichés and buzzwords, focusing on original humor that makes people laugh."
        "You avoid using bullet points or asterisks."
        "Don't highlight any part of the response text using asterisks or anything. keep the response as a pure string."
        "Keep it under 50 words and make it entertaining and lighthearted."
    )
    
    user_prompt = (
        f"Please tell me a {category_desc} joke in {language_name}. "
    )
    
    try:
        response = openai.chat.completions.create(
            model='chatgpt-4o-latest',
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=400,
            temperature=0.7
        )
        
        joke_text = response.choices[0].message.content.strip()
        return critic(state, joke_text)
        
    except Exception as e:        
        fallback_joke_text = get_joke(language=state.language, category=state.category)
        new_joke = Joke(text=fallback_joke_text, category=state.category, language=state.language)
        print_joke(new_joke)
        
        return {"jokes": new_joke}


def reset_jokes(state: JokeState) -> dict:
    """
    reset the joke history
    """
    print(f"\n🔄 Joke history successfully cleared.\n")
    return {"jokes": "reset"} # i'm using the default overwrite reducer


def update_category(state: JokeState) -> dict:
    categories = ["neutral", "chuck", "all", "programmer", "dad"]
    print_category_menu()

    for i, cat in enumerate(categories):
        emoji = "🎯" if cat == "neutral" else "🥋" if cat == "chuck" else "🌟"
        print(f"    {i}. {emoji} {cat.upper()}")

    print("=" * 60)

    try:
        selection = int(get_user_input("    Enter category number: "))
        if 0 <= selection < len(categories):
            selected_category = categories[selection]
            print(f"    ✅ Category changed to: {selected_category.upper()}")
            return {"category": selected_category}
        else:
            print("    ❌ Invalid choice. Keeping current category.")
            return {}
    except ValueError:
        print("    ❌ Please enter a valid number. Keeping current category.")
        return {}
    
def change_language(state: JokeState) ->  dict:
    languages = ["en", "de", "es"]
    print_language_menu()

    for i, lang in enumerate(languages):
        print (f" {i}. 🌟 {lang.upper()}")
    print ("=" * 60)

    try:
        selection = int(get_user_input("    Enter language number: "))
        if 0 <= selection < len(languages):
            selected_language = languages[selection]
            print(f"    ✅ Language changed to: {selected_language.upper()}")
            return {"language": selected_language}
        else:
            print("    ❌ Invalid choice. Keeping current language.")
            return {}
    except ValueError:
        print("    ❌ Please enter a valid number. Keeping current language.")
        return {}


def exit_bot(state: JokeState) -> dict:
    print("\n" + "🚪" + "=" * 58 + "🚪")
    print("    GOODBYE!")
    print("=" * 60)
    return {"quit": True}


def route_choice(state: JokeState) -> str:
    """
    Router function to determine the next node based on user choice.
    Keys must match the target node names.
    """
    if state.jokes_choice == "n":
        return "writer"
    elif state.jokes_choice == "c":
        return "update_category"
    elif state.jokes_choice == "q":
        return "exit_bot"
    elif state.jokes_choice == "l":
        return "change_language"
    elif state.jokes_choice == "r":
        return "reset_jokes"
    else:
        return "exit_bot"


# ===================
# Build Graph
# ===================


def build_joke_graph() -> CompiledStateGraph:
    workflow = StateGraph(JokeState)

    # Register nodes
    workflow.add_node("show_menu", show_menu)
    workflow.add_node("writer", writer)
    workflow.add_node("update_category", update_category)
    workflow.add_node("change_language", change_language)
    workflow.add_node("reset_jokes", reset_jokes)
    workflow.add_node("exit_bot", exit_bot)

    # Set entry point
    workflow.set_entry_point("show_menu")

    # Routing logic
    workflow.add_conditional_edges(
        "show_menu",
        route_choice,
        {
            "writer": "writer",
            "update_category": "update_category",
            "change_language": "change_language",
            "reset_jokes": "reset_jokes",
            "exit_bot": "exit_bot",
        },
    )

    # Define transitions
    workflow.add_edge("writer", "show_menu")
    workflow.add_edge("update_category", "show_menu")
    workflow.add_edge("change_language", "show_menu")
    workflow.add_edge("reset_jokes","show_menu")
    workflow.add_edge("exit_bot", END)

    return workflow.compile()


# ===================
# Main Entry
# ===================


def main():
    print("\n" + "🎉" + "=" * 58 + "🎉")
    print("    WELCOME TO THE LANGGRAPH JOKE BOT!")
    # print("    This example demonstrates agentic state flow without LLMs")
    print("    This example demonstrates agentic state flow with LLMs.")
    print("=" * 60 + "\n")

    graph = build_joke_graph()

    #print("\n📊 === MERMAID DIAGRAM ===")
    #print(graph.get_graph().draw_mermaid())
    graph_visualiser(graph)

    print("\n" + "🚀" + "=" * 58 + "🚀")
    print("    STARTING JOKE BOT SESSION...")
    print("=" * 60)

    final_state = graph.invoke(JokeState(), config={"recursion_limit": 100})

    print("\n" + "🎊" + "=" * 58 + "🎊")
    print("    SESSION COMPLETE!")
    print("=" * 60)
    print(
        f"    📈 You enjoyed {len(final_state.get('jokes', []))} jokes during this session!"
    )
    print(f"    📂 Final category: {final_state.get('category', 'unknown').upper()}")
    print("    🙏 Thanks for using the LangGraph Joke Bot!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()