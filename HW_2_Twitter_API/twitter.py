from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from requests_oauthlib import OAuth1Session
import os
import json

# creating flask app
app = Flask(__name__)

#  API object creation
CORS(app)
api = Api(app)

my_twitter_key = os.environ.get("MY_TWITTER_KEY")
my_twitter_secret_key = os.environ.get("MY_TWITTER_SECRET_KEY")
GET_USERID_URL = "https://api.twitter.com/2/users/by/username/{}"
GET_ENDPOINT_URL = "https://api.twitter.com/2/users/{}/tweets"
POST_ENDPOINT_URL = "https://api.twitter.com/2/tweets"


class Twitter(Resource):

    def get(self):
        #parameters = {"id": "1569445268529217537"}
        user_name = request.args.get("user_name")


        # get request token
        token_request_url = "https://api.twitter.com/oauth/request_token"
        oauthsession = OAuth1Session(my_twitter_key, client_secret=my_twitter_secret_key)
        try:
            response_fetch = oauthsession.fetch_request_token(token_request_url)
        except ValueError:
            print("Issue with entered twitter key and twitter secret key")

        owner_key = response_fetch.get("oauth_token")
        owner_secret_key = response_fetch.get("oauth_token_secret")
        print("Got OAuth token: %s" % owner_key)

        # Getting Authorization
        twitter_authorization_url = "https://api.twitter.com/oauth/authorize"
        authorization_url = oauthsession.authorization_url(twitter_authorization_url)
        print("Please use the link to authorize: %s" % authorization_url)
        verifier = input("Enter or Paste the PIN here: ")

        # Get the access token
        token_access_url = "https://api.twitter.com/oauth/access_token"
        oauth = OAuth1Session(
            my_twitter_key,
            client_secret=my_twitter_secret_key,
            resource_owner_key=owner_key,
            resource_owner_secret=owner_secret_key,
            verifier=verifier,
        )
        oauth_tokens = oauth.fetch_access_token(token_access_url)
        token_access = oauth_tokens["oauth_token"]
        token_access_secret = oauth_tokens["oauth_token_secret"]

        # Making a request
        oauth = OAuth1Session(
            my_twitter_key,
            client_secret=my_twitter_secret_key,
            resource_owner_key=token_access,
            resource_owner_secret=token_access_secret,
        )
        print(user_name)
        user_id_resp = oauth.get(
            GET_USERID_URL.format(user_name)
        )

        print("Get user id response: {}".format(user_id_resp.json()))

        user_data = user_id_resp.json()
        user_id = user_data["data"]["id"]

        api_response = oauth.get(
            GET_ENDPOINT_URL.format(user_id)
        )

        if api_response.status_code != 200:
            raise Exception(
                "Request returned an error: {} {}".format(api_response.status_code, api_response.text)
            )

        print("Response code: {}".format(api_response.status_code))
        json_response = api_response.json()
        print(json.dumps(json_response, indent=4, sort_keys=True))
        return jsonify(json_response)

    # POST request to create tweet
    def post(self):

        data = request.get_json()

        token_request_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
        oauthsession = OAuth1Session(my_twitter_key, client_secret=my_twitter_secret_key)

        try:
            response_fetch = oauthsession.fetch_request_token(token_request_url)
        except ValueError:
            print("Issue with entered twitter key and twitter secret key")

        owner_key = response_fetch.get("oauth_token")
        owner_secret_key = response_fetch.get("oauth_token_secret")
        print("Got OAuth token: %s" % owner_key)

        # Getting Authorization
        twitter_authorization_url = "https://api.twitter.com/oauth/authorize"
        authorization_url = oauthsession.authorization_url(twitter_authorization_url)
        print("Please use the link to authorize: %s" % authorization_url)
        verifier = input("Enter or Paste the PIN here: ")

        # Get the access token
        token_access_url = "https://api.twitter.com/oauth/access_token"
        oauth = OAuth1Session(
            my_twitter_key,
            client_secret=my_twitter_secret_key,
            resource_owner_key=owner_key,
            resource_owner_secret=owner_secret_key,
            verifier=verifier,
        )
        oauth_tokens = oauth.fetch_access_token(token_access_url)
        owner_token_access = oauth_tokens["oauth_token"]
        owner_token_access_secret = oauth_tokens["oauth_token_secret"]

        # Making a request
        oauth = OAuth1Session(
            my_twitter_key,
            client_secret=my_twitter_secret_key,
            resource_owner_key=owner_token_access,
            resource_owner_secret=owner_token_access_secret,
        )
        tweet_text = {"text": data["tweet_data"]}
        api_response = oauth.post(
            POST_ENDPOINT_URL,
            json=tweet_text,
        )

        if api_response.status_code != 201:
            raise Exception(
                "Request returned an error: {} {}".format(api_response.status_code, api_response.text)
            )

        print("Response code: {}".format(api_response.status_code))

        json_response = api_response.json()
        print(json.dumps(json_response, indent=4, sort_keys=True))
        return jsonify(json_response)


# adding the defined resources along with their corresponding urls
api.add_resource(Twitter, '/twitter-demo')

# main function
if __name__ == '__main__':
    app.run(debug=True)


