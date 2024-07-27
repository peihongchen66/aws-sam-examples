# clinical_studies
Please note that some of services used by this application are not free tier. You may incur small charges if deployed to your account. The charges should be miminal if you are just doing some learning and testing. I have been working on this project the past few weekends and am only charged $0.10 in my AWS account.

This project contains example source code and supporting files for a sample AWS serverless application that notifes user through emails when a ClinicalTrials.gov clinical study on a disease that the user signed up for opens for patient enrollment. There are three Lambda modules, a DynamoDB table, and a website hosting S3 bucket in ths application. I am considering to add CloudFront and Cognito to the web page hosted in S3 in a later version so that the S3 bucket will not be publicly exposed.

- A Lambda function that loads disease keywords mapping from csv file 'disease_mapping.csv' in this repository. It then reads studies from ClinicalTrails.gov that satify certain criteria using ClinicalTrials.gov API, which is described in this link https://clinicaltrials.gov/data-api/api. Finally, the studies are looped through and if study conditions contain any of keywords for a disease/condition, disease/condition, study nctID, and study overall status is entered into DynamoDB table as an Item. If a study's conditions contain keywords for multiple disease/condition, multple items are entered into the table for this study.

- A Lambda function behind an API Gateway to provide a rest API which supports a post method with variables disease/condition and email address in the body. It save the data to the DynamoDB table as notification subscription.

- A Lambda function that is triggered by events from DynamoDB Stream of the table. It sends out emails to the disease/condition subscripbers if the event name is INSERT and overallStatus in the new image is "RECRUITING" or the event name is MODIFY and overallStatus in the new image is "RECRUITING" but in the old image is not.

- A DynamoDB table with PK as partition key and SK as sort key. It holds 3 type of different items. The first type is disease mapping from the csv file with attributes "d#DISEASES"(PK), "d#"+disease/condition(SK), and keywords(keyWords). The secord type is the combination of disease mapping and study information from ClinicalTrails.gov with attributs "s#"+disease/condition(PK), "s#'+nctID(SK), and study overall status(overallStatus). The third type of records is notification subscription with attributes "n#"+disease/condition(PK) and "n#"+email address(SK).

- A website hosting S3 bucket with an HTML page. The HTML page has a simple form. The form action is the URL for the API gateway and method is 'POST'. The form has a multiselect for the user to pick a disease/condition and a textbox to enter email address that enrollment notifications should be sent to.


You can deploy this application with the SAM CLI. It includes the following files and folders.
- func_get_studies - contains Python code for lambda function to get data from ClinicalTrial.gov and disease keyword mapping csv file.
- func_notification_signup - contains Python code for lambda function for notification signup rest API.
- func_study_status_change - contains Python code for lambda function trigged by the DynamoDB table stream to send out notification emails when there are studies that open up for patient enrollment. 
- template.yaml - a template that defines the application's AWS resources.
- index.html - this is the HTML page containing a simple form for the users to submit subscription for enrollment notification for certain disease/condition.

The application uses below AWS resources. These resources are defined in the `template.yaml` file in this project. You can update the template to add AWS resources through the same deployment process that updates your application code.
- AWS Lambda
- Amazon API Gateway
- Amazon DynamoDB
- AWS Identity and Access Management
- Amazon EventBridge
- Amazon S3
- Amazon Simple Email Service


## Deploy the sample application

The Serverless Application Model Command Line Interface (SAM CLI) can be used for build and deploy AWS serverless applications. To deploy this application, there are tasks before and after SAM deploy. 

Before SAM deploy, you need create and verify SES identities for the email addresses that you are going to use. When you first use SES service, your service is in Sandbox. Please see below link for restrictions of Sandbox status.
https://docs.aws.amazon.com/ses/latest/dg/request-production-access.html

Also, in SAM template.yaml file, change email addresses of SESCrudPolicy for StudyStatusChangeFunction to your test sending and receiving email addresses. Change start and end dates of StudyRefreshScheduleEvent for GetStudiesFunction to sometime in the future (they are in UTC timezone). Finally, change BucketName for StudyEnrollmentNotificationS3Bucket to something of your own since bucket names are globally unique.

After SAM deploy, get API gateway endpoint from the output section and replace form action in index.html with this endpoint. Then upload the index.html to the S3 bucket.

To use the SAM CLI, you need the following tools.

* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [Python 3 installed](https://www.python.org/downloads/)

To build and deploy your application for the first time, run the following in your shell:

```bash
sam build 
sam deploy --guided
```
The first command will build the source of your application. The second command will package and deploy your application to AWS, with a series of prompts:

* **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region.
* **AWS Region**: The AWS region you want to deploy your app to.
* **Confirm changes before deploy**: If set to yes, any change sets will be shown to you before execution for manual review. If set to no, the AWS SAM CLI will automatically deploy application changes.
* **Allow SAM CLI IAM role creation**: This SAM template creates AWS IAM roles required for the AWS Lambda functions to access AWS services. By default, these are scoped down to minimum required permissions. To deploy an AWS CloudFormation stack which creates or modifies IAM roles, the `CAPABILITY_IAM` value for `capabilities` must be provided. If permission isn't provided through this prompt, to deploy this example you must explicitly pass `--capabilities CAPABILITY_IAM` to the `sam deploy` command.
* **NoticationSignUpFunction has no authentication. Is this okay?**: To simplify this sample application, there is no authentication mechanism implemented for API gateway. Answer Y.
* **Save arguments to samconfig.toml**: If set to yes, your choices will be saved to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.

You can find your API Gateway Endpoint URL in the output values displayed after deployment.

## Add a resource to your application
The application template uses AWS Serverless Application Model (AWS SAM) to define application resources. AWS SAM is an extension of AWS CloudFormation with a simpler syntax for configuring common serverless application resources such as functions, triggers, and APIs. For resources not included in [the SAM specification](https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md), you can use standard [AWS CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html) resource types.


## Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

