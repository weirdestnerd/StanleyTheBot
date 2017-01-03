from flask import Flask, render_template, request
import json
from pattern.en import wordnet
from watson_developer_cloud import VisualRecognitionV3

visual_recognition = VisualRecognitionV3('2016-05-20', api_key='c6f25fcfd00c3ad03ffa283a79eb2e5490874d02')

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('intro.html')

@app.route("/analyize", methods=['GET', 'POST'])
def img_upload():
    #imageUrl = request.form['hiddenUrl']
    imageUrl = 'https://firebasestorage.googleapis.com/v0/b/stanleythebot-8c6b0.appspot.com/o/images%2Falan-frog.jpg?alt=media&token=07b803f8-388d-43f6-bee3-db00e098a05f'
    regc = json.dumps(visual_recognition.classify(images_url=imageUrl), indent=2)
    return render_template('info.html', regc=regc, imgUrl=imageUrl)
if __name__ == "__main__":
    app.run()
