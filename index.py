import os
from flask import Flask, render_template, request
from pattern.en import wordnet, pluralize, singularize
from watson_developer_cloud import VisualRecognitionV3

#instantiates the IBM Watson's visual regconition
visual_recognition = VisualRecognitionV3('2016-05-20', api_key='c6f25fcfd00c3ad03ffa283a79eb2e5490874d02')

app = Flask(__name__)
#app.config.from_object(os.environ['APP_SETTINGS'])

@app.route("/")
def index():
    #show welcome page
    return render_template('intro.html')

@app.route("/get_user_name", methods=['POST'])
def get_user_name():
    user_name = str(request.form['user_name'])
    return render_template('info.html', user_name = user_name)

#analyze given image
@app.route("/analyze", methods=['GET', 'POST'])
def img_upload():
    #get the given image's url (firebase storage url)
    imageUrl = str(request.form['hiddenUrl'])
    #IBM Watson classifies image and returns a dictionary
    result_from_IBM_Watson = visual_recognition.detect_faces(images_url=imageUrl)
    list_of_faces = result_from_IBM_Watson['images'][0]['faces']
    if list_of_faces:
        bot_say = parse_faces(list_of_faces)
    else:
        result_from_IBM_Watson = visual_recognition.classify(images_url=imageUrl)
        #get list of dictionaries containing 'scores' and 'class' from 'result_from_IBM_Watson'
        list_of_scores_and_classes = result_from_IBM_Watson['images'][0]['classifiers'][0]['classes']
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
        bot_say = parse_classify(list_of_scores_and_classes)
    return render_template('analyze.html', bot_say = bot_say, imgURL=imageUrl)

def parse_faces(list_of_faces):
    return "there is face(s) in this photo"

def parse_classify(list_of_scores_and_classes):
    string = ""
    for dictionary in list_of_scores_and_classes:
        string = string + ", " + dictionary['class']
    return "there is " + string + " in this photo"

if __name__ == "__main__":
    app.run()
