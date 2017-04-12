import os
from flask import Flask, render_template, request
from werkzeug.contrib.cache import SimpleCache
from pattern.en import wordnet, pluralize, singularize
from watson_developer_cloud import VisualRecognitionV3

#instantiates the IBM Watson's visual regconition
visual_recognition = VisualRecognitionV3('2016-05-20', api_key='c6f25fcfd00c3ad03ffa283a79eb2e5490874d02')

app = Flask(__name__)
#app.config.from_object(os.environ['APP_SETTINGS'])
cache = SimpleCache()

#TODO: cache user's name.
def cache_username(user_name):
    return cache.set('current_user', user_name, timeout=300)
def get_cached_username():
    return cache.get('current_user') if cache.get('current_user') else False
def cache_bot_img(bot_say, imageUrl):
    cache.set('imageUrl', imageUrl, timeout=300)
    return cache.set('bot_say', bot_say, timeout=300)
def get_bot_say():
    return cache.get('bot_say')
def get_image_url():
    return cache.get('imageUrl')

@app.after_request
def cache_control(res):
    res.cache_control.public = True
    return res

@app.route("/")
def index():
    cache.clear()
    #show welcome page
    return render_template('intro.html')

@app.route("/compliment")
def say_thanks():
    if get_cached_username() == False:
        return index()
    return render_template('thanks.html', bot_say = get_bot_say(), imgURL = get_image_url(), user_name = get_cached_username())
@app.route("/anotherone")
def anotherone():
    if get_cached_username() == False:
        return index()
    return render_template('anotherone.html', bot_say = get_bot_say(), imgURL = get_image_url(), user_name = get_cached_username())
@app.route("/get_user_name", methods=['GET', 'POST'])
def get_user_name():
    user_name = str(request.form['user_name'])
    cache_username(user_name)
    if get_cached_username() == False:
        return index()
    return render_template('info.html', user_name = get_cached_username())

#analyze given image
@app.route("/analyze", methods=['GET', 'POST'])
def img_upload():
    #get the given image's url (firebase storage url)
    imageUrl = str(request.form['hiddenUrl'])

    #IBM Watson classifies image and returns a dictionary
    #TODO: use try catch here, in case of an error
    #in this case, try catch can't be used cos Watson doesn't return an error
    #exception but a dictionary

    #IBM Watson checks for faces in the photo
    result_from_IBM_Watson = visual_recognition.detect_faces(images_url=imageUrl)
    #if faces are found in the image
    if 'faces' in result_from_IBM_Watson['images'][0] and result_from_IBM_Watson['images'][0]['faces']:
        bot_say = "I can see " + parse_faces(result_from_IBM_Watson['images'][0]['faces']) + " in this photo."
    #if there was an error with the image
    elif 'error' in result_from_IBM_Watson['images'][0]:
        bot_say = "I'm sorry, I had some error with that photo. Try a different photo please."
    else:
        #TODO: use try catch here, in case of an error
        #in this case, try catch can't be used cos Watson doesn't return an error
        #exception but a dictionary
        result_from_IBM_Watson = visual_recognition.classify(images_url=imageUrl)

        if 'error' in result_from_IBM_Watson['images'][0]:
            bot_say = "I'm sorry, I had some error with that photo. Try a different photo please."
        #get list of dictionaries containing 'scores' and 'class' from 'result_from_IBM_Watson'
        else:
            #refine the result from IBM Watson
            list_of_scores_and_classes = refine_classes(result_from_IBM_Watson['images'][0]['classifiers'][0]['classes'])
            bot_say = parse_classify(list_of_scores_and_classes)
    cache_bot_img(bot_say, imageUrl)
    if get_cached_username() == False:
        return index()
    return render_template('analyze.html', bot_say = bot_say, imgURL=imageUrl, user_name = get_cached_username())

def parse_faces(list_of_faces):
    '''
    parsing list_of_faces['age'], list_of_faces['gender'], list_of_faces['identity']
    '''
    faces_found = []

    #list_of_faces is a list of dictionaries containing info about the different face(s) found in the image
    #go thru each dictionaries in the list
    for x in range(0, len(list_of_faces)):
        #if the current dictionary has key 'identity'
        if 'identity' in list_of_faces[x]:
            #add that 'famous' person to faces_found
            faces_found.append(list_of_faces[x]['identity']['name'])
        else:
            #if current dictionary is not representing a 'famous' person
            #then, use age range to classify the male or female
            faces_found.append(classify_age(list_of_faces[x]['age']['max'], list_of_faces[x]['age']['min'], list_of_faces[x]['gender']['gender']))
    return ", ".join(faces_found)

def parse_classify(list_of_scores_and_classes):
    classes_in_string = ", ".join(dictionary['class'] for dictionary in list_of_scores_and_classes)
    return "Here's what I see this photo: " + classes_in_string + "."

def classify_age(age_max, age_min, gender):
    if age_min < 12:
        return "a little boy" if gender == "MALE" else "a little girl"
    elif age_min >= 12 and age_max <= 17:
        return "a teenage boy" if gender == "MALE" else "a teenage girl"
    elif age_min >= 18 and age_max <= 24:
        return "a young guy" if gender == "MALE" else "a young lady"
    elif age_min >= 25 and age_max <= 35:
        return "a young man" if gender == "MALE" else "a young woman"
    else:
        return "a old man" if gender == "MALE" else "a old woman"

def refine_classes(list_of_scores_and_classes):
    #get rid of classes with more than one word
    list_of_scores_and_classes = [dictionary for dictionary in list_of_scores_and_classes if " " not in dictionary['class']]
    #extract nouns in the list of scores and classes
    for dictionary in list_of_scores_and_classes:
        s = wordnet.synsets(dictionary['class'])[0]
        if s.pos != "NN":
            del list_of_scores_and_classes[list_of_scores_and_classes.index(dictionary)]
    #get rid of words that are plural/singular of other words
    for dictionary in list_of_scores_and_classes:
        #get index of the current dictionary
        x = list_of_scores_and_classes.index(dictionary) + 1
        #go thru the rest of the list from the index of the current dictionary
        while x != len(list_of_scores_and_classes):
            #is the current dictionary the same as the plural or singular of other dictionarys?
            if dictionary['class'] == pluralize(list_of_scores_and_classes[x]['class']) or dictionary['class'] == singularize(list_of_scores_and_classes[x]['class']):
                #if yes, which dictionary has higher score (greater chance of predicting that the dictionary is the image)
                #remove dictionary with lower score
                if int(dictionary['score']) > int(list_of_scores_and_classes[x]['score']):
                    del list_of_scores_and_classes[x]
                #if current dictionary has lower score, delete it and move to next dictionary
                else:
                    del list_of_scores_and_classes[list_of_scores_and_classes.index(dictionary)]
                    continue
            x += 1
    return list_of_scores_and_classes

if __name__ == "__main__":
    app.run()
