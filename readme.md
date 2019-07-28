# slack-demo-heroku

This is a simple Slack app for showing how to implement the OAuth installation based on Flask and Slackclient.

This app can respond to slash commands and has a simple webpage for installing it to a workspace. Tokens are stored in a local JSON file.

## Setup

Here is a brief overview how to setup this app with Heroku:

Create a new Slack app

Create a new Heroku app

Clone this repo to your system and deploy it to your new Heroku app

Set the client ID and client secret of your Slack app as config variables in Heroku:

```bash
heroku config:set SLACK_CLIENT_ID=XXX
heroku config:set SLACK_CLIENT_SECRET=YYYY
```

Configure your Slash app as follows:

1. Slash commands: create new command (e.g. `/testapp`) and link it to `https://your-app.herokuapp.com/slash`

2. Ouath & Permission: Add permission: `users:read`

3. Ouath & Permission: Add redirect URL set to `https://your-app.herokuapp.com/finish_auth`

4. Manage Distribution: Activate

Optionally you can add `https://your-app.herokuapp.com` as your installation landing page to your Slack app.

You can now install your Slack app to additional workspaces via this link: https://your-app.herokuapp.com

## Technical details

This apps implements a slash command and makes a call to the Slack API to get the real name of the user that issues the slash command.

In addition this app implements a simple web page with a link to enable installation to a Slack workspace.

The workspace related token is stored in a local JSON file.
