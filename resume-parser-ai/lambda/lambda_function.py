import json
import boto3
import os
from pypdf import PdfReader
from openai import OpenAI
from botocore.exceptions import ClientError

# Initialize AWS clients
s3 = boto3.client('s3')
secrets_client = boto3.client('secretsmanager')

# Function to retrieve the OpenAI API key from Secrets Manager
def get_secret():
    secret_name = "<OPENAI-API-KEY-SECRET-KEY-NAME>"  # Replace with your secret name
    try:
        response = secrets_client.get_secret_value(SecretId=secret_name)
        secret = response['SecretString']
        secret_data = json.loads(secret)  # Parse the secret as JSON if stored as a key-value pair
        return secret_data['OPENAI_API_KEY']
    except ClientError as e:
        print(f"Error retrieving secret: {str(e)}")
        raise e

# Function to extract data using OpenAI
def ats_extractor(resume_data, api_key):
    prompt = '''
You are an advanced AI resume parser capable of analyzing resumes in both English and French. Your task is to extract and structure information accurately from the provided resume.

Please extract and format the following information:

1. Personal Information:
   - Full Name
   - Email Address
   - Phone Number
   - Location (City/Country)

2. Online Presence (extract and categorize all URLs/links):
   - Professional Networks:
     * LinkedIn Profile
     * Xing Profile
     * Other Professional Networks
   - Code Repositories:
     * GitHub Profile
     * GitLab Profile
     * Bitbucket Profile
     * Other Code Repositories
   - Portfolio:
     * Personal Website
     * Project Portfolio
     * Design Portfolio (Behance, Dribbble, etc.)
   - Additional Online Profiles:
     * Medium
     * Dev.to
     * Stack Overflow
     * Other relevant platforms

3. Professional Experience:
   - For each position:
     * Company Name
     * Role/Title
     * Duration (Start Date - End Date)
     * Location
     * Key Responsibilities
     * Notable Achievements

4. Skills:
   - Technical Skills:
     * Programming Languages
     * Frameworks & Libraries
     * Tools & Technologies
     * Databases
     * Cloud Platforms
     * Other Technical Skills
   - Soft Skills:
     * Leadership Skills
     * Communication Skills
     * Other Soft Skills
   - Languages:
     * Language Name
     * Proficiency Level

5. Education:
   - For each degree:
     * Institution Name
     * Degree/Certification
     * Field of Study
     * Duration
     * Notable Achievements

Please follow these guidelines:
1. Identify and process text in both English and French
2. Validate all URLs and ensure they are properly formatted
3. Maintain the original language for proper nouns and organization names
4. Structure the output in clean, properly formatted JSON
5. Use null for missing fields rather than omitting them
6. Include all dates in ISO format (YYYY-MM-DD)
7. Categorize unknown links under "Other" with their domain names

Return the information in the following JSON format:
{
    "personal_info": {},
    "online_presence": {
        "professional_networks": {},
        "code_repositories": {},
        "portfolio": {},
        "additional_profiles": {}
    },
    "professional_experience": [],
    "skills": {
        "technical": {},
        "soft": [],
        "languages": []
    },
    "education": []
}

If you're uncertain about any information, mark it as "unspecified" rather than making assumptions.
'''
    openai_client = OpenAI(api_key=api_key)
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": resume_data}
    ]
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.0,
            max_tokens=1500
        )

        # Use dot notation to access the content of the response
        data = response.choices[0].message.content
        return data
    except Exception as e:
        print(f"Error calling OpenAI API: {str(e)}")
        return None

# Function to read PDF from S3 bucket
def read_file_from_s3(bucket_name, object_key):
    local_path = f'/tmp/{os.path.basename(object_key)}'
    s3.download_file(bucket_name, object_key, local_path)
    
    reader = PdfReader(local_path)
    text_data = ""
    
    # Extract text from each page
    for page in reader.pages:
        text_data += page.extract_text()
    
    return text_data

# Save extracted data to S3 and return the S3 key
def save_extracted_data_to_s3(bucket_name, object_key, extracted_data):
    try:
        s3.put_object(
            Bucket=bucket_name,
            Key=object_key,
            Body=json.dumps(extracted_data),
            ContentType='application/json'
        )
        print(f"Extracted data saved to {bucket_name}/{object_key}")
        return object_key  # Return the object key
    except Exception as e:
        print(f"Error saving data to S3: {str(e)}")
        raise e

# Update lambda_handler
def lambda_handler(event, context):
    try:
        # Check if this is an API Gateway request
        if 'queryStringParameters' in event:
            if not event['queryStringParameters'] or 'filename' not in event['queryStringParameters']:
                raise ValueError("Filename parameter is required")
            
            bucket_name = "resume-uploads-bucket"  # Your upload bucket
            object_key = event['queryStringParameters']['filename']
        
        # Check if this is an S3 event
        elif 'Records' in event and event['Records']:
            bucket_name = event['Records'][0]['s3']['bucket']['name']
            object_key = event['Records'][0]['s3']['object']['key']
        
        else:
            raise ValueError("Invalid event source")
        
        print(f"Processing file {object_key} from bucket {bucket_name}")

        # Get OpenAI API key
        api_key = get_secret()

        # Read PDF content from S3
        resume_data = read_file_from_s3(bucket_name, object_key)
        if not resume_data:
            raise ValueError("No content extracted from the resume")

        # Extract data using OpenAI
        extracted_data = ats_extractor(resume_data, api_key)
        if not extracted_data:
            raise ValueError("Failed to extract data from the resume")

        # Clean the extracted data
        cleaned_data = extracted_data.replace("```json", "").replace("```", "").strip()
        json_data = json.loads(cleaned_data)

        # Save to resume-extracted-data bucket
        output_bucket = "resume-extracted-data"
        output_key = f"extracted_{os.path.basename(object_key).replace('.pdf', '.json')}"
        
        # Save data and get it back for the response
        save_extracted_data_to_s3(output_bucket, output_key, json_data)

        # Return the parsed data
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Resume processed successfully',
                'parsed_data': json_data
            }),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Content-Type': 'application/json'
            }
        }
        
    except Exception as e:
        print(f"Error processing resume: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to process resume'
            }),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Content-Type': 'application/json'
            }
        }
  
