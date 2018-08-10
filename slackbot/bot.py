import os
import time
import jenkins
import requests
from slackclient import SlackClient

# Function to get bot information and infinite loop for listen
def get_bot_id():
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == bot_name:
                return "<@" + user.get('id') + ">"

        return None

def listen():
    if slack_client.rtm_connect(with_team_state=False):
        print "Successfully connected, listening for commands"
        while True:
            wait_for_event()
            time.sleep(1)
    else:
        exit("Error, Connection Failed")

# POST info to bot
def wait_for_event():
    events = slack_client.rtm_read()

    if events and len(events) > 0:
        for event in events:
            # print event
            parse_event(event)

def parse_event(event):
    if event and 'text' in event and bot_id in event['text']:
        entry = event['text'].split(bot_id)[1].strip().lower()
        command = entry.split()
        if len(entry.split()) == 1:
            handle_event(event['user'], command[0], event['channel'], None)
        else:
            handle_event(event['user'], command[0], event['channel'], command[1])

def handle_event(user, command, channel, app):
    if command and channel:
        if app is None:
            print "Received command: " + command + " in channel: " + channel + " from user: " + user
        else:
            print "Received command: " + command + " in channel: " + channel + " from user: " + user  + " for application: " + app

        response = handle_command(user, command, channel, app)
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

# Function for handling command with response
def handle_command(user, command, channel, app):
    response = "<@" + user + ">: "
    if command in commands:
        if command == "help":
            response += help()
        else:
            if app in applications:
                response += commands[command](app)
            else:
                if app == None:
                   response += "*No application name is entered*" + help()
                else:
                    response += "*Sorry, There is no application name: " + app + "*" + help()
    else:
      response += "*Sorry I don't understand the command: " + command + "*"+ ". " + help()
    return response

# Command for commands operations
def help():
    response = "\r\n*Currently support the following commands:*\r\n"
    for command in commands:
        response += command + "\r\n"
    response += "\r\n*Currently support the following Applications:*\r\n"
    for app in applications:
        response += app + "\r\n"
    return response

def start(app):
    jenkins_client.build_job(app, { 'ops': 'start' })
    last_build_number = jenkins_client.get_job_info(app)['lastCompletedBuild']['number']
    response = str(jenkins_client.get_build_info(app, last_build_number))
    return response

def restart(app):
    jenkins_client.build_job(app, { 'ops': 'restart' })
    last_build_number = jenkins_client.get_job_info(app)['lastCompletedBuild']['number']
    response = str(jenkins_client.get_build_info(app, last_build_number))
    return response

def stop(app):
    jenkins_client.build_job(app, { 'ops': 'stop' })
    last_build_number = jenkins_client.get_job_info(app)['lastCompletedBuild']['number']
    response = str(jenkins_client.get_build_info(app, last_build_number))
    return response

def status(app):
    jenkins_client.build_job(app, { 'ops': 'status' })
    last_build_number = jenkins_client.get_job_info(app)['lastCompletedBuild']['number']
    response = str(jenkins_client.get_build_info(app, last_build_number))
    return response

# Slack information
slack_client = SlackClient(os.environ.get('SLACK_API_TOKEN'))
bot_name = "biscuitops"
bot_id = get_bot_id()

# Jenkins information || Make sure below values are set on server
jenkins_host = "http://" + os.environ.get('JENKINS_HOST') + ":" + os.environ.get('JENKINS_PORT')

jenkins_client = jenkins.Jenkins(jenkins_host, username=os.environ.get('JENKINS_USER'), password=os.environ.get('JENKINS_TOKEN'))

# Application and Services
commands = {
    "start": start,
    "stop" : stop,
    "restart": restart,
    "status" : status,
    "help": help
}

applications = []
for job in jenkins_client.get_all_jobs():
  applications.append(str(job["name"]).lower())
# applications = [str(items) for items in applications]
print applications
# applications = ["alpha", "beta", "gamma" ]

listen()