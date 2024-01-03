from typing import Any
from datetime import datetime
import toml
import boto3
import pandas as pd


S3_Path = "s3://{}/{}"
timestamp = f"{datetime.now().strftime('%d_%m_%y_%H_%M_%S')}"


def get_s3_bucket(bucket: Any, aws_creds: dict):
    session = boto3.Session(
        aws_access_key_id=aws_creds["key"], aws_secret_access_key=aws_creds["secret"]
    )
    s3 = session.resource("s3")
    return s3.Bucket(bucket)


def read_jsonl(path: str, aws_creds: dict):
    print(f"Reading {path}")
    df = pd.read_json(path, storage_options=aws_creds, lines=True)
    print(f"Number of records in {path}: ", df.shape)
    return df


def read_source(bucket: Any, source: str, aws_creds: dict, has_wild_card: bool = False):
    if has_wild_card:
        files = [
            S3_Path.format(bucket.name, f_name.key)
            for f_name in bucket.objects.filter(Prefix=source)
            if f_name.key.endswith(".jsonl")
        ]
    else:
        files = [S3_Path.format(bucket.name, source)]
    df = pd.concat([read_jsonl(f_path, aws_creds) for f_path in files])
    print(f"Total number of rows : {df.shape}")
    return df


def compose_datasets(config):
    res = pd.DataFrame()
    train_file_path = (
        S3_Path.format(config["s3"]["output_bucket"], config["s3"]["output_dir"])
        + f"/trainset_{timestamp}.csv"
    )
    test_file_path = (
        S3_Path.format(config["s3"]["output_bucket"], config["s3"]["output_dir"])
        + f"/testset_{timestamp}.csv"
    )
    aws_creds = {"key": config["s3"]["key"], "secret": config["s3"]["secret"]}
    for source in config["sources"]:
        print(f"Composing sources from the bucket: {source['bucket']}")
        paths = source["paths"]
        bucket_name = source["bucket"]
        s3_bucket = get_s3_bucket(bucket_name, aws_creds)
        for path in paths:
            has_wild_card = True if "*" in path else False
            if has_wild_card:
                path = path.split("/")[0]  # remove the * from the path
            res = pd.concat(
                [res, read_source(s3_bucket, path, aws_creds, has_wild_card)]
            )
        print(f"Finished reading all files from bucket/source : {bucket_name}/{source}")
    # shuffle and split to train-test
    res = res.sample(frac=1)
    train_df = res.sample(frac=config["composition"]["train"], random_state=200)
    test_df = res.drop(train_df.index)
    print(f"Train shape: {train_df.shape}")
    print(f"Test shape: {test_df.shape}")
    train_df.to_csv(train_file_path, storage_options=aws_creds)
    test_df.to_csv(test_file_path, storage_options=aws_creds)
    print("Files written to s3")


if __name__ == "__main__":
    with open("config.toml", "r") as f:
        config = toml.load(f)
    compose_datasets(config)
