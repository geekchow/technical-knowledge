  apigatewayauthorizernodejs:
    Type: AWS::Serverless::Application
    Properties:
      Location:
        ApplicationId: arn:aws:serverlessrepo:us-east-1:077246666028:applications/api-gateway-authorizer-nodejs
        SemanticVersion: 1.0.3
      Parameters: 
        TopicNameParameter: YOUR_VALUE  
      

https://github.com/amazon-archives/serverless-app-examples/tree/master/javascript/api-gateway-authorizer-nodejs