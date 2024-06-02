# Getting Started
We used React Native and python-flask technologies for this app.

Since this is a app running on local. We need to learn our ip adress and path of app.

# Start your Application
You can run the Python side by customizing and running the following command in the terminal.

python main.py --host 192.168.1.2 --port 5000 --path /some/path/to/data

For mobile part we need to customize ipAddress and host variables on screens/Home.js file on lines 8-9.
Then we can run app with "npx react-native run-android"
