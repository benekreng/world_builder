### Explanation of the backend structure 

We have a world_engine package where our main app lives. It has a seperate main entrypoint
for launching it without fast api.
We have an api package where our fast api lives and its main.py is the entry points of the entire backend.
It is launched by docker. Fast api instanciates our world builder app and orchestrates it through api calls.
For development and testing functionatliy of our app we dont want to prematurely make api endpoints for whatever
we are testing so more often than not we would launch the app by itself throught he main.py in world_builder.

(The current structure is very reasonable for our size of project although it can be argued
that fast api doesnt have to have in its own package and could just live a a main.py in world builder 
but in case it gets big and to avoid futuer headache I made it seperate)

> tree
.
├── api
│   ├── __init__.py
│   └── main.py # fast api entry point, launched by univcorn
├── docker-compose.yaml
├── Dockerfile
├── dockerless_setup_env.sh # quick setup for local env
├── proto_main.py
├── notebooks # jupyter notebooks
├── README.md
├── requirements.txt
└── world_builder # main app package
    ├── __init__.py
    ├── app.py # app entry point, core runtime logic, bread and butter
    ├── main.py # main to run app without fast api
    ├── models.yaml # easy definition of llm endpoints
    └── router.py # llm endpoint abstraction

### Run docker
1. Start docker daemon
2. docker compose build
3. docker compose up
4. access via http://0.0.0.0:8000/

Docker now launches fast api which launches the app.
Personally for development I prefer to work locally cause the logs are L with docker but you do you

### OLD --- Setup local python env
Run setup_env.sh for quick setup.
To run add execute privledge:
> sudo chmod +x ./setup_env.sh

Otherwise: 

Have python installed. Check with:
> which python3

Setup virtual environment: 
> python3 -m venv .venv

Install packages via requirements.txt
> pip install -r requirements.txt

Set api key:
> export OPEN_ROUTER_API_KEY="key goes here"