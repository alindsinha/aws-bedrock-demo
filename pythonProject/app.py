from http.client import responses

import boto3
import botocore.config

from datetime import datetime
import json


def blog_generate_using_bedrock(blogpost: str) -> str:
    prompt = f""" Create a blog topic in 200 words"""
    config = botocore.config.Config(read_timeout=300, retries={'max_attempts': 3})
    body = {
        "prompt": prompt,
        "max_gen_length": 512,
        "tempearture": 0.5,
        "top_p": 0.9

    }

    try:
        bedrock = boto3.client("bedrock-runtime", region_name="us=east-1",
                               config=config)
        response = bedrock.invoke_model(body=json.dumps(body), modelId='meta.llama3-8b-instruct-v1:0')

        response_content = response.get('body').read()
        response_data = json.load(response_content)
        print(response_data)
        blog_details = response_data['generation']
    except Exception as e:
        print(f"Error generating the  blog:{e}")


def save_s3_blog_details(s3_key, s3_bucket, generate_blog):
    s3 = boto3.client('s3')
    try:
        s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=generate_blog)
        print("Blog saved to s3")
    except Exception as e:
        print("Error Saving blog")


def lambda_handler(event, context):
    event = json.loads(event['body'])
    blogtopic = event['blog_topic']

    generate_blog = blog_generate_using_bedrock(blogpost=blogtopic)

    if generate_blog:
        current_time = datetime.now().strftime('%H%M%S')
        s3_key = f"blog-output/{event['blog_topic']}.txt"
        s3_bucket = "alind_bedrock"
        save_s3_blog_details(s3_key, s3_bucket, generate_blog)
    else:
        print("No Blog Generated")

    return {
        'statusCode': 200,
        'body': json.dumps("Blog Generation complete")
    }

