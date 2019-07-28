import os
import slack
from flask import Flask, json, request

# file name for local JSON file to store tokens for workspaces
FILENAME_TOKENS = "tokens"

# setting oauth client parameters
client_id = os.environ["SLACK_CLIENT_ID"]
client_secret = os.environ["SLACK_CLIENT_SECRET"]
oauth_scope = "commands,users:read"

# helper functions for reading and writing a dict to a JSON file

def dict_read_from_json_file(filename):
    """reads a json file and returns its contents as dict"""     
    filename += '.json'
    try:
        with open(filename, 'r', encoding="utf-8") as f:
            arr = json.load(f)            
    except Exception as e:
        print("WARN: failed to read from {}: ".format(filename), e)
        arr = dict()

    return arr


def dict_write_to_json_file(arr, filename):
    """writes dict to a json file"""     
    filename += '.json' 
    print("Writing file: name {}".format(filename))
    try:
        with open(filename , 'w', encoding="utf-8") as f:
            json.dump(
                arr, 
                f, 
                sort_keys=True, 
                indent=4, 
                ensure_ascii=False
                )
    except Exception as e:
        print("ERROR: failed to write to {}: ".format(filename), e)   


# flask app

app = Flask(__name__)


@app.route("/", methods=["GET"])
def pre_install():
    """shows the 'Add to Slack' link that will start the the oauth process"""
    url = f'https://slack.com/oauth/authorize?scope={ oauth_scope }&client_id={ client_id }'
    html = f'<a href="{ url }">Add to Slack</a>'
    return html


@app.route("/finish_auth", methods=["GET", "POST"])
def post_install():
    """Exchange to oauth code with a token and store it"""

    # Retrieve the auth code from the request params
    auth_code = request.args['code']

    # An empty string is a valid token for this request
    client = slack.WebClient(token="")

    # Request the auth tokens from Slack
    api_response = client.oauth_access(
        client_id=client_id,
        client_secret=client_secret,
        code=auth_code
    )    
    team_id = api_response["team_id"]
    access_token = api_response["access_token"]
    team_name = api_response["team_name"]

    # store the received token to our local store for later use
    # we are using a JSON file to keep this example simple
    # but this should be a database for any production app
    tokens = dict_read_from_json_file(FILENAME_TOKENS)
    tokens[team_id] = access_token
    dict_write_to_json_file(tokens, FILENAME_TOKENS)

    http = 'Installation completed to workspace ' + team_name
    return http


@app.route('/slash', methods=['POST'])
def slash_response():                
    """endpoint for receiving all slash command requests from Slack"""

    # get token for current workspace
    team_id = request.form.get("team_id")
    tokens = dict_read_from_json_file(FILENAME_TOKENS)
    if team_id not in tokens:
        return "This app is not properly installed."
    token = tokens[team_id]
    
    # get real name of current user from Slack API
    user_id = request.form.get("user_id")
    client = slack.WebClient(token=token)
    api_response = client.users_info(user=user_id)
    assert(api_response["ok"])
    user_info = api_response["user"]
    if "real_name" in user_info:
        user_name = user_info["real_name"]
    else:
        user_name = user_info["name"]
    
    # create response
    
    response = json.jsonify({
        "text": "Hi " + user_name + "! How is it going?"
    })

    ## convert response message into JSON and send back to Slack
    return response


# to run this flask app locally
if __name__ == '__main__':
    app.run(debug=True, port=8000) 
