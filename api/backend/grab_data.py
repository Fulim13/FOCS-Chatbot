import time
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import TextLoader
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.utils.function_calling import convert_to_openai_tool
from typing import Optional, List
from langchain_pinecone import PineconeVectorStore
import json
import os
from uuid import uuid4
from dotenv import load_dotenv
load_dotenv()


model = ChatMistralAI(model="mistral-small-latest",
                      mistral_api_key=os.environ["MISTRAL_API_KEY"])


class Programme(BaseModel):
    programme_overview: Optional[str] = Field(
        description="A brief overview of the programme.")
    programme_name: str = Field(
        description="The name of the programme.")
    campuses: List[str] = Field(
        description="The campuses where the programme is offered.")
    duration: str = Field(
        description="The duration of the programme.")
    intake: str = Field(
        description="The intake dates for the programme.")
    programme_outlines: str = Field(
        description="The outlines of the programme.")
    career_perspectives: Optional[str] = Field(
        description="The career perspectives of the programme.")
    estimated_fees: int = Field(
        description="The estimated fees for the programme.")
    minimum_entry_requirements: List[str] = Field(
        description="The minimum entry requirements for the programme.")
    academic_progression: Optional[str] = Field(
        description="The academic progression opportunities after completing the programme.")
    url: str = Field(
        description="The URL to the programme page.")


prompt = ChatPromptTemplate.from_messages([
    ("system", "Extract the relevant information, if not explicitly provided do not guess. Extract partial info, in JSON Format"),
    ("human", "{input}")
])

pydantic_schemas = [Programme]
tools = [convert_to_openai_tool(p) for p in pydantic_schemas]

# Give the model access to these tools:
extraction_model = model.bind_tools(tools=tools)

extraction_chain = prompt | extraction_model | JsonOutputParser()

# List of file paths
file_paths = [
    "./data/Foundation_in_Computing.txt",
    "./data/Diploma_in_Computer_Science.txt",
    "./data/Diploma_in_Information_Technology.txt",
]
output_file = "./data/extracted_programmes.json"

if not os.path.exists(output_file):
    # Load each file separately and combine the results
    docs = []
    for path in file_paths:
        loader = TextLoader(path)
        docs.extend(loader.load())  # Combine the documents

    pinecone_api_key = os.environ.get("PINECONE_API_KEY")
    pc = Pinecone(api_key=pinecone_api_key)

    index_name = "focs-index2"

    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=1024,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        while not pc.describe_index(index_name).status["ready"]:
            time.sleep(1)

    index = pc.Index(index_name)

    embeddings = MistralAIEmbeddings(
        mistral_api_key=os.environ["MISTRAL_API_KEY"])

    vector_store = PineconeVectorStore(index=index, embedding=embeddings)

    uuids = [str(uuid4()) for _ in range(len(docs))]

    vector_store.add_documents(documents=docs, ids=uuids)

# for doc in docs:
#     response = extraction_chain.invoke({"input": doc})
#     # Check if the JSON file exists and load its content if it does
#     try:
#         with open(output_file, 'r') as file:
#             existing_data = json.load(file)
#     except FileNotFoundError:
#         existing_data = []

#     # Append the new data to the existing content
#     existing_data.append(response)

#     # Write the updated content back to the JSON file
#     with open(output_file, 'w') as file:
#         json.dump(existing_data, file, indent=4)

#     print(f"data appended to {output_file}")
