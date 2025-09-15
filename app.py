import speech_recognition as sr
import pyttsx3
import webbrowser
import datetime
import os
# import requests
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
# from langchain_core.tools import tool
from langchain_groq import ChatGroq

# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.prompts import PromptTemplate
# from langchain_community.tools import Tool
from langchain_core.messages import BaseMessage,HumanMessage
from langgraph.graph.message import add_messages

from dotenv import load_dotenv

load_dotenv()





def search(command):

    groq_api_key= os.getenv("GROQ_API_KEY")
    llm = ChatGroq(groq_api_key=groq_api_key, model_name="openai/gpt-oss-120b")
    class ChatState(TypedDict):
        messages : Annotated[list[BaseMessage],add_messages]

    search_tool = DuckDuckGoSearchRun()
    tools = [search_tool]
    llm_with_tools = llm.bind_tools(tools)


    def chat_node(state:ChatState):
        """LLM node that any answer or request a tool call"""
        messages = state['messages']
        response = llm_with_tools.invoke(messages)
        return {"messages":[response]}


    tool_node = ToolNode(tools)

    graph = StateGraph(ChatState)
    graph.add_node("chat_node",chat_node)
    graph.add_node("tool_node",tool_node)
    graph.add_edge(START,"chat_node")
    graph.add_conditional_edges("chat_node",tools_condition)

    graph.add_edge("tool_node","chat_node")


    AI = graph.compile()
    out = AI.invoke({"messages":[HumanMessage(content= command)]})

    final = out["messages"][-1].content
    speak(final)


# def search(command):
#     prompt = PromptTemplate(
#         template="You are the helpful AI assistant. please understand the question of the user and give the right answer to the user in 50 words \n question -> {question}",
#         input_variables=["question"])
#     parser = StrOutputParser()
#     groq_api_key= os.getenv("GROQ_API_KEY")
#     llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama3-8b-8192")
#     chain = prompt | llm | parser
#     result = chain.invoke({"question":command})
#     print(f"AI said : {result}")
#     speak(result)


# Initialize the speech engine
engine = pyttsx3.init()

def speak(text):
    """Converts text to speech"""
    engine.say(text)
    engine.runAndWait()

def listen():
    """Captures user's voice command"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"You said: {command}")
        return command
    except sr.UnknownValueError:
        print(f"AI said : Sorry, I could not understand.")
        return ""
    except sr.RequestError:
        print(f"AI said : Could not request results. Check your internet connection.")
        return ""

def wake_word():
    """Waits for the wake word to activate the assistant"""
    while True:
        command = listen()
        if "hey assistant" in command:
            print(f"AI said : How can I help you, sir?")
            speak("How can I help you, sir?")
            handle_commands()
        elif "exit" in command or "stop" in command:
            print(f"AI said : goodbye,Sir")
            speak("goodbye,Sir")
            break
        def exit():
            pass
        break

def open_website(command):
    """Opens a website based on user's command"""
    if "open youtube" in command:
        webbrowser.open("https://www.youtube.com")
        print(f"AI said : Opening YouTube")
        speak("Opening YouTube")
    elif "open google" in command:
        webbrowser.open("https://www.google.com")
        print(f"AI said : Opening Google")
        speak("Opening Google")
    elif "open github" in command:
        webbrowser.open("https://www.github.com")
        print(f"AI said : Opening GitHub")
        speak("Opening GitHub")
    elif "open whatsapp" in command:
        webbrowser.open("https://web.whatsapp.com")
        print(f"AI said : Opening WhatsApp")
        speak("Opening WhatsApp")
    else:
        print(f"AI said : Sorry, I can't open that website.")
        speak("Sorry, I can't open that website.")

def get_time():
    """Tells the current time"""
    now = datetime.datetime.now().strftime("%I:%M %p")
    print(f"AI said : The time : {now}")
    speak(f"The time is {now}")

# def get_weather():
#     """Fetches current weather using OpenWeatherMap API"""
#     api_key = "your_api_key_here"  # Replace with your OpenWeatherMap API Key
#     city = "New Delhi"  # Change to your city
#     url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
#     response = requests.get(url)
#     data = response.json()

    # if data["cod"] == 200:
    #     temp = data["main"]["temp"]
    #     description = data["weather"][0]["description"]
    #     print(f"AI said : The current temperature in {city} is {temp} degrees Celsius with {description}.")
    #     speak(f"The current temperature in {city} is {temp} degrees Celsius with {description}.")
    # else:
    #     print(f"AI said : Sorry, I couldn't fetch the weather.")
    #     speak("Sorry, I couldn't fetch the weather.")

def handle_commands():
    """Handles user commands after wake word is detected"""
    while True:
        command = listen()
        if "exit" in command or "stop" in command:
            print(f"AI said : Goodbye!")
            speak("Goodbye!")
            wake_word(exit())
            break
        elif "time" in command:
            get_time()
        # elif "weather" in command:
        #     get_weather()
        elif "open" in command:
            open_website(command)
        elif "hey assistant" in command:
            print(f"AI said : How can I help you, sir?")
            speak("How can I help you, sir?")
        else:
            search(command)


if __name__ == "__main__":

    wake_word()
