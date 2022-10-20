import json
import boto3
import PIL
import datetime
import os
from io import BytesIO
from PIL import Image



def callImage(event, context):
    image_key = event["pathParameters"]["image"]
    image_size = event["pathParameters"]["size"]

    result_url = image_resize(os.environ["BUCKET"], image_key, image_size)
 
    response = {
        "statusCode": 301,
        "body": "",
        "headers": {
            "location": result_url
        }
    }
 
    return response


def image_resize(bucket_name, image_key, image_size):
    split_size = image_size.split('x')
    s3 = boto3.resource('s3')
    obj = s3.Object(
        bucket_name=bucket_name, 
        key=image_key,
    )
    obj_body = obj.get()['Body'].read()

    #resizing the image read to new size
    image = Image.open(BytesIO(obj_body))
    image = image.resize((int(split_size[0]), int(split_size[1])), PIL.Image.ANTIALIAS)
    buffer = BytesIO()
    image.save(buffer, 'JPEG')
    buffer.seek(0)

    #upload the resized image into s3 bucket
    image_resized_key="{size}_{key}".format(size=image_size, key=image_key)
    obj = s3.Object(
        bucket_name=bucket_name,
        key=image_resized_key,
    )
    obj.put(Body=buffer, ContentType='image/jpg')

    return image_resized_url(image_resized_key, bucket_name, os.environ["AWS_REGION"])


def image_resized_url(image_resized_key, bucket, region):
    return "https://s3-{region}.amazonaws.com/{bucket}/{image_resized_key}".format(bucket=bucket, region=region, image_resized_key=image_resized_key)
