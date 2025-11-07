### Setup environment

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