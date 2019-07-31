# main module with the Slack app

import os
import slack
from flask import Flask, json, request
import psycopg2

# database connection
DATABASE_URL = os.environ['DATABASE_URL']

# setting oauth client parameters
client_id = os.environ["SLACK_CLIENT_ID"]
client_secret = os.environ["SLACK_CLIENT_SECRET"]
oauth_scope = "commands,users:read"

class SlackTeam:
    """A slack team with its token
    
    Public properties:
        id: team ID
        name: team name
        token: Slack token
    """
    def __init__(self, id, name, token):
        self._id = id[:64]
        self._name = name[:255]
        self._token = token[:255]

    
    @property
    def id(self):
        return self._id


    @property
    def name(self):
        return self._name


    @property
    def token(self):
        return self._token


    def store(self, connection):
        """stores the current object to database. will overwrite existing.

        Args:
            connection: current postgres connection

        Exceptions:
            on any error

        """
        try:                
            cursor = connection.cursor()               
            sql_query = """INSERT INTO slack_teams (id, name, token) 
                VALUES (%s, %s, %s) 
                ON CONFLICT (id)
                DO UPDATE SET name=%s, token=%s"""
            record = (self._id, self._name, self._token, self._name, self._token)
            cursor.execute(sql_query, record)
            connection.commit()
        except (Exception, psycopg2.Error) as error:            
            print("WARN: Failed to insert record into table", error)
            raise error
        finally:
            #closing cursor
            if (cursor):
                cursor.close()                

    @staticmethod
    def fetchFromDb(connection, id):
        """fetches an object from database by its team ID
         
         Args:            
            connection: current postgres connection
            id: team ID of object to be fetched

        Returns:
            the SlackTeam object when found or None if not found
        
        Exceptions:
            on any error
        """
        try:            
            cursor = connection.cursor()
            sql_query = """SELECT id, name, token 
                FROM slack_teams 
                WHERE id = %s"""            
            cursor.execute(sql_query, (id,))            
            record = cursor.fetchone()
            if (record == None):
                print(f"WARN: Could not find a team for ID: {id}")
                obj = None
            else:                
                obj = SlackTeam(record[0], record[1], record[2])
            
        except (Exception, psycopg2.Error) as error :
            print("Error while fetching data from PostgreSQL", error)
            raise
        finally:
            #closing database connection.
            if(cursor):
                cursor.close()

        return obj

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

    try:
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
        team_name = api_response["team_name"]
        access_token = api_response["access_token"]
        
        # store the received token to our DB for later use        
    
        connection = psycopg2.connect(DATABASE_URL)
        team = SlackTeam(
            team_id,
            team_name,
            access_token
        )
        team.store(connection)
        connection.close()
        http = 'Installation completed for workspace ' + team_name
    except (Exception, psycopg2.Error) as error :
        print("ERROR: ", error)
        http = 'Installation failed for workspace ' + team_name
    
    return http


@app.route('/slash', methods=['POST'])
def slash_response():                
    """endpoint for receiving all slash command requests from Slack"""
    
    try:        
        # get token for current workspace
        team_id = request.form.get("team_id")
        connection = psycopg2.connect(DATABASE_URL)
        team = SlackTeam.fetchFromDb(
            connection, 
            team_id
        )    
        connection.close()
        if team is None:
            raise RuntimeError(
                "This app is not properly installed for team " + team_id
                )
                
        # get real name of current user from Slack API
        user_id = request.form.get("user_id")
        print(team.token)
        client = slack.WebClient(token=team.token)
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
    except Exception as error:
        print("ERROR: ", error)
        response = "An internal error occurred"

    ## respond to user
    return response


# to run this flask app locally
if __name__ == '__main__':
    app.run(debug=True, port=8000) 
