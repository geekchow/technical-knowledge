import AWS from "aws-sdk";

const ChangeDetector = async (event, context) =>  {
  console.log("ChangeDetector is called by ", event, context);

  const sns = new AWS.SNS();

  await new Promise((resolve, reject)=> {
    sns.publish({
      Message: JSON.stringify({ message: "product price changed"}),
      TopicArn: process.env["SNS_ARN"]
    }, (error, data)=> {
      if (error) {
        console.error(error);
        reject(error);
      } else {
        resolve(data);
      }
    })
  })
}

export { ChangeDetector }