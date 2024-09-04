from rest_framework.decorators import api_view
from rest_framework.response import Response
import os
import json
from langchain.memory import ConversationSummaryMemory
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from pathlib import Path
from django.conf import settings
from dotenv import load_dotenv
import time

load_dotenv()
memory = ConversationSummaryMemory(llm=ChatMistralAI(
    temperature=0, model="mistral-large-latest"))

MAX_RETRIES = 3  # Define the maximum number of retries
RETRY_DELAY = 2  # Delay between retries in seconds


@api_view(['POST'])
def send_some_data(request):
    load_dotenv()

    output_file = Path(settings.BASE_DIR) / "backend" / \
        "data" / "extracted_programme.json"

    if os.path.exists(output_file):
        model = ChatMistralAI(model="mistral-small-latest",
                              mistral_api_key=os.environ["MISTRAL_API_KEY"])
        question = request.data.get('message', '')

        data = json.loads(Path(output_file).read_text())
        previous_context = str(memory.load_memory_variables({}))

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an assistant for TARUMT to help students with FOCS university courses. "
             "This is the history of chat: {history_chat}. "
             "Answer the question based on the following context:"),
            ("human", "Question: {question}\n Context: {context}")
        ])
        chain = prompt | model

        retries = 0
        while retries < MAX_RETRIES:
            try:
                result = chain.invoke(
                    {"question": question, "context": data,
                        "history_chat": previous_context}
                )

                memory.save_context({"input": question}, {
                                    "output": result.content})

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
    else:
        return Response({
            "data": "No data available"
        })
