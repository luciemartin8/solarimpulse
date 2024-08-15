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

def classify_entry(entry):
    prompt = f"""
    You are an assistant tasked with classifying user interactions as 'good' (relevant) or 'bad' (irrelevant) based on specific criteria. Analyze the following user data:

    User ID: {entry.get('user_id', 'N/A')}
    Message: {entry.get('message', 'N/A')}
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
    4. Message Length: Must be longer than 20 characters.
    5. Spam Detection: 
           a. Total Message from user should be less than 11
           b. Repeated Message should be less than 6
    6. User Activity: The user should have been active within approximately the last year (compare 'last_seen' and 'date_of_request'). If 'last_seen' or 'date_of_request' are missing, ignore this check.
    7. Message Format: The message should not be entirely in uppercase.

    Classify this user interaction as 'good' (1) or 'bad' (0) based on these criteria. Return only the number 1 or 0.
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

def main():
    # Load JSON data
    data = load_json_data("sortedbasedonprofileandmessage.json")

    # Prepare CSV file for output
    with open('classification_resultsOP3.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['USER_ID', 'EXISTING_RELEVANCY', 'PREDICTED_RELEVANCY'])

        # Process each entry in the JSON file
        for entry in data:
            prediction = classify_entry(entry)
            if prediction is not None:
                csvwriter.writerow([
                    entry.get('user_id', 'N/A'),
                    entry.get('Relevancy', 'N/A'),
                    prediction
                ])
            
            # Optional: Print progress
            print(f"Processed entry for User ID: {entry.get('user_id', 'N/A')}")
            time.sleep(2)

    print("Classification complete. Results saved in 'classification_resultsOP3.csv'")

if __name__ == "__main__":
    main()
#this works