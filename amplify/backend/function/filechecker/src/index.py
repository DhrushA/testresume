import boto3
import PyPDF2
import openai
from io import BytesIO
import os

# Set your OpenAI API key (you should store it in AWS Secrets Manager or Lambda environment variables for security)
openai.api_key = os.getenv("OPENAI_API_KEY")

def handler(event, context):
    # Get bucket name and object key from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']

    # Log the file details
    print(f"File uploaded: {object_key} in bucket {bucket_name}")

    # Check if the file is a PDF by the extension
    if object_key.lower().endswith('.pdf'):
        # Initialize the S3 client
        s3_client = boto3.client('s3')

        try:
            # Get the PDF file from S3
            response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
            pdf_file = response['Body'].read()

            # Open the PDF file using PyPDF2
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file))

            # Extract text from the PDF (from all pages)
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()

            # Use ChatGPT to extract data
            extracted_data = extract_data_with_chatgpt(text)

            print("Extracted Data: ", extracted_data)

            return {
                "statusCode": 200,
                "message": "Data extracted successfully.",
                "extracted_data": extracted_data
            }
        except Exception as e:
            print(f"Error processing PDF: {e}")
            return {
                "statusCode": 500,
                "message": f"Error processing PDF: {str(e)}"
            }
    else:
        print("The uploaded file is NOT a PDF.")
        return {
            "statusCode": 400,
            "message": "File is not a PDF."
        }

def extract_data_with_chatgpt(text):
    """
    Send the extracted text to ChatGPT and request structured data extraction
    """

    # Create a prompt for ChatGPT to extract name, email, phone, and skills
    prompt = f"""
    Extract the following details from the provided text:

    1. Full Name
    2. Email Address
    3. Phone Number
    4. Skills (a list of skills)

    Text: 
    {text}

    Provide the output in the following JSON format:

    {{
        "name": "<Full Name>",
        "email": "<Email Address>",
        "phone": "<Phone Number>",
        "skills": ["Skill1", "Skill2", "Skill3"]
    }}
    """

    try:
        # Call ChatGPT to process the text
        response = openai.Completion.create(
            model="gpt-3.5-turbo",  # You can use a specific model like "gpt-3.5-turbo" or "gpt-4"
            prompt=prompt,
            max_tokens=500,  # Adjust based on the length of the expected response
            temperature=0.7,  # Adjust for creativity (0.0 to 1.0)
        )

        # Extract the data from the response
        extracted_data = response['choices'][0]['text'].strip()

        # Return the extracted data as a JSON-like structure
        return extracted_data

    except Exception as e:
        print(f"Error calling ChatGPT: {e}")
        return {"error": "Error processing with ChatGPT"}
