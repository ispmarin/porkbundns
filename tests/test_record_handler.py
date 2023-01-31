import requests
import httpretty

@httpretty.activate
def test_call_api_create():
    # define your patch:
    httpretty.register_uri(httpretty.GET, "http://yipit.com/",
                        body="Find the best daily deals")
    # use!
    response = requests.get('http://yipit.com')
    assert response.text == "Find the best daily deals"
