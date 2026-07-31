# how to operation jenkins via api

## With NodeJs
[npm pacakge jenkins](https://github.com/silas/node-jenkins) 
```shell
npm i jenkins@1.0.0
# caution the 1.0.1 version doesn't work, it hangs all requests there. Version 1.0.0 works like a charm.

```
```javascript
import Jenkins from "jenkins";

const jenkins = new Jenkins({
  baseUrl: "http://user:pass@localhost:8080",
});

let a = await jenkins.info();

await jenkins.job.build({
  name: "example",
  parameters: { name: "value" },
});
```

result 
```json
{
  "assignedLabels": [{}],
  "description": null,
  "jobs": [
    {
      "color": "blue",
      "name": "example",
      "url": "http://localhost:8080/job/example/"
    }
  ],
  "mode": "NORMAL",
  "nodeDescription": "the master Jenkins node",
  "nodeName": "",
  "numExecutors": 2,
  "overallLoad": {},
  "primaryView": {
    "name": "All",
    "url": "http://localhost:8080/"
  },
  "quietingDown": false,
  "slaveAgentPort": 12345,
  "unlabeledLoad": {},
  "useCrumbs": false,
  "useSecurity": false,
  "views": [
    {
      "name": "All",
      "url": "http://localhost:8080/"
    }
  ]
}
```

## With Python

[python-jenkins pip package](https://opendev.org/jjb/python-jenkins)
[document](https://python-jenkins.readthedocs.io/en/latest/examples.html)

```shell
# pip package jenkins
pip install python-jenkins=1.8.0
```

```python
import jenkins

server = jenkins.Jenkins('http://localhost:8080', username='myuser', password='mypassword')
user = server.get_whoami()
version = server.get_version()
print('Hello %s from Jenkins %s' % (user['fullName'], version))

```



## Working with Scripted Clients
Requests sent using the POST method are subject to CSRF protection in Jenkins and generally need to provide a crumb. This also applies to scripted clients that authenticate using username and password. Since the crumb includes the web session ID, clients need to do the following:

- Send a request to the /crumbIssuer/api endpoints, requesting a crumb. Note the Set-Cookie response header.
- For all subsequent requests, provide the crumb and the session cookie in addition to username and password.
- Alternatively authenticate using username and API token. Requests authenticating with an API token are exempt from CSRF protection in Jenkins.

## References:

- https://www.jenkins.io/doc/book/security/csrf-protection/#disabling-csrf-protection