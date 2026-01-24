from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
import asyncio

async def test_ollama():
    print("Testing Ollama with llama3.1:8b...")
    llm = ChatOllama(model="llama3.1:8b", temperature=0)
    try:
        response = await llm.ainvoke([HumanMessage(content="Say 'Hello, I am ready'")])
        print(f"Response: {response.content}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_ollama())
