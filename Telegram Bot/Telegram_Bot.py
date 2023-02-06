from asyncio.windows_events import NULL
import googlesearch as gs
import telebot
import re
from bs4 import BeautifulSoup
import requests

from sgnlp.models.sentic_gcn import(
    SenticGCNBertConfig,
    SenticGCNBertModel,
    SenticGCNBertEmbeddingConfig,
    SenticGCNBertEmbeddingModel,
    SenticGCNBertTokenizer,
    SenticGCNBertPreprocessor,
    SenticGCNBertPostprocessor
)

#Instantiate the SGnlp model
#instantiation process

tokenizer = SenticGCNBertTokenizer.from_pretrained("bert-base-uncased")

config = SenticGCNBertConfig.from_pretrained(
            "https://storage.googleapis.com/sgnlp/models/sentic_gcn/senticgcn_bert/config.json"
        )

model = SenticGCNBertModel.from_pretrained(
            "https://storage.googleapis.com/sgnlp/models/sentic_gcn/senticgcn_bert/pytorch_model.bin",
            config=config
        )

embed_config = SenticGCNBertEmbeddingConfig.from_pretrained("bert-base-uncased")

embed_model = SenticGCNBertEmbeddingModel.from_pretrained("bert-base-uncased",
            config=embed_config
        )

preprocessor = SenticGCNBertPreprocessor(
            tokenizer=tokenizer, embedding_model=embed_model,
            senticnet="https://storage.googleapis.com/sgnlp/models/sentic_gcn/senticnet.pickle",
            device="cpu")

postprocessor = SenticGCNBertPostprocessor()
   
inputs = []

#instantiation process end


#function to use sgnlp package Aspect-Based Sentiment Analysis model,
#returns an average aspect score based on array of sentences
def sgnlp_Analysis(sentences, aspect):

        
        input_dict = {"aspects": [],
              
                      "sentence": ""}

        input_dict["aspects"].append(aspect)

        for sentence in sentences:

            input_dict["sentence"] = sentence
            inputs.append(input_dict)
            input_dict = {"aspects": [],
              
                      "sentence": ""}
            input_dict["aspects"].append(aspect)

        #process inputs and generate sentiment aspect labels
        processed_inputs, processed_indices = preprocessor(inputs)
        raw_outputs = model(processed_indices)
        post_outputs = postprocessor(processed_inputs=processed_inputs, model_outputs=raw_outputs)
    

        scores = []
        for output in post_outputs:

            #aspect_score = post_outputs[3]["labels"][0]
            scores.append(output["labels"][0])

        #compute average sentiment aspect score 
        avg_score = float(sum(scores))/float(len(scores))

        if avg_score > 0:
            #return "Positive"
            print("Positive")

        elif avg_score < 0:
            #return "Negative"
            print("Negative")

        elif avg_score == 0:
            #return "Neutral"
            print("Neutral")

        return avg_score



#function to replace certain characters in telebot format
def replaced_escaped_characters(message_string):
    return message_string.replace("-","\\-").replace(".","\\.").replace("_","\\_").replace("*","\\*").replace("[","\\[").replace("]","\\]").replace(")","\\)").replace("(","\\(").replace("!","\\!").replace("~","\\~")



#input the api key here
API_KEY = ''
bot = telebot.TeleBot(API_KEY,parse_mode="MarkdownV2")

@bot.message_handler(commands=['search'])
def search(message):
    prompt = bot.send_message(message.chat.id, "Please enter a word that you would like to search")
    #moving to the next message
    bot.register_next_step_handler(prompt, search_reply)

def search_reply(message):
    query = message.text
    bot.send_message(message.chat.id, "Thank you")
    #reply will be the word being send back by the user
    print(query)


    #function access content in given url 
    def getdata(url): 
        r = requests.get(url) 
        return r.text 



    #function to retrieve links based on keyword    
    def search_for_results(query, num_links):

        #links that might caused problems
        forbidden_link = ["www.imf.org", "dictionary.cambridge.org"]
        listoflinks = []
        counter = 0

        for j in gs.search(query, num_results=100):

            if any(link in j for link in forbidden_link):
                continue
         
            if listoflinks.count(j)==0:
                listoflinks.append(j)
                counter+=1

                #obtained  required no. of links
                if counter == num_links: 
                    return list(listoflinks)

        #For situations where there arent many different search results, it just yields all unique links            
        return list(listoflinks)

        

    def get_content(link):
        #inserting the link in here of the webpage (Standard)
        url = link

        #checking for permission (Standard)
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
        response = requests.get(url, headers=headers)
        print(response)
        print('\n')

        #access content in given link
        htmldata = getdata(link) 
        soup = BeautifulSoup(htmldata, 'html.parser') 

        # initialize the largest paragraph and its length
        largest_paragraph = ""
        largest_length = 0


        # find all the p_paraSet in the HTML document
        p_paraSet = soup.find_all("p")
        # loop through each paragraph to find the largest paragraph to be used for analysis
        a_paraSet = soup.find_all("a")
        
        for p in p_paraSet:
            if (len(p.text) > largest_length) and (query.lower() in p.text.lower()):
                largest_paragraph = (p.text).lower()
                largest_length = len(p.text)
                
        if p_paraSet == []:
            for a in a_paraSet:
                    if (len(a.text) > largest_length) and (query.lower() in a.text.lower()):
                        largest_paragraph = (a.text).lower()
                        largest_length = len(a.text)

        # print the largest paragraph
        return (largest_paragraph)
        
      

    #function to convert paragraph to array sentences
    def paragraph_to_sentence(para):
        new_sent = []

        sentences = [x for x in re.split(r"[.|!|?]", para) if x!=""]

        #remove last sentence because might be incomplete 
        #remove before checking
        if len(sentences) > 1:
            sentences.pop()

        #check if sentence contains aspect word, if not remove
        for sentence in sentences:
            if query.lower() in sentence.lower():
                new_sent.append(sentence)
    
        #the sentence array is assign to the new one
        sentences = new_sent

        return sentences


    #start searching for links
    start = "Please give me a few seconds"
    bot.send_message(message.chat.id,start)
   
    #for link in search_for_results(query,3):
    for link in search_for_results(query,5):
        
        try:
            par = get_content(link)
            sentences = paragraph_to_sentence(par)
            print("printing sentences and query")
            print(sentences)
            print(query)
            avg_score = sgnlp_Analysis(sentences,str(query).lower())

            eval_Text = ""
            if avg_score > 0:
                eval_Text = "Positive"
            elif avg_score < 0:
                eval_Text = "Negative"
            elif avg_score == 0:
                eval_Text = "Neutral"

            word = "[link](" + replaced_escaped_characters(str(link)) + ")" + " is " + eval_Text +  " with a rating score of " + replaced_escaped_characters(str(round(avg_score,2)))    
            bot.send_message(message.chat.id, word)
            
        except ValueError:
            word = "Invalid Link skipped"    
            bot.send_message(message.chat.id, word)
            continue
            

    end = "Here are all the links I have found, thank you for using PaperNinja Bot\\."
    bot.send_message(message.chat.id, end)
     


#declaring it as global so it can be used in both functions
global text 
text = "Welcome to *OUR APP* \nEnter /search followed by a keyword and we will provide you with links based on that keyword\\. \
In addition, using SGNLP AI model, we will inform you whether the article contains positive or negative sentiments regarding the keyword\\."

#starter
@bot.message_handler(commands=['start'])
def start(message):
  bot.reply_to(message, text)

#help
@bot.message_handler(commands=['help'])
def start(message):
  bot.reply_to(message, text)
                   
bot.polling()