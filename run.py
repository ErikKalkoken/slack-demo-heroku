from flask import Flask, json, request

app = Flask(__name__) #create the Flask app

@app.route('/slash', methods=['POST'])
def slash_response():                
    """ endpoint for receiving all slash command requests from Slack """

    # create response
    user_id = request.form.get("user_id")
    response = json.jsonify({
        "text": "Hi <@" + user_id + ">! How is it going?"
    })

    ## convert response message into JSON and send back to Slack
    return response

if __name__ == '__main__':
    app.run(debug=True, port=8000) #run app in debug mode on port 8000
