# `requests` pip package 

## basic request & respsonse operation

- Get Operation

  ```python
  # Passing HTTP Heades into a Python requests.get() Function
  import requests

  url = 'https://httpbin.org/get'
  headers = {'Content-Type': 'text/html'}

  print(requests.get(url, headers=headers))

  # Returns: <Response [200]>
  ```

- Post operation with customized headers

  ```python
  # Passing HTTP Headers into a Python requests.post() Function
  import requests
  resp = requests.post(
      'https://httpbin.org/post', 
      headers={"Content-Type": "application/json"})

  print(resp)

  # Returns: <Response [200]>

  print(resp.headers.get('content-type'))

  # Returns: application/json

  ```

- Serializing a GET Request with .json()

  ```python
  # Serializing a GET Request with .json()
  import requests
  resp = requests.get('https://reqres.in/api/users')
  resp_dict = resp.json()

  print(type(resp_dict))

  # Returns: <class 'dict'>
  ```

## session and cookies

### What is the difference between session and cookies?

>A cookie and a session are used to store information. Cookies are only stored on the client machine, and sessions are stored on both the client and the server. The session creates a file in a temporary directory on the server where the registered session variables and their values ​​are stored. This data will be available for all site pages during this visit. Typically, a session ends 30 minutes after the user leaves the site or closes the browser. Cookies are text files that are stored on the client's computer and are designed to track usage. The server script sends a set of cookies to the browser. Cookies are stored locally in the browser for future use.


## references

- https://reqbin.com/code/python/9ooszjzg/python-requests-session-example