from langchain_community.document_loaders import TextLoader
from langchain_mistralai import ChatMistralAI
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.utils.function_calling import convert_to_openai_tool
from typing import Optional, List
import json
import os

model = ChatMistralAI(model="mistral-small-latest")


class Requirement(BaseModel):
    exam_qualification: str = Field(
        description="The exam or qualification required.")
    grade: str = Field(
        description="The grade or score required in the exam or qualification.")
    subject: Optional[str] = Field(
        description="The subject or area of study required for the exam or qualification.")


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
    minimum_entry_requirements: List[Requirement] = Field(
        description="The minimum entry requirements for the programme.")
    academic_progression: Optional[str] = Field(
        description="The academic progression opportunities after completing the programme.")


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
    "./data/Bachelor_of_Software_Engineering.txt",
    "./data/Bachelor_of_DS.txt"
]
output_file = "./data/extracted_programme.json"

if not os.path.exists(output_file):
    # Load each file separately and combine the results
    docs = []
    for path in file_paths:
        loader = TextLoader(path)
        docs.extend(loader.load())  # Combine the documents

    for doc in docs:
        response = extraction_chain.invoke({"input": doc})
        # Check if the JSON file exists and load its content if it does
        try:
            with open(output_file, 'r') as file:
                existing_data = json.load(file)
        except FileNotFoundError:
            existing_data = []

        # Append the new data to the existing content
        existing_data.append(response)

        # Write the updated content back to the JSON file
        with open(output_file, 'w') as file:
            json.dump(existing_data, file, indent=4)

        print(f"data appended to {output_file}")
