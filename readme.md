# slack-demo-heroku

This is a simple Slack app for showing how to implement the OAuth installation based on Flask and Slackclient.

This app can respond to slash commands and has a simple webpage for installing it to a workspace. Tokens are stored in a local JSON file.

This app is implemented based on the official python example for [Multiple Workspace Install](https://slack.dev/python-slackclient/auth.html) by Slack. Please refer to that documentation for a more detailed explanation how the OAuth process works with Slack.

## How to setup for Heroku

Here is a brief overview how to setup this app with Heroku:

### 1. Create a new Slack app

Create a new Slack app on your development workspace. You can give it any name. We only need the client ID and client secret for now and will configure it fully later.

### 2. Clone this repo to your local system

In order to deploy this app you first need to clone it to your development system:

```bash
git clone https://github.com/ErikKalkoken/slack-demo-heroku.git
```

### 3. Deploy to Heroku

Create a new Heroku app and deploy this app to it. Make sure you are in the cloned git folder.

```bash
cd slack-demo-heroku
heroku create
git push heroku master

```

### 4. Configure your Heroku app

Set the client ID and client secret of your Slack app as config variables in Heroku:

```bash
heroku config:set SLACK_CLIENT_ID=XXX
heroku config:set SLACK_CLIENT_SECRET=YYYY
```

Next we setup the postgres database:

```bash
heroku addons:create heroku-postgresql:hobby-dev
```

### 5. Configure your Slack app

Configure your Slack app as follows:

- Slash commands:

   create new command (e.g. `/slackdemoheroku`) and link it to `https://your-app.herokuapp.com/slash`

- OAuth & Permission:

   Add permission: `users:read`

   Add redirect URL to `https://your-app.herokuapp.com/finish_auth`

- Manage Distribution: 

   Activate

Optionally you can add `https://your-app.herokuapp.com` as your installation landing page to your Slack app.

### 6. Install your Slack app

The setup is now complete and you can install your Slack app to additional workspaces at this link:

```http
https://your-app.herokuapp.com
```

## How to run locally

To run the app in your local dev environment you need to also set client ID and client secret to your environment variables. Many development environments (e.g. Visual Studio Code) will let you do this comfortable as part of your debug configuration.

In addition you need to run ngrok or another VPN tunnel to expose your local machine to the Internet, so Slack can make requests to it.

In order to avoid having to constantly update your Slack app for switching between environments I recommend to have a Slack app for each environment, e.g. one for Heroku and one for your local dev machine.

## Technical details

This apps implements a slash command and makes a call to the Slack API to get the real name of the user that issues the slash command.

In addition this app implements a simple web page with a link to enable installation to a Slack workspace.

The workspace related token is stored in a local JSON file.

The app uses the standard Python library slackclient to access the Slack API.

The web application is implemented based on Flask and uses Gunicorn on Heroku as web server.
