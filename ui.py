import os
from werkzeug.utils import secure_filename
import cv2 as cv
from flask import Flask, redirect, render_template, request
from guiAPI import guiAPI
import subprocess
import merge_logs as merge

#log files to be merged
log_file1 = "ui.log" # saved logs from the ui
log_file2 = "app.log" # saved logs from the main processing on the cloud
merged_log_file = "full.log" # all logs

# azure storage account credentials
storage_account = "datastorageimg" 
container_name = "logs"
log_file_name = "app.log"
destination_path = "app.log"  # Destination path where the log file will be saved
account_key = "" # <--- insert storage account password

os.environ["PYOPENCL_CTX"] = ""
api = guiAPI()
operations=["Gray","Brighten","Darken","Threshold"]
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

# function that download the app.log file from the azure storage account using the credentials provided above
def download_log_from_azure(storage_account, container_name, log_file_name, destination_path, account_key):
    try:
        # Construct the Azure CLI command to download the log file
        command = f"az storage blob download --account-name {storage_account} --container-name {container_name} --name {log_file_name} --file {destination_path} --account-key {account_key}"
        subprocess.run(command, shell=True, check=True)
        print("Log file downloaded successfully from Azure Storage.")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading log file from Azure Storage: {e}")

@app.route("/",methods=['GET','POST'])
def index():
    images = list_images_in_folder(app.config['UPLOAD'])
    outputImages = list_images_in_folder(app.config['OUTPUT'])
    
    # Read log entries from the full.log file
    with open(merged_log_file, 'r') as file:
        log_entries = file.readlines()
    
    return render_template('index.html', images=images, outputImages=outputImages, operations=operations, log_entries=log_entries)

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
    # Clear or create the log file
    with open('ui.log', "w"):
        pass  
    inputImages=list_images_in_folder(app.config['UPLOAD'])
    selectOp=request.form.get("Operation")
    #Only 1 image will be processed for now
    inputIm=cv.imread(inputImages[0])
    processedImage=api.processImage(inputIm,selectOp)
    # get app.log file from the cloud
    download_log_from_azure(storage_account, container_name, log_file_name, destination_path, account_key)
    
    # merge app.log and ui.log and sort them to get the full final log which will be displayed on the gui
    merge.merge_and_sort_logs(log_file1, log_file2, merged_log_file)
    
    print(os.path.join(app.config['OUTPUT'],"out1.png"))
    cv.imwrite(os.path.join(app.config['OUTPUT'],"out1.png"),processedImage)
    return redirect("/")

# Ensure the Flask app runs when this script is executed directly
if __name__ == "__main__":
    app.run()
    
