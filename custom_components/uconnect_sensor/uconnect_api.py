import requests
import boto3
import json
import datetime
from base64 import b64encode

from aws_requests_auth.aws_auth import AWSRequestsAuth

from uuid import uuid4


class Uconnect_API:
    def __init__(self, username: str, password: str, pin: str) -> None:
        self._user = username
        self._passw = password
        self._pin = pin
        self._loginApiKey = (
            "3_mOx_J2dRgjXYCdyhchv3b5lhi54eBcdCTX4BI8MORqmZCoQWhA0mV2PTlptLGUQI"
        )
        self._apiKey = "2wGyL6PHec9o1UeLPYpoYa1SkEWqeBur9bLsi24i"
        self._loginUrl = "https://loginmyuconnect.fiat.com"
        self._tokenUrl = "https://authz.sdpr-01.fcagcv.com/v2/cognito/identity/token"
        self._apiUrl = "https://channels.sdpr-01.fcagcv.com"
        self._authApiKey = "JWRYW7IYhW9v0RqDghQSx4UcRYRILNmc8zAuh5ys"
        self._authUrl = "https://mfa.fcl-01.fcagcv.com"
        self._locale = "de_de"
        self._cookies = None

        """
            needs to be filled
        """
        self._login_token = ""
        self._user_id = ""
        self._jwt_token = ""
        self._identity_id = ""
        self._identity_token = ""

        self._login_default_params_dict = {
            "targetEnv": "jssdk",
            "loginMode": "standard",
            "sdk": "js_latest",
            "authMode": "cookie",
            "sdkBuild": "12234",
            "format": "json",
            "APIKey": self._loginApiKey,
        }

        self._aws_default_params_dict = {
            "x-clientapp-name": "CWP",
            "x-clientapp-version": "1.0",
            "clientrequestid": uuid4().hex,
            "x-api-key": self._apiKey,
            "locale": self._locale,
            "x-originator-type": "web",
        }

    def login(self) -> str:
        """Login to api"""
        parameter = self._login_default_params_dict.copy()
        parameter["apiKey"] = self._loginApiKey

        session = requests.session()

        r = session.get(f"{self._loginUrl}/accounts.webSdkBootstrap", params=parameter)
        self._cookies = requests.utils.dict_from_cookiejar(session.cookies)

        return r.text

    def auth_response(self) -> str:
        """
        auth Response
        """
        parameter = self._login_default_params_dict.copy()
        parameter["loginID"] = self._user
        parameter["password"] = self._passw
        parameter["sessionExpiration"] = 86400
        parameter["include"] = "profile,data,emails,subscriptions,preferences"

        session = requests.session()

        r = session.get(
            f"{self._loginUrl}/accounts.login", params=parameter, cookies=self._cookies
        )

        self._login_token = r.json()["sessionInfo"]["login_token"]
        self._user_id = r.json()["UID"]

        print(f"UID: {self._user_id}")
        return self._user_id

    def get_jwt_token(self) -> str:
        parameter = self._login_default_params_dict.copy()
        parameter[
            "fields"
        ] = "profile.firstName,profile.lastName,profile.email,country,locale,data.disclaimerCodeGSDP"
        parameter["login_token"] = self._login_token

        session = requests.session()

        r = session.get(
            f"{self._loginUrl}/accounts.getJWT", params=parameter, cookies=self._cookies
        )

        self._jwt_token = r.json()["id_token"]

        print(f"JWT Token: {self._jwt_token}")
        return self._jwt_token

    def get_identity_token(self) -> str:
        session = requests.session()

        new_header = self._aws_default_params_dict.copy()
        new_header["content-type"] = "application/json"
        new_header["apiKey"] = self._loginApiKey

        body = {"gigya_token": self._jwt_token}

        r = session.post(self._tokenUrl, headers=new_header, json=body)

        self._identity_id = r.json()["IdentityId"]
        self._identity_token = r.json()["Token"]

        print(f"identityResponse IdentiyId : {self._identity_id} ")
        print(f"identityResponse Token : {self._identity_token} ")

    def get_aws_credentials(self) -> str:
        client = boto3.client("cognito-identity", region_name="eu-west-1")

        response = client.get_credentials_for_identity(
            IdentityId=self._identity_id,
            Logins={"cognito-identity.amazonaws.com": self._identity_token},
        )

        self._aws_access_key = response["Credentials"]["AccessKeyId"]
        self._aws_secret_key = response["Credentials"]["SecretKey"]
        self._aws_session_token = response["Credentials"]["SessionToken"]

        print(f"AccessKeyId: {self._aws_access_key}")
        print(f"SecretKey: {self._aws_secret_key}")
        print(f"SessionToken: {self._aws_session_token}")

    def get_aws_data(self, endpoint: str) -> json:
        new_header = {
            "Host": "channels.sdpr-01.fcagcv.com",
            "content-type": "application/json",
            "x-clientapp-version": "1.0",
            "clientrequestid": uuid4().hex,
            "accept": "application/json, text/plain, */*",
            "x-amz-date": datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
            "x-amz-security-token": self._aws_session_token,
            "locale": self._locale,
            "x-api-key": self._apiKey,
            "accept-language": "de-de",
            "x-clientapp-name": "CWP",
            "origin": "https://myuconnect.fiat.com",
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Mobile/15E148 Safari/604.1",
            "referer": "https://myuconnect.fiat.com/de/de/dashboard",
            "x-originator-type": "web",
        }

        auth = AWSRequestsAuth(
            aws_access_key=self._aws_access_key,
            aws_secret_access_key=self._aws_secret_key,
            aws_token=self._aws_session_token,
            aws_host="channels.sdpr-01.fcagcv.com",
            aws_region="eu-west-1",
            aws_service="execute-api",
        )

        response = requests.get(endpoint, auth=auth, headers=new_header)

        data = json.loads(response.content.decode("utf-8"))

        return data

    def get_aws_data_post(self, endpoint: str, data: str) -> json:
        new_header = {
            "Host": "channels.sdpr-01.fcagcv.com",
            "content-type": "application/json",
            "x-clientapp-version": "1.0",
            "clientrequestid": uuid4().hex,
            "accept": "application/json, text/plain, */*",
            "x-amz-date": datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
            "x-amz-security-token": self._aws_session_token,
            "locale": self._locale,
            "x-api-key": self._apiKey,
            "accept-language": "de-de",
            "x-clientapp-name": "CWP",
            "origin": "https://myuconnect.fiat.com",
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Mobile/15E148 Safari/604.1",
            "referer": "https://myuconnect.fiat.com/de/de/dashboard",
            "x-originator-type": "web",
        }

        auth = AWSRequestsAuth(
            aws_access_key=self._aws_access_key,
            aws_secret_access_key=self._aws_secret_key,
            aws_token=self._aws_session_token,
            aws_host="channels.sdpr-01.fcagcv.com",
            aws_region="eu-west-1",
            aws_service="execute-api",
        )

        response = requests.get(
            endpoint, auth=auth, headers=new_header, data=json.dumps(data)
        )

        data = json.loads(response.content.decode("utf-8"))

        return data

    def post_aws_pin_authenticate(self, pin: str) -> json:
        endpoint = (
            f"{self._authUrl}/v1/accounts/{self._user_id}/ignite/pin/authenticate"
        )

        new_header = {
            "sec-ch-ua": '"Chromium";v="91", " Not A;Brand";v="99", "Google Chrome";v="91"',
            #'Host' : 'channels.sdpr-01.fcagcv.com',
            "Host": "mfa.fcl-01.fcagcv.com",
            "content-type": "application/json",
            "x-clientapp-version": "1.0",
            "clientrequestid": uuid4().hex,
            "accept": "application/json, text/plain, */*",
            "x-amz-date": datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
            "x-amz-security-token": self._aws_session_token,
            "locale": self._locale,
            "x-api-key": self._authApiKey,
            "accept-language": "de,en;q=0.9",
            # "x-clientapp-name": "CWP" ,
            "sec-ch-ua-mobile": "?0",
            "origin": "https://myuconnect.fiat.com",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
            "referer": "https://myuconnect.fiat.com/de/de/dashboard",
            "x-originator-type": "web",
        }

        auth = AWSRequestsAuth(
            aws_access_key=self._aws_access_key,
            aws_secret_access_key=self._aws_secret_key,
            aws_token=self._aws_session_token,
            aws_host="mfa.fcl-01.fcagcv.com",
            aws_region="eu-west-1",
            aws_service="execute-api",
        )

        base64_string = b64encode(pin.encode("ascii")).decode("ascii")

        payload = {"pin": base64_string}

        response = requests.post(endpoint, auth=auth, headers=new_header, json=payload)

        data = json.loads(response.content.decode("utf-8"))

        # print(data)
        self._pin_token = data["token"]
        print(f"PIN_Token: {self._pin_token}")

        return self._pin_token

    def post_aws_command(self, pin: str, vin: str, command: str, action: str) -> json:
        pin_token = self.post_aws_pin_authenticate(pin)

        endpoint = (
            f"{self._authUrl}/v1/accounts/{self._user_id}/vehicles/{vin}/{action}"
        )

        new_header = {
            "Host": "channels.sdpr-01.fcagcv.com",
            "content-type": "application/json",
            "x-clientapp-version": "1.0",
            "clientrequestid": uuid4().hex,
            "accept": "application/json, text/plain, */*",
            "x-amz-date": datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
            "x-amz-security-token": self._aws_session_token,
            "locale": self._locale,
            "x-api-key": self._apiKey,
            "accept-language": "de-de",
            "x-clientapp-name": "CWP",
            "origin": "https://myuconnect.fiat.com",
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Mobile/15E148 Safari/604.1",
            "referer": "https://myuconnect.fiat.com/de/de/dashboard",
            "x-originator-type": "web",
        }

        auth = AWSRequestsAuth(
            aws_access_key=self._aws_access_key,
            aws_secret_access_key=self._aws_secret_key,
            aws_token=self._aws_session_token,
            aws_host="channels.sdpr-01.fcagcv.com",
            aws_region="eu-west-1",
            aws_service="execute-api",
        )

        payload = {
            "command": command,
            "pinAuth": pin_token,
        }

        response = requests.post(endpoint, auth=auth, headers=new_header, json=payload)
        print(response.text)

    #        return self._pin_token

    def fetch_data(self) -> str:
        r = self.login()
        print(f"Login response: {r} ")
        print("-" * 50)
        self.auth_response()
        print("-" * 50)
        self.get_jwt_token()
        print("-" * 50)
        self.get_identity_token()
        print("-" * 50)
        self.get_aws_credentials()
        print("-" * 50)

        ret = self.get_aws_data(f"{self._apiUrl}/v4/accounts/{self._user_id}/vehicles")
        vin = ret["vehicles"][0]["vin"]
        print(f"VIN: {vin}")

        # Status of vehicle
        ret_vehicle = self.get_aws_data(
            f"{self._apiUrl}/v2/accounts/{self._user_id}/vehicles/{vin}/status"
        )

        ret_location = self.get_aws_data_post(
            f"{self._apiUrl}/v1/accounts/{self._user_id}/vehicles/{vin}/location/lastknown",
            "location",
        )

        ret = {
            "status": ret_vehicle,
            "location": ret_location,
        }

        print(json.dumps(ret, indent=4, sort_keys=True))
        # print(ret['evInfo']['battery']['stateOfCharge'])

        return ret  # ['evInfo']['battery']['stateOfCharge']

    def fetch_data_with_payload(self, endpoint: str, payload: str) -> str:
        r = self.login()
        print(f"Login response: {r} ")
        print("-" * 50)
        self.auth_response()
        print("-" * 50)
        self.get_jwt_token()
        print("-" * 50)
        self.get_identity_token()
        print("-" * 50)
        self.get_aws_credentials()
        print("-" * 50)

        ret = self.get_aws_data(f"{self._apiUrl}/v4/accounts/{self._user_id}/vehicles")
        vin = ret["vehicles"][0]["vin"]
        print(f"VIN: {vin}")

        ret = self.get_aws_data_post(
            f"{self._apiUrl}/v1/accounts/{self._user_id}/vehicles/{vin}/{endpoint}",
            payload,
        )

        return ret

    def fetch_location(self):
        return self.fetch_data_with_payload("location/lastknown", "location")

    def post_data(self, command, action) -> str:
        r = self.login()
        print(f"Login response: {r} ")
        print("-" * 50)
        self.auth_response()
        print("-" * 50)
        self.get_jwt_token()
        print("-" * 50)
        self.get_identity_token()
        print("-" * 50)
        self.get_aws_credentials()
        print("-" * 50)

        ret = self.get_aws_data(f"{self._apiUrl}/v4/accounts/{self._user_id}/vehicles")
        vin = ret["vehicles"][0]["vin"]
        print(f"VIN: {vin}")

        # self.post_aws_data(self._pin)

        self.post_aws_command(self._pin, vin, command, action)

        # ret = self.get_aws_data(f'{self._apiUrl}/v2/accounts/{self._user_id}/vehicles/{vin}/status')
        # print(json.dumps(ret, indent=4, sort_keys=True))
        # print(ret['evInfo']['battery']['stateOfCharge'])
        return ret  # ['evInfo']['battery']['stateOfCharge']

    def precond_on(self):
        self.post_data(command="ROPRECOND", action="remote")
