from http.server import BaseHTTPRequestHandler, HTTPServer
#from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import re
import pymongo
from datetime import datetime, timedelta
import random
import os
import boto3
import socket


my_hostname = socket.gethostname()
my_ip = socket.gethostbyname(my_hostname)

client = pymongo.MongoClient("")
mydb = client["Cloud-Computing"]
aws_access_key_id = ""
aws_secret_access_key = ""
BUCKET_NAME = "6998project"


def s3setup():
    global aws_access_key_id, aws_secret_access_key, BUCKET_NAME
    
    session = boto3.Session(aws_access_key_id = aws_access_key_id,
                            aws_secret_access_key = aws_secret_access_key,
                            )
                            
    s3 = session.resource('s3')
    return s3

def processimg(img_in, s3, IsColorize = True, IsStyle = True,):
AKIAJCCF7ONELNKCD5KA
    style_list = ["wave", "scream", "la_muse", "rain_princess", "udnie", "wreck"]

    if IsStyle:
        (filename, extension) = os.path.splitext(img_in)
        
        for style in style_list:
            img_out = filename + "_" +style + extension
            style = style + '.ckpt'
            os.system("bash style.sh "+ img_in + " " + img_out + " " + style )
            s3.Bucket(BUCKET_NAME).upload_file(img_out, img_out)
            os.remove(img_out)

    if IsColorize:
        (filename, extension) = os.path.splitext(img_in)
        img_out = filename + "_colorized" + extension
        os.system("bash colorize.sh " + img_in + " " + img_out)
        s3.Bucket(BUCKET_NAME).upload_file(img_out, img_out)
        os.remove(img_out)
    print("Successfully processed incoming image " + img_in)




# HTTPRequestHandler class
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):

    # GET
    def do_POST(self):
        # Send response status code
        self.send_response(200)
        # Send headers
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        body = body.decode('utf-8')
        temp = body.split('&')
        user = temp[0].split('=')[1]
        image = temp[1].split('=')[1]

        #s3 = s3setup()
        global s3        
        s3.Bucket(BUCKET_NAME).download_file(image, image)
        processimg(img_in = image, s3 = s3)
        os.remove(image)        

        '''
        s3 download img_in
        img_out = process(img_in, ),
        upload img_out
        
        
        '''
        
        #process images here
        photorecord = mydb["photos"]
        photorecord.update_one({'user':user, 'unprocess':image}, {'$set':{'status':True}})
        return


def run():
    print('starting server...')
    

    # Server settings
    # Choose port 8080, for port 80, which is normally used for a http server, you need root access
    server_address = (my_ip, 8080)
    httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
    print('running server...')
    httpd.serve_forever()

s3 = s3setup()
run()




