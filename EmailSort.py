import pandas as pd
from datetime import datetime
from googletrans import Translator, LANGUAGES
#import unicodedata

# Initialize the translator
translator = Translator()

def detect_and_translate(text, target_lang='en'):
    try:
        detection = translator.detect(text)
        if detection.lang != target_lang:
            translated = translator.translate(text, src=detection.lang, dest=target_lang)
            #print(f"Translated message: {translated.text}")
            return translated.text
    except Exception as e:
        print(f"Error during translation: {e}")
    return text

#def remove_accents(input_str):
   # nfkd_form = unicodedata.normalize('NFKD', input_str)
   # return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

def classify_email(row, message_counts):
    user_id = row['user_id']
    email = row['email']
    row['message'] = detect_and_translate(row['message'], target_lang='en')
    # 1. Check if required fields are filled
    required_fields = ['firstname', 'lastname', 'email', 'jobtitle', 'phone']
    if any(pd.isna(row[field]) for field in required_fields):
        print(f"{user_id}: Failed to fill out all necessary fields")
        return 'bad'
    
    # 2. Check if message is less than 20 characters 
    if len(row['message'].split()) < 20:
        print(f"{user_id}: Failed message length check: {email}")
        return 'bad'

    
     # 3. Check if message is in all caps 
    if row['message'] == row['message'].upper():
        print(f"{user_id}: Failed all caps check")
        return 'bad'



    # 4. Check if company name is in email 
    if 'gmail' in email or 'hotmail' in email or 'outlook' in email:
        print(f"{user_id}: Failed email domain check: {email}")
        return 'bad'
    
     # 5. Check for business inquiry or investing keywords 
    business_keywords = ['business','innovating','pitch','capital','financial','finance','invest','investing','investment', 'investor', 'sell', 'selling', 'cost', 'costs', 'partnership','collaboration', 'opportunity', 'market', 'marketing', 'call', 'chat', 'schedule', 'pricing', 'purchase', 'adopt', 'adopting', 'fund', 'funding', 'cooperation', 'buy']
    if not any(keyword in row['message'].lower() for keyword in business_keywords):
        print(f"{user_id}: Failed relevancy check")
        return 'bad'
    
    keyword_count = sum(keyword in row['message'].lower() for keyword in business_keywords)
    company_name = str(row['company_name']).lower() if pd.notna(row['company_name']) else ''
    company_words = company_name.split()
    email = str(row['email']).lower() if pd.notna(row['email']) else ''
    company_name_in_email = any(word in email for word in company_words)
    if not company_name_in_email and keyword_count > 2:
        print(f"Failed company name check but sufficient keywords: {user_id}")
        return 'good'

    # 6. Company name check if no relevant keywords
    if not any(word in email for word in company_words):
        print(f"{user_id}: Failed company name check: {company_name} not in {email}")
        return 'bad'

    # 7. Check for duplicate messages (this would require grouping by user_id and counting messages)
  #  if message_counts.get((row['user_id'], row['message']), 0) > 4:
  #      print(f"{user_id}: Failed spam check")
  #      return 'bad'

    # check frequency, varied messages every day is okay

    # 7a. Check if duplicate messages from same user 
    if row['repeated_message'] > 5 :
        print(f"{user_id}: Failed originality check")
        return 'bad'
    
    # 7b. Check if user is a spammer
    if row['total_user_message'] > 10:
        print(f"{user_id}: Failed spam check")
        return 'bad'
    # 8. Check user activity
    if (row['last_seen'] - row['date_of_request']).days > 365:
        print(f"{user_id}: Failed activity check")
        return 'bad'
    
    # If all checks pass, classify as good
    return 'good'

# Read the CSV file
df = pd.read_csv('specialcase.csv', parse_dates=['last_seen', 'date_of_request'])
message_counts = df.groupby(['user_id', 'message']).size().to_dict()
# Apply the classification function
df['classification'] = df.apply(classify_email, axis=1, message_counts=message_counts)

# Filter to include only 'good' emails
good_emails = df[df['classification'] == 'good']


good_emails.to_csv('specialcaseresult.csv', index=False)

# Display the results
print(good_emails[['user_id', 'firstname', 'lastname', 'email', 'classification']])
