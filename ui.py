import os
from werkzeug.utils import secure_filename
from flask import Flask, redirect, render_template, request
# import sample

def list_images_in_folder(folder_path):
    image_extensions = [".jpg", ".jpeg", ".png"]  # Add more extensions if needed
    image_files = []

    for file in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file)):
            _, extension = os.path.splitext(file)
            if extension.lower() in image_extensions:
                image_files.append(os.path.join(folder_path, file))

    return image_files

images=[]
app = Flask(__name__,template_folder="templates")
upload_folder = os.path.join('static', 'uploads')
output_folder = os.path.join('static', 'output')
app.config['UPLOAD'] = upload_folder
app.config['OUTPUT'] = output_folder
@app.route("/",methods=['GET','POST'])
def index():
    images=list_images_in_folder(app.config['UPLOAD'])
    outputImages=list_images_in_folder(app.config['OUTPUT'])
    return render_template('index.html', images=images,outputImages=outputImages)

@app.route("/resetImages",methods=['POST'])
def resetImages():
    for file_name in os.listdir(app.config['UPLOAD']):
        file_path = os.path.join(app.config['UPLOAD'], file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
    for file_name in os.listdir(app.config['OUTPUT']):
        file_path = os.path.join(app.config['OUTPUT'], file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
    return redirect("/")

@app.route("/addImage",methods=['POST'])
def addImage():
    file = request.files['img']
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD'], filename))
    return redirect("/")

# @app.route("/output",methods=['POST'])
# def output():
#     return redirect("/")

@app.route("/startProcessing",methods=['POST'])
def startProcessing():
    inputImages=list_images_in_folder("static/uploads")
    #processing
    return redirect("/")
if __name__ == "__main__":
    app.run()