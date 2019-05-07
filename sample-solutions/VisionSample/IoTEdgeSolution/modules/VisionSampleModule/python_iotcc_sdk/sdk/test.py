
import threading
import time
from urllib.request import urlopen
from urllib.request import urlretrieve
import urllib.request as urllib2
import cgi

def GetFile(ModelUrl) :
    #adding code to fix issue where the file name may not be part of url details here 
    #
    remotefile = urlopen(ModelUrl)
    myurl = remotefile.url
    FileName = myurl.split("/")[-1]
    if FileName:
        # find root folders
        dirpath = os.getcwd()
        #src = os.path.join(dirpath,"model")
        dst = os.path.abspath("/app/vam_model_folder")
        print("Downloading File ::" + FileName)
        urllib2.urlretrieve(ModelUrl, filename=(os.path.join(dst,FileName)))
        #WaitForFileDownload(os.path.join(dst,FileName))
        return True
    else:
        print("Cannot extract file name from URL")
        return False
       
def main():

    url = "https://yadavsrorageaccount01.blob.core.windows.net/peabody/model.dlc"#"https://www.gstatic.com/webp/gallery3/2.png"#"http://aka.ms/ai-vision-dev-kit-default-model" #"https://www.gstatic.com/webp/gallery3/2.png"
    
    remotefile = urlopen(url)
    myurl = remotefile.url
    FileName = myurl.split("/")[-1]
    print("filename is :: %s",FileName)


if __name__ == '__main__':
    main()

"""     i=0
    startTime = time.time()
    while(i<100):
       # myThread = threading.Timer(3, f)
       # myThread.start()
        if time.time() - startTime > 3 :
            print("I n 3sec ")
            startTime = time.time()
        print(" I m in Main")
        i = i+1
        time.sleep(1) """