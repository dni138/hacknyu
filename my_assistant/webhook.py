from flask import Flask
from flask_assistant import Assistant, ask, tell
import logging
from datetime import datetime
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Say
from selenium import webdriver
import time

logging.getLogger('flask_assistant').setLevel(logging.DEBUG)

app = Flask(__name__)
assist = Assistant(app, project_id='neighbor-1fd69')

@assist.action('greeting') #'greeting' here is an intent 
def greet_and_start():
    return ask("What do you need help with?")

what_they_want = ''
@assist.action('help')
def helper(action):
    what_they_want = action
    return ask("Great! You need help with " + what_they_want + ". What day do you need help with this?")

day_they_want = ''
@assist.action('day')
def day_def(day):
    day_they_want = day[:10]
    return ask("Fantastic! You want help on " + day_they_want + ". What time?")

time_they_want = ''
@assist.action('time')
def time_def(time):
    datetime_object = datetime.strptime(time[11:16], '%H:%M')
    time_they_want = datetime_object.strftime('%I:%M%p')
    return ask("Awesome! So at "+ time_they_want + ". Do you want us to call now?")

@assist.action('call')
def make_call(yes_no):
    if yes_no.lower() == 'yes':
        # Start of Twilio Integration
        response = VoiceResponse()
        response.say('Hey there! Your friend needs help with '+ what_they_want + '. If you are free on ' + day_they_want + ' at ' + time_they_want + '. Thanks!')
        raw_text=str(response)
        split_text = raw_text.split('>')
        split_text = split_text[0] + '>\n' + split_text[1] + ">\n" + split_text[2] + '>\n' + split_text[3] + ">\n" + split_text[4] + ">"
        split_text = split_text.split('<')
        text = '<' + split_text[1] + '<' + split_text[2] + '<' + split_text[3] + '\n<' + split_text[4] + '<' + split_text[5]

        #Input message into link
        driver = webdriver.Chrome('/Users/nissani/Desktop/hacknyu/chromedriver')
        driver.get("https://www.twilio.com/labs/twimlets/echo")
        driver.find_element_by_tag_name("textarea").send_keys(text)

        time.sleep(5)

        #Extract link we need
        new_url=driver.find_elements_by_partial_link_text('a')[1].text

        #text_list = []
        #for links in new_url:
        #   text_list.append(links.text)
        final_url=new_url
        print(final_url)

        # Your Account Sid and Auth Token from twilio.com/console
        account_sid = 'ACbb4c9a919128882a2cc3de7bb35eb628'
        auth_token = '846ef94690b4ee4cb504f6af6f4c3ded'
        client = Client(account_sid, auth_token)

        call = client.calls.create(
                                url= final_url,
                                to='+12488603141',
                                from_='+12482923276'
                            )
        return "Call in progress. Have a great day!"
    else:
        return "Thanks! Have a great day!"

if __name__ == '__main__':
    app.run(debug=True, port = 5000)