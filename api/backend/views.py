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
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
import requests
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

    index_name = "focs-index11"
    pinecone_api_key = os.environ.get("PINECONE_API_KEY")
    pc = Pinecone(api_key=pinecone_api_key)
    index = pc.Index(index_name)

    embeddings = MistralAIEmbeddings(
        mistral_api_key=os.environ["MISTRAL_API_KEY"])
    vector_store = PineconeVectorStore(index=index, embedding=embeddings)
    data = vector_store.similarity_search(
        question,
        k=2,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are Jamie, an assistant for TARUMT, here to help students with questions about FOCS university courses. "
         "Please answer the student's question based on the provided context. "
         "If possible, structure your answer in a numbered or ordered list for clarity. "
         "At the end of your response, include the relevant program URL in the following format: "
         "<a href='url'>Programme Name</a>. "
         "If the context does not provide enough information to answer the question directly, "
         "respond by saying you don't know and provide the following website URL for further assistance: "
         "<a href='https://focs.tarc.edu.my/programmes' target='_blank'>FOCS Programmes</a>. "
         "Encourage the student to contact FOCS for more information at 03-4145 0123 ext 3233, 011-1075 8554, "
         "or via email at focs@tarc.edu.my. You can also visit the 2nd Floor, Bangunan Tan Sri Khaw Kai Boh (Block A). "
         "If the user asks about the programs offered, provide the following information:\n"
         "Here is a list of programs offered by FOCS:\n\n"
         "1. Foundation in Computing\n"
         "2. Diploma in Computer Science\n"
         "3. Diploma in Information Technology\n"
         "4. Bachelor of Software Engineering (Honours)\n"
         "5. Bachelor of Computer Science (Honours) in Data Science\n"
         "6. Bachelor of Computer Science (Honours) in Interactive Software Technology\n"
         "7. Bachelor of Information Technology (Honours) in Software Systems Development\n"
         "8. Bachelor of Information Technology (Honours) in Information Security\n"
         "9. Master of Information Technology\n"
         "10. Master of Computer Science\n"
         "11. Doctor of Philosophy (Information Technology)\n"
         "12. Doctor of Philosophy in Computer Science\n\n"
         "For more details, please visit the FOCS website: <a href='https://focs.tarc.edu.my/programmes' target='_blank'>FOCS Programmes</a>."
         ),
        ("human",
         "Question: {question}\n"
         "Context: {context}"
         )
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


@api_view(['POST'])
def upload_result(request):
    # Parsing the incoming request with file and form data
    parser_classes = [MultiPartParser, FormParser]

    # Get the uploaded file and the selected program from the form
    image_file = request.FILES.get('resultImage', None)
    selected_program = request.POST.get('program', '')

    # Prepare the request to OCR.Space API
    url = "https://api.ocr.space/parse/image"
    api_key = os.environ["OCR_API_KEY"]  # Replace with your actual API key

    # Prepare the multipart/form-data payload
    files = {
        'file': image_file,
    }
    data = {
        'apikey': api_key,
        'language': 'eng',
        'isTable': 'true',
    }

    # Send the POST request to the OCR.Space API
    try:
        response = requests.post(url, files=files, data=data)
        response_data = response.json()
        print(response_data['ParsedResults'][0]['ParsedText'])

        # Check if the response was successful
        if response.status_code == 200:
            model = ChatMistralAI(model="mistral-large-latest",
                                  mistral_api_key=os.environ["MISTRAL_API_KEY"])

            index_name = "focs-index11"
            pinecone_api_key = os.environ.get("PINECONE_API_KEY")
            pc = Pinecone(api_key=pinecone_api_key)
            index = pc.Index(index_name)

            embeddings = MistralAIEmbeddings(
                mistral_api_key=os.environ["MISTRAL_API_KEY"])
            vector_store = PineconeVectorStore(
                index=index, embedding=embeddings)
            data = vector_store.similarity_search(
                selected_program*5,
                k=1,
            )

            prompt = ChatPromptTemplate.from_messages([
                ("system",
                 "You are an evaluation assistant for TARUMT, tasked with helping students determine their eligibility for selected programs. "
                 "Please respond strictly using the format provided below, based on your analysis:\n"
                 "<div color='red' for Not Eligible or green for Eligible'> Eligible Status: Eligible/Not Eligible </div>\n"
                 "Reason: <reason here>\n"),

                ("human",
                 "Here is the extracted text from the uploaded image:\n"
                 "{extracted_text}\n\n"
                 "Here are the minimum requirements for the selected program:\n"
                 "{minimum_requirement}\n\n"

                 "Important: If the extracted text is empty or does not include 'SPM - Sijil Pelajaran Malaysia', return only this format:\n"
                 "<div color='red'> Eligible Status: Not Eligible </div>\n"
                 "Reason: Unable to find SPM Certificate\n"
                 "Do not proceed further in this case.\n\n"

                 "Follow this step-by-step guide to assess eligibility:\n"
                 "1. Identify the Minimum Requirement for the Program.\n"
                 "2. Check the extracted text for 'SPM' (Sijil Pelajaran Malaysia):\n"
                 "   - Cemerlang Tertinggi - A+\n"
                 "   - Cemerlang Tinggi - A\n"
                 "   - Cemerlang - A-\n"
                 "   - Kepujian Tertinggi - B+\n"
                 "   - Kepujian Tinggi - B\n"
                 "   - Kepujian Atas - C+\n"
                 "   - Kepujian - C\n"
                 "   - Lulus Atas - D\n"
                 "   - Lulus - E\n"
                 "   - Gagal - G\n"
                 "   - TH - Tidak Hadir\n"
                 "Note: 'MATHEMATIK TAMBAHAN' refers to Additional Mathematics. If OCR misreads it as 'Ma Tematik', consider it Additional Mathematics.\n"
                 "3. Compare the applicant's certificate results with the program's minimum requirements:\n"
                 "   - If the result exceeds the minimum, the applicant is eligible.\n"
                 "   - If the result is below the minimum, the applicant is not eligible.\n"
                 "   - If the result matches the minimum, the applicant is eligible.\n"
                 "   - If the result is unclear or not found, the applicant is not eligible.\n"
                 "   - If the extracted text includes 'SPM - Sijil Pelajaran Malaysia' but does not provide sufficient grades to meet the minimum requirements, provide the appropriate reason for not being eligible.\n"
                 "Examples:\n"
                 "   - If the minimum requirement is 'A' in Mathematics and the applicant has 'B', they are not eligible.\n"
                 "   - If Additional Mathematics is required and not listed in the grades, even though the applicant has Mathematics, they are not eligible.\n"
                 "   - If the minimum requirement is 5 credits and the applicant has only 4 credits, they are not eligible.\n"
                 "   - If the applicant has 'C' in English but the minimum requirement is 'B', they are not eligible.\n"
                 "   - If the extracted result states 'SPM - Not found' instead of a grade, the applicant is not eligible.\n"
                 "   - If the required subjects are not mentioned in the extracted text, the applicant is not eligible.\n"
                 "   - If the applicant has 'G' in Bahasa Melayu and Sejarah, they are not eligible.\n"
                 "4. Return the eligibility format:\n"
                 "<div color='red' for Not Eligible or green for Eligible'> Eligible Status: Eligible/Not Eligible </div>\n"
                 "Reason: <reason here>\n"
                 "Note: If uncertain, indicate 'Not Eligible' with a clear reason. Avoid using 'unknown'.\n"
                 )
            ])

            chain = prompt | model

            retries = 0
            while retries < MAX_RETRIES:
                try:
                    result = chain.invoke(
                        {"extracted_text": response_data['ParsedResults']
                            [0]['ParsedText'],
                            "minimum_requirement": data}
                    )

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

                    return Response(response_data)
        else:
            return Response({"error": "Failed to process the image.", "details": response_data}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": "An error occurred while processing the request.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
