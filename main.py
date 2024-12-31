from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
import os
from IPython.display import Markdown, display
from openai import OpenAI



# Some websites need you to use proper headers when fetching them:
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

class Website:
    def __init__(self, url):
        self.url = url
        self.text = None
        self.title = None

    def fetch_content(self):
        try:
            response = requests.get(self.url, headers=headers)  # Send a GET request to the URL
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
            response.encoding = 'utf-8' # Ensure the response encoding is set to utf-8
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve the webpage. Error: {e}")
            return None

        try:
            soup = BeautifulSoup(response.content, 'lxml')  # Parse the HTML content using BeautifulSoup and lxml
            self.title = soup.title.string  # Extract the title of the webpage
            text_content = soup.get_text()  # Extract the entire text content
            # print(text_content.encode('utf-8', errors='ignore').decode('utf-8'))  # Print the text content with encoding
            # with open('output.txt', 'w', encoding='utf-8') as f:
            #     f.write(text_content)  # Write the text content to a file
            # return text_content
            for irrelevant in soup.body(["script", "style", "img", "input"]):
                irrelevant.decompose()
            self.text = soup.body.get_text(separator="\n", strip=True)
            return self.text
        except Exception as e:
            print(f"Failed to parse the webpage content. Error: {e}")
            return None

# website = Website('https://pypi.org/project/beautifulsoup4/')
web = Website('https://edwarddonner.com')
# print(web.fetch_content())
# print(web.title)


# Load environment variables in a file called .env
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

# Check the key
if not api_key:
    print("No API key was found - please head over to the troubleshooting notebook in this folder to identify & fix!")
elif not api_key.startswith("sk-proj-"):
    print("An API key was found, but it doesn't start sk-proj-; please check you're using the right key - see troubleshooting notebook")
elif api_key.strip() != api_key:
    print("An API key was found, but it looks like it might have space or tab characters at the start or end - please remove them - see troubleshooting notebook")
else:
    print("API key found and looks good so far!")

openai = OpenAI() # Create an instance of the OpenAI class

# message = "Hello, GPT! This is my first ever message to you! Hi!"
# response = openai.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user", "content":message}])
# print(response.choices)
# print(response.choices[0].message.content)

# Define our system prompt - you can experiment with this later, changing the last sentence to 'Respond in markdown in Spanish."
system_prompt = "You are an assistant that analyzes the contents of a website \
and provides a short summary, ignoring text that might be navigation related. \
Respond in markdown."

# A function that writes a User Prompt that asks for summaries of websites:

def user_prompt_for(website):
    user_prompt = f"You are looking at a website titled {website.title}"
    user_prompt += "\nThe contents of this website is as follows; \
    please provide a short summary of this website in markdown. \
    If it includes news or announcements, then summarize these too.\n\n"
    user_prompt += website.fetch_content()
    return user_prompt  

user_prompt = user_prompt_for(web)

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt}
]

response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
print(response.choices[0].message.content)