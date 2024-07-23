import requests
import requests.auth
import logging.config
import os
import base64
import traceback
import threading

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from PIL import Image
from io import BytesIO

from src.log import logConfiguration

logging.config.dictConfig(logConfiguration)
infoLog = logging.getLogger('infoLog')

tokenURL = 'https://python-course.lat/image-app/api-token-auth/'
imageURL = 'https://python-course.lat/image-app/images/'
username = 'user'
password = 'python22024!'

def getToken():
    """
    This function obtains an authentication token from the specified token URL.

    **Args:**
        
    **Returns:**
       The authentication token if successful, otherwise None.
    """
    try:
        authentication = {
            'user': username,
            'password': password
        }
        response = requests.post(tokenURL, json=authentication)
        if response.status_code == 200:
            token = response.text
            infoLog.info(f"Token successfully taken. Token:{token}")
            return token
        else:
            print(f"ERROR: Failed to obtain the token. Error code: {response.status_code}")
            print(f"ERROR: {response.json()}")
            infoLog.error(f"Failed to obtain the token. Error code: {response.status_code}, {response.json()}")
            return None
    except requests.exceptions.RequestException as error:
        print(f"ERROR: {error}")
        infoLog.error(f"Failed to obtain the token. Error code: {response.status_code}, {response.json()}, error:{error}")
        return None
    except Exception as error:
        print(f"ERROR:{error}")
        infoLog.error(f"Failed to obtain the token. Error code: {response.status_code}, {response.json()}, error:{error}")
        return None

def downloadImage(newImageURL, imagePath):
    """
    This function downloads an image from a given URL and save it to the specified path.

    **Args:**
        newImageURL: The URL of the image to be downloaded.
        imagePath: The path where the image will be saved.
        
    **Returns:**
    """
    try:
        imageResponse = requests.get(newImageURL)
        if imageResponse.status_code == 200:
            imageContent = imageResponse.content
            with BytesIO(imageContent) as image:
                with open(imagePath, 'wb') as imageOut:
                    imageOut.write(image.read())
    except Exception as error:
        print(f"INFO: Failed to download image: {newImageURL}, error message: {error}")
        infoLog.info(f"Failed to download image: {newImageURL}, error message: {error}", traceback.format_exc())

def imageNumThread(token, imageNumInt):
    """
    This function downloads a specified number of images using multithreading.

    **Args:**
        token: The authentication token.
        imageNumInt: The number of images to download.
        
    **Returns:**
    """
    token = token[1:-1]
    try:
        postHeaders = {
          'Authorization': f'Bearer {token}',
        }
        payload = {
            "cantidad" : int(imageNumInt)
        }
        response = requests.post(imageURL, headers=postHeaders, json=payload)
        if response.status_code == 200:
            try:  
                images = response.json()
                print(f"INFO: Downloading {len(images)} images, please wait...")
                threads = []
                for i, newImageURL in enumerate(images):
                    imagePath = os.path.join('images', f'image_{i + 1}.jpg')
                    thread = threading.Thread(target=downloadImage, args=(newImageURL, imagePath))
                    threads.append(thread)
                    thread.start()
                
                for thread in threads:
                    thread.join()
                    
                print(f"INFO: Successfully saved {len(images)} images. Images saved in folder \"images\"")
                infoLog.info(f"Successfully saved {len(images)} images. Images saved in folder \"images\"")
                # os.system("PAUSE")       
            except Exception as error:
                print(f"ERROR: {error}, error code: {response.status_code}")
                infoLog.error(f"Failed to obtain the images in the POST call(imageNum). Error code: {response.status_code}, {response.json()}, error:{error}")
        else:
            print(f"ERROR: Failed to obtain images. POST fail error code: {response.status_code}")
            print(f"ERROR: {response.json()}")  
            infoLog.error(f"Failed to obtain the images in the POST call(imageNum). Error code: {response.status_code}, {response.json()}")
    except requests.exceptions.RequestException as error:
        print(f"ERROR: {error}, error code: {response.status_code}")      
        infoLog.error(f"Failed to obtain the images in the POST call(imageNum). Error code: {response.status_code}, {response.json()}, error:{error}")
    except Exception as error:
        print(f"ERROR: {error}, error code: {response.status_code}")
        infoLog.error(f"Failed to obtain the images in the POST call(imageNum). Error code: {response.status_code}, {response.json()}, error:{error}")

def sendEmail(emailString):
    """
    This function sends an email with the modified images attached.

    **Args:**
        emailString: The recipient's email address.
        
    **Returns:**
    """
    try:
        email = MIMEMultipart()
        email['From'] = 'Luis Alfaro <solera.luis12@gmail.com>'
        email['To'] = f'{emailString}'
        email['Subject'] = 'Modified images'

        imgSource = 'images'
        imgFiles = os.listdir(imgSource)
        totalImages = len(imgFiles)
        
        userLogsPath = "logs/modificationsList.txt"
        txtContent = ""
        
        try:
            with open(userLogsPath, 'r') as txtFile:
                txtContent = txtFile.read()
        except FileNotFoundError:
            print(f"Error: The file '{userLogsPath}' does not exist.")
            infoLog.error(f"The file '{userLogsPath}' does not exist.")
        except Exception as error:
            print(f"ERROR: Unable to read the file {userLogsPath}.")
            infoLog.error(f"Unable to read the file. Error message: {error}\n", traceback.format_exc())
    
        body = f'''Good morning,

This is the email generated by the modify images program.

Total number of images: {totalImages}

Below are the list of modifications donde to each image:
{txtContent}

All the images were attached.

Regards,
System.
'''
        email.attach(MIMEText(body, 'plain'))

        requirementsTXT = MIMEText(txtContent)
        requirementsTXT.add_header('Content-Disposition', 'attachment', filename='requirements.txt')
        email.attach(requirementsTXT)

        for imgFile in imgFiles:
            with open(os.path.join(imgSource, imgFile), 'rb') as image:
                downloadedImg = MIMEBase('image', 'octet-stream')
                downloadedImg.set_payload(image.read())
                encoders.encode_base64(downloadedImg)
                downloadedImg.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{imgFile}"'
                )
                email.attach(downloadedImg)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(user='solera.luis12@gmail.com', password='cmefajxesraeorzt')
        server.sendmail('solera.luis12@gmail.com', 'solera.luis12@gmail.com', email.as_string())
        server.quit()
        print(f"INFO: Email sent successfully to {emailString}.")
        infoLog.info(f"Email sent successfully to {emailString}")

    except smtplib.SMTPAuthenticationError:
        print("ERROR: Unable to authenticate with the SMTP server. Check the username and password.")
        infoLog.error(f"Unable to authenticate with the SMTP server. Check the username and password\n", traceback.format_exc())
    except smtplib.SMTPException as error:
        print("ERROR: Unable to send email.")
        infoLog.error(f"Unable to send email. Error message: {error}\n", traceback.format_exc())
    except Exception as error:
        print("ERROR: An unexpected error occurred.")
        infoLog.error(f"An unexpected error occurred. Error message: {error}\n", traceback.format_exc())

def sendEmailThread(emailString):
    """
    This function sends an email with the modified images attached using a separate thread.

    **Args:**
        emailString: The recipient's email address.
        
    **Returns:**
    """
    try:
        thread = threading.Thread(target=sendEmail, args=(emailString,))
        thread.start()

    except Exception as error:
        print("ERROR: An unexpected error occurred.")
        infoLog.error(f"An unexpected error occurred. Error message: {error}\n", traceback.format_exc())