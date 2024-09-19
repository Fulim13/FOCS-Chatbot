from rest_framework.decorators import api_view
from rest_framework.response import Response
import os
import json
from langchain.memory import ConversationSummaryMemory
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from pathlib import Path
from django.conf import settings
from dotenv import load_dotenv
import time
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
load_dotenv()
# memory = ConversationSummaryMemory(llm=ChatMistralAI(
#     temperature=0, model="mistral-large-latest"))

MAX_RETRIES = 3  # Define the maximum number of retries
RETRY_DELAY = 2  # Delay between retries in seconds


@api_view(['POST'])
def send_some_data(request):
    load_dotenv()

    output_file = Path(settings.BASE_DIR) / "backend" / \
        "data" / "extracted_programme.json"

    model = ChatMistralAI(model="open-mixtral-8x22b",
                          mistral_api_key=os.environ["MISTRAL_API_KEY"])
    question = request.data.get('message', '')

    # data = json.loads(Path(output_file).read_text())
    # previous_context = str(memory.load_memory_variables({}))

    index_name = "focs-index2"
    pinecone_api_key = os.environ.get("PINECONE_API_KEY")
    pc = Pinecone(api_key=pinecone_api_key)
    index = pc.Index(index_name)

    embeddings = MistralAIEmbeddings(
        mistral_api_key=os.environ["MISTRAL_API_KEY"])
    vector_store = PineconeVectorStore(index=index, embedding=embeddings)
    data = vector_store.similarity_search(
        question,
        k=1,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an assistant for TARUMT to help students with FOCS university courses. if possible arrange the answer in numbered/ordered list and at the end of the answer, provide the url of the programmed as source: <a href='url'>Programme Name</a>"
            "Answer the question based on the following context:"),
        ("human", "Question: {question}\n Context: {context}")
    ])
    chain = prompt | model

    retries = 0
    while retries < MAX_RETRIES:
        try:
            result = chain.invoke(
                {"question": question, "context": data}
            )

            # memory.save_context({"input": question}, {
            #                     "output": result.content})

            return Response({
                "data": result.content
            })
        except Exception as e:
            retries += 1
            if retries >= MAX_RETRIES:
                return Response({
                    "error": "Failed to process the request after multiple attempts.",
                    "details": str(e)
                })
            else:
                time.sleep(RETRY_DELAY)  # Wait before retrying
