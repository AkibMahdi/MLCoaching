#todo:
#Fix up artical retrieval for excessive requests ( > 1000 articles)
#Implement Document-Interpreting and input on a per-request basis to GPT API
import os
import glob
import openai
import requests
from bs4 import BeautifulSoup

print("Bismillah")

# term = str(input("Enter a Keyword for an article: "))
# term = "strength training AND weight lifting AND resistance training AND muscle growth AND cardio AND fat loss"
term = "hypertension AND male AND 60 years"


search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi/"
search_params = {
    "crdt" : "2008/12/16 6:00",
    "db" : "pmc",
    "term": f"{term}",
    "retmode": "json",
    "retmax": "1"
}

#3 requests per second per IP
response = requests.get(search_url, params=search_params)
data = response.json()
ids = data["esearchresult"]["idlist"]


fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
fetch_params = {
    "db": "pmc",
    "id": ",".join(ids),
    "rettype": "full",
    "retmode": "xml"
}

fetch_response = requests.get(fetch_url, params=fetch_params)

soup = BeautifulSoup(fetch_response.content, "lxml")
content = soup.find('body')
print("Fetched Article Details:")
print(content.get_text())

with open("traintest.txt", "w") as t:
    t.write(str(content.get_text()))


split_articles = [art for art in content.get_text().strip().split('pmc')]

articles_local = glob.glob("Articles/*")

for f in articles_local:
    os.remove(f)

#Add ids to cumulative ids



#filter articles, and write them to articles directory
article_count = 0
for id in ids:
    with open(f'Articles/{id}', "w") as a:
        a.write(split_articles[article_count+1])
    article_count += 1
    if article_count==len(ids):
        break


summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
summary_params = {
    "db": "pmc",
    "id": ",".join(ids),
    "retmode": "json"
}

summary_response = requests.get(summary_url, params=summary_params)
summary_data = summary_response.json()

print("Fetched Article Titles:")
for uid in ids:
    title = str(summary_data["result"][uid]["title"])
    print(title)

with open("traintest.txt", "w") as t:
    for uid in ids:
        info = str(summary_data["result"][uid])
        t.write(info)
        t.write('\n')

    

with open("articletitles.txt", "w") as t:
    for uid in ids:
        info = str(summary_data["result"][uid]["title"])
        t.write(info)
        t.write('\n')


with open('culum_ids.txt', 'r') as v:
    const_id = v.read() 

with open("culum_ids.txt", "a") as t:
    for uid in ids:
        if str(uid) in str(const_id):
            continue
        else:
            info = str(uid)
            t.write(info)
            t.write('\n')

print("Article IDs:", ids)
#print(data)

#openai implementation
import os
from openai import OpenAI

# Directory containing text files
directory = '/Users/farhanmukit/Desktop/ML Project/Articles'

def read_text_files(directory):
    texts = []
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            with open(os.path.join(directory, filename), 'r') as file:
                texts.append(file.read())
    return texts

texts = read_text_files(directory)

prompt = "how to decrease hypertension in men over 60"

combined_input = prompt + "\n\n" + soup.get_text()

#Use this for multiple articles, 
#combined_input = prompt + "\n\n" + "\n\n".join(texts)


# if len(combined_input.split()) > 8000:
#     raise ValueError("The combined input exceeds the token limit for GPT-4"# Send the request to OpenAI
response = OpenAI().chat.completions.create(
    model="gpt-4-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant, and give cited strength training advice based upon the articles provided to you, and nothing more. Also, with every suggestion, you provide an in-text citation, from only the articles you are provided. Be as technical as possible. Include the pmc uid of the article at the end of your response."},
        {"role": "user", "content": combined_input}
    ],
    max_tokens=500 # Adjust as needed
)

# Print the response
print(response)
# print(response.choices[0].message['content'].strip())
