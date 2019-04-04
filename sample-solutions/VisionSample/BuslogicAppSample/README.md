# aicameraBuslogicSample
This is the code that uses microsoft aicamera and develop business logic such that it describe the object of interest and whenever the objec to fo interest is detected by camera an email is send to it user.
Prerequiste ::
https://docs.microsoft.com/en-us/azure/iot-edge/how-to-vs-code-develop-module

How to run this sample 
1. clone the sample 
2. change .env file with your azure acr credentials 
Optional change your email and object of interest in main.py and deployment.template.json to the Object that you like to track from 99 Coco data set objects as listed here 
    https://tech.amikelive.com/node-718/what-object-categories-labels-are-in-coco-dataset/

3. Build and push to your acr using deployment.template.json as explained in details here 
4. Once it is runing change you twin property to match what ever email you want to use to get alerts and also what Object you want to track, by default it track object = "person" and send email to email = "tomyaicamera@gmail" if you need to access this gmail account send me an email..

more details please watch this video 
https://msit.microsoftstream.com/video/c7339103-d65b-4b5c-a119-be16d7d19434?list=studio

