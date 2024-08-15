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
        

def main():
    # Load JSON data
    data = load_json_data("sortedonlymessage2.json")

    # Prepare CSV file for output
    with open('classification_resultsMESSAGEONLY.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['USER_ID', 'EXISTING_RELEVANCY', 'PREDICTED_RELEVANCY'])

        # Process each message in the JSON file
        for message in data:
            prediction = classify_message(message)
            if prediction is not None:
                csvwriter.writerow([
                    message.get('user_id', 'N/A'),
                    message.get('Relevancy', 'N/A'),
                    prediction
                ])
            
            # Optional: Print progress
            print(f"Processed entry for User ID: {message.get('user_id', 'N/A')}")
            time.sleep(2)

    print("Classification complete. Results saved in 'classification_resultsMESSAGEONLY.csv'")

if __name__ == "__main__":
    main()
