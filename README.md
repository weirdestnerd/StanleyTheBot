

# StanleyTheBot
## intro
StanleyTheBot is a simple Python web-app that serves as a image recognition chat-bot.
The app simply asks for the name of the user, then asks the user for a photo to classify.

## background
I've always had great interest in Artificial Intelligence and I have strive to thrive in this field. In my endeavor to understand A.I., I realized that Python is one of the major programming languages in the field. So, I decided to learn Python >at least the basics. After getting a comfortable with the basics of Python, I wanted to build a simple program with Python that relates to A.I. Thereby, I created StanleyTheBot.

## backbone
The base of StanleyTheBot is **Flask** and **Jinja**. **Flask** framework handles the dynamicity of the app: redirection of pages, variables in HTML.
Images are classified with **IBM Watson Visual Recognition API**.
**Firebase** storage is used to store the images uploaded.
UI is done with **MaterializeCSS**.
StanleyTheBot is deployed to **Heroku** [StanleyTheBot.herokuapp.com](https://StanleyTheBot.herokuapp.com).

## walkthrough
The main python file that controls the app is `index.py`.
All the web pages in this app are in `templates` folder.
`Static` folder holds other files that are used in the HTML pages.
The following files are used for deploying the app to Heroku:
- `_pycache_`
- `config.py`
- `config.pyc`
- `Procfile`
- `requirements.txt`
- `settings.py`

## demo
1. Stanley introduces itself and asks for user's name.
2. User provides a non-empty name.
3. Stanley mentions its purpose.
4. User picks a photo.
5. Stanley uploads the photo to Firebase storage.
6. Link to photo is received from Firebase.
7. IBM Watson uses the link to access photo.
8. IBM Watson returns a dictionary.
9. Stanley processes the dictionary.
10. Stanley replies user with processed result.
