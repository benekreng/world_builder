- make sure you are in world_builder\backend to run the code 
- if you are not using a launch.json enter in terminal with venv activated: uvicorn api.main:app --reload  (this will start the FASTAPI server)
- click in terminal on the localhost link, brwoser window will open 
- to see the swagger page of the fastapi backend add /docs in the url like this -> http://127.0.0.1:8000/docs
- now you can see and test the available three endpoints:
1. use the endpoint generate-map to trigger an llm request; copy prompt string as a Json escaped string, use formatter website to convert, endpoint will return task id
2. use endpoint task and provide task id to ask for status or result  

