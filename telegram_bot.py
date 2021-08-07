# import required libraries
import telebot,requests,random
from bs4 import BeautifulSoup
from requests_html import HTMLSession

# setup bot with Telegram token from .env
API = 'API_KEY'
bot = telebot.TeleBot(API)

bot.remove_webhook()

session = HTMLSession()
r = session.get('https://news.google.com/topstories?hl=en-GB&gl=GB&ceid=GB:en')
#render the html, sleep=1 to give it a second to finish before moving on. scrolldown= how many times to page down on the browser, to get more results. 5 was a good number here
r.html.render(sleep=1, scrolldown=0)

#find all the articles by using inspect element and create blank list
articles = r.html.find('article')
newslist = []
res = ""

#loop through each article to find the title and link. try and except as repeated articles from other sources have different h tags.
for item in articles:
    try:
        newsitem = item.find('h3', first=True)
        title = newsitem.text
        link = newsitem.absolute_links
        newsarticle = [title, link]
        newslist.append(newsarticle)
    except:
       pass

for h in range(len(newslist)):
    res += str(newslist[h][0]) + '\n'
    res += 'Link is give below:' +'\n'
    res += str(newslist[h][1]) + '\n'
    res += '-'*20 + '\n'

#scrap qoutes
sauce = requests.get("https://www.brainyquote.com/quote_of_the_day").text

soup = BeautifulSoup(sauce, 'lxml')
res_qotd = ""
for quote in soup.find_all('div', class_ = 'qotd-q-cntr'):
    heading = quote.h2.text
    #print(heading)
    res_qotd += '[' + heading + ']'

    t = quote.find_all('a')
    res_qotd += f'{t[0].text}'

    res_qotd += f'~by {t[1].text}'
    res_qotd += '\n' + ' '*30 + '\n'

# Handler triggered with the /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
 bot.reply_to(message, random.choice(['Heyyo!', 'Holaa', 'Howdyy!', 'Helloo','Ssup?!','Heyya','Hiiiee','Hey hooman','Namaskar','Hii']))
 bot.send_message(message.chat.id, "What can I do for you?\n Use /news for latest news \n Use /random for random photo \n Use /4k for 4k images \n Use /topic to get photo of related topics \n Use /qotd for Quote of the day")
 
@bot.message_handler(commands=["qotd"])
def qotd(message):
    bot.send_message(message.chat.id, res_qotd)

@bot.message_handler(commands=["news"])
def news(message):
    bot.send_message(message.chat.id, res)


# send random unsplash picture
@bot.message_handler(commands=['random'])
def send_random_pic(message):
  response = requests.get('https://source.unsplash.com/random')
  bot.send_photo(message.chat.id, response.content)
  
# send random 4k unsplash picture
@bot.message_handler(commands=['4k'])
def send_random_pic(message):
  response = requests.get('https://source.unsplash.com/random/4096x2160')
  bot.send_photo(message.chat.id, response.content)  
  bot.send_document(message.chat.id, response.content,caption='rename_to_jpeg')  


# send picture from topic  
@bot.message_handler(commands=['topic'])
def handle_text(message):
    cid = message.chat.id
    msgTopics = bot.send_message(cid, 'Type the topic(s), coma separated:')
    bot.register_next_step_handler(msgTopics , step_Set_Topics)

def step_Set_Topics(message):
    cid = message.chat.id
    topics = message.text
    response = requests.get("https://source.unsplash.com/random?{0}".format(topics))
    bot.send_photo(message.chat.id, response.content)

bot.polling()
