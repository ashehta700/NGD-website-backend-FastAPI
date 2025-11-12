to run go to the directory Fast API
and then run this command 
# $ uvicorn app.main:app --reload 


# to install it on the the docker 



1- docker login to my repo 
$ docker login ghcr.io -u ashehta700

2- this is the key of the application i have 
key = env(key)

3- pull the lastest version for the image  from my github after login to the docker with my id 
$ docker pull ghcr.io/ashehta700/fastapi-app:latest

4- install the new one with the file .env new and the path of the static folder 
PS C:\Users\asheh> docker run -d --name fastapi_app `
>>   --env-file "D:\my main laptop\Geo Makanii\SGS project\Website Backend\Fast API\app\.env" `
>>   -p 8000:8000 `
>>   -v D:\static_fast_api:/app/static `
>>   ghcr.io/ashehta700/fastapi-app:latest

# for update in images on github
5- stop the last one ?
$ docker stop fastapi_app
6- remove the last one ?
$ docker rm fastapi_app