from langchain_google_genai import ChatGoogleGenerativeAI

import os
from dotenv import load_dotenv

load_dotenv()


def Load_Gemini_Model():
    llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"))
    return llm


if __name__ == "__main__":
    model = Load_Gemini_Model()
    print(model.invoke("Hello! how are you!").content)
    # print(Load_Gemini_Model().invoke("Hi").content)