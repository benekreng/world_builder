- make sure you are in world_builder\backend to run the code 
- if you are not using a launch.json enter in terminal with venv activated: uvicorn api.main:app --reload  (this will start the FASTAPI server)
- click in terminal on the localhost link, brwoser window will open 
- tto see the swagger page of the fastapi backend add /docs in the url like this -> http://127.0.0.1:8000/docs
- now you can see and test the available endpoint
- if you want to test the generate-map api endpoint make sure to enter the prompt string as a Json escape string, use formatter website to convert 

