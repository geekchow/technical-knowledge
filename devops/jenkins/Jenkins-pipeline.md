# Jenkins 2 Pipeline definition (Configuration as Code)



## Flow Control Options

### timeout 

```groovy
node {
    def response
    stage('input') {
       timeout(time:10, unit:'SECONDS') {
          response = input message: 'User', 
           parameters: [string(defaultValue: 'user1', 
           description: 'Enter Userid:', name: 'userid')]
       }
       echo "Username = " + response
    }
}
```
When timeout, the whole pipeline aborted. If you don't want to abort the whole pipeline, just wrap it within `try catch` clause.

### try catch 
```groovy
node {
    def response
    stage('input') {
       try {
         timeout(time:10, unit:'SECONDS') {
            response = input message: 'User', 
             parameters: [string(defaultValue: 'user1',
             description: 'Enter Userid:', name: 'userid')]
         }
       }
       catch (err) {
          response = 'user1'
       }
    }
}
```

### retry

The retry closure wraps code in a step that retries the process n times if an exception occurs in the code. n here refers to a value you pass in to the retry step. The syntax is just:

```groovy
retry(<n>) { // processing }
```

### sleep 
This is the basic delay step. It accepts a value and delays that amount of time before continuing processing. The default time unit is seconds, so sleep 5 waits for 5 seconds before continuing processing. If you want to specify a different unit, you just add the unit name parameter, as in:

```groovy
sleep time: 5, unit: 'MINUTES'
```

### waitUntil

As you might guess, this step causes processing to wait until something happens. The “something” in this case is the closure returning true.

If the processing in the block returns false, then this step waits a bit longer and tries again. Any exceptions thrown in the processing cause the step to exit immediately and throw an error.


```groovy
waitUntil { // processing that returns true or false }
```

```groovy
timeout(time:15, unit:'SECONDS') {
    waitUntil {
       def ret = sh returnStatus: true, 
         script: 'test -e /home/jenkins2/marker.txt'
       return (ret == 0)
    }

 }
```

Wait until a file named: `marker.txt` 


## Dealing with Concurrency
