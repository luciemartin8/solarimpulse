import json
import csv
import requests
import time

# Configuration
GPT4V_KEY = "insert key here"
headers = {
    "Content-Type": "application/json",
    "api-key": GPT4V_KEY,
}
GPT4V_ENDPOINT = "insert url here"

def load_json_data(file_path):
    full_path = f"sorted_samples/{file_path}"
    with open(full_path, 'r') as file:
        return json.load(file)

def classify_message(message):
    prompt = f"""
    You are an assistant tasked with filtering emails. First, categorize each email as "business inquiry", "innovators/investing", "partnership/collaboration", or "irrelevant" based on the content provided.
    Message: {message.get('message', 'N/A')}
    Criteria for classification: 
    1. Business Inquiry:
    - Questions about products, services, pricing, or availability.
    - Requests for proposals (RFPs) or sales inquiries.
    - Customer questions or potential leads.

    2. Innovators/Investing:
    - Discussion of investment opportunities.
    - Inquiries about innovation projects or new technology.
    - Information on funding, venture capital, or startup pitches.

    3. Partnership/Collaboration:
    - Proposals for joint ventures or strategic partnerships.
    - Offers for business or organizational collaborations.
    - Requests for meetings to discuss potential collaborations.

    4. Irrelevant:
    - Does not match any of the above categories or does not meet legitimacy criteria.

    Second, analyze if the email seems legitimate. A legitimate email should meet at least 2 out of these criteria:
    - Use proper grammar.
    - Have correctly spelled words.
    - Include an introduction with the sender's name.
    - Have a greeting such as "Hello", "Hi", or "Dear".
    - End with a sign-off including the sender's name and/or contact information.
    - Mention a company name.

    Based on the email categorization and legitimacy test, classify it as relevant or irrelevant.
    Do not print out the message, simply classify it as relevant or irrelevant. Relevant is a 1 and irrelevant is 0.
    Return only the number 1 or 0
    """

    payload = {
        "messages": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 800
    }

    try:
        response = requests.post(GPT4V_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()['choices'][0]['message']['content'].strip()
        return int(result)
    except requests.RequestException as e:
        print(f"Failed to make the request. Error: {e}")
        return None
    except (KeyError, ValueError) as e:
        print(f"Error processing response: {e}")
        return None
        
def classify_user(entry):
    prompt = f"""
    You are an assistant tasked with classifying emails as 'good' or 'bad' based on specific criteria. Analyze the following email data:
    User ID: {entry.get('user_id', 'N/A')}
    Date of Request: {entry.get('date_of_request', 'N/A')}
    Job Title: {entry.get('jobtitle', 'N/A')}
    First Name: {entry.get('firstname', 'N/A')}
    Last Name: {entry.get('lastname', 'N/A')}
    Email: {entry.get('email', 'N/A')}
    Phone: {entry.get('phone', 'N/A')}
    Last Seen: {entry.get('last_seen', 'N/A')}
    Company Name: {entry.get('company_name', 'N/A')}
    Total Messages from User: {entry.get('total_user_message', 'N/A')}
    Repeated Message: {entry.get('repeated_message', 'N/A')}

    Classification Criteria:
    1. Required Fields: All fields (firstname, lastname, email, jobtitle, phone) must be filled out.
    2. Email Domain: Must not be from generic providers (e.g., Gmail, Hotmail, Outlook).
    3. Company Email: The company name should be present in the email domain.
        Example: Company: Solar Impulse, Email: luciemartin@solarimpulse.com
    4. Spam Detection: 
        a. Total Message from user should be less than 11
        b. Repeated Message should be less than 6
    5. User Activity: The user should have been active within approximately the last year (compare 'last_seen' and 'date_of_request'). If 'last_seen' or 'date_of_request' are missing, ignore this check.

    Do not print out the message, simply classify it as relevant or irrelevant. Relevant is a 1 and irrelevant is 0.
    Return only the number 1 or 0

    """

    payload = {
        "messages": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 800
    }

    try:
        response = requests.post(GPT4V_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()['choices'][0]['message']['content'].strip()
        return int(result)
    except requests.RequestException as e:
        print(f"Failed to make the request. Error: {e}")
        return None
    except (KeyError, ValueError) as e:
        print(f"Error processing response: {e}")
        return None

def determine_relevancy(user_relevancy, message_relevancy):
    if (user_relevancy == 1 or message_relevancy == 1):
        return 1
    else:
        return 0

import csv
from collections import defaultdict

def main():
    # Load JSON data
    messagedata = load_json_data("sortedonlymessage2.json")
    userdata = load_json_data("sortedbasedonuserprofileonly.json")
    profile_and_message_data = load_json_data("sortedbasedonprofileandmessage.json")

    # Create a dictionary to store existing relevancy
    existing_relevancy = {entry['user_id']: entry['Relevancy'] for entry in profile_and_message_data}

    # Create a dictionary to store combined data for each user
    combined_data = defaultdict(lambda: {'existing_relevancy': 'N/A', 'predicted_user_relevancy': 'N/A', 'predicted_message_relevancy': 'N/A'})

    # Process each message in the JSON file
    for message in messagedata:
        user_id = message.get('user_id', 'N/A')
        message_prediction = classify_message(message)
        if message_prediction is not None:
            combined_data[user_id]['existing_relevancy'] = existing_relevancy.get(user_id, 'N/A')
            combined_data[user_id]['predicted_message_relevancy'] = message_prediction
        
        # Optional: Print progress
        print(f"Processed message for User ID: {user_id}")
        time.sleep(2)

    for entry in userdata:
        user_id = entry.get('user_id', 'N/A')
        user_prediction = classify_user(entry)
        if user_prediction is not None:
            combined_data[user_id]['existing_relevancy'] = existing_relevancy.get(user_id, 'N/A')
            combined_data[user_id]['predicted_user_relevancy'] = user_prediction
        
        # Optional: Print progress
        print(f"Processed user profile for User ID: {user_id}")
        time.sleep(2)

    # Determine overall predicted relevancy
    for user_id, data in combined_data.items():
        if isinstance(data, dict):
            user_relevancy = data.get('predicted_user_relevancy', 'N/A')
            message_relevancy = data.get('predicted_message_relevancy', 'N/A')
        else:
            print(f"Unexpected data type for user {user_id}: {type(data)}")
            user_relevancy = 'N/A'
            message_relevancy = 'N/A'
        
        # Convert to int if not 'N/A'
        user_relevancy = int(user_relevancy) if user_relevancy != 'N/A' else 'N/A'
        message_relevancy = int(message_relevancy) if message_relevancy != 'N/A' else 'N/A'
        
        predicted_relevancy = determine_relevancy(user_relevancy, message_relevancy)

        # Ensure data is a dictionary before assigning
        if not isinstance(data, dict):
            data = {}
        data['predicted_relevancy'] = predicted_relevancy

    # Prepare CSV file for output
    with open('classification_results_OP1.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['USER_ID', 'EXISTING_RELEVANCY', 'PREDICTED_USER_RELEVANCY', 'PREDICTED_MESSAGE_RELEVANCY', 'PREDICTED_RELEVANCY'])
        for user_id, data in combined_data.items():
            if isinstance(data, dict):
                csvwriter.writerow([
                    user_id,
                    data.get('existing_relevancy', 'N/A'),
                    data.get('predicted_user_relevancy', 'N/A'),
                    data.get('predicted_message_relevancy', 'N/A'),
                    data.get('predicted_relevancy', 'N/A')
                ])
            else:
                csvwriter.writerow([user_id, 'N/A', 'N/A', 'N/A', 'N/A'])

    print("Classification complete. Results saved in 'classification_results_OP1.csv'")


if __name__ == "__main__":
    main()


#based off of the entries in the classification results 5 csv classify the emails as overall relevant or irrelevant
#compare the overall predicted relevancy with existing relevancy for evaluation metric
#need to allow for double user entries?