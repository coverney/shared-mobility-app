# App Installation Guide

## Clone GitHub repository
Clone GH repo using GitHub Desktop or using a terminal window. In a terminal, navigate to the location where you want the app to be and type
```
git clone https://github.com/coverney/shared-mobility-app.git
```

## Satisfying the requirements
To run the React web app, you need to install three packages on your machine
- [Node.js](https://nodejs.org/en/): the JavaScript runtime that you will use to run your frontend project
- [Yarn](https://yarnpkg.com/getting-started/install): a package and project manager for Node.js applications
- [Python](https://www.python.org/downloads/): a recent Python 3 interpreter to run the Flask backend on

Follow the links to install the packages you need for your operating system!

## Install frontend dependencies
Before we can view the React web page, we need to install all of the dependencies. This can be done by navigating to the `shared-mobility-app/shared-mobility-app` folder in a terminal and then typing `yarn install`.  

## Creating a Python virtual environment within the Flask API
It's good programming practice to create a virtual environment when using Python, so you have full control over which Python packages to install. The following instructions explain how to set up the virtual environment in a terminal window and install the necessary packages to run the backend API:
1. Navigate to the `shared-mobility-app/shared-mobility-app/api` folder via `cd api`
2. Create a Python 3 virtual environment
  - Windows: `python -m venv venv`
  - Unix-based OS: `python3 -m venv venv`
3. Activate `venv`
  - Windows: `venv\Scripts\activate`
  - Unix-based OS: `source venv/bin/activate`
4. Install Python packages specified in `requirements.txt` within `venv` via `pip install -r requirements.txt`
5. The Flask API should be ready to go! You can exit out of the `venv` through the `deactivate` command

## Running the app
Reference [here](shared-mobility-app/README.md) for instructions on how to run the React app on your local machine
