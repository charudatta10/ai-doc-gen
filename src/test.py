from langgraph.graph import AgentGraph
from langchain.llms import Ollama
from langchain.tools import Tool

llm = Ollama(model="phi3")

tools = [
    Tool(name="ReadMarkdown", func=read_markdown, description="Reads a Markdown file."),
]

graph = AgentGraph(llm=llm, tools=tools)
response = graph.run("Generate a haiku based on the Markdown file content.")
print(response)