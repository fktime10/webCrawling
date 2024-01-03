import os
import toml
import pandas as pd
import spacy
import img2pdf
import matplotlib.pyplot as plt
import seaborn as sns

nlp = spacy.load("de_core_news_sm")
nlp.max_length = 2000000
S3_PATH = "s3://{}/{}"
NOUN_POS = ["NOUN", "PROPN"]


def noun_to_word_ratio(doc):
    sents = list(doc.sents)
    ratios = 0.0
    for sent in sents:
        num_nouns = sum([1 if tok.pos_ in NOUN_POS else 0 for tok in sent])
        all_pos = len(sent)
        ratios += float(num_nouns / all_pos)
    return round(float(ratios / len(sents)), 3)


def compute_doc_level_metrics(row: pd.Series, config: dict, column: str):
    metrics = []
    text = row[column]
    doc = nlp(text)
    if config["num_words"]:
        metrics.append("num_words")
        row["num_words"] = sum([1 if token.is_alpha else 0 for token in doc])
    if config["num_sentences"]:
        metrics.append("num_sentences")
        row["num_sentences"] = len(list(doc.sents))
    if config["num_unique_words"]:
        metrics.append("num_unique_words")
        row["num_unique_words"] = len(
            list(set([token.text for token in doc if token.is_alpha]))
        )
    if config["noun_to_word_ratios"]:
        metrics.append("noun_to_word_ratios")
        row["noun_to_word_ratios"] = noun_to_word_ratio(doc)
    return row[metrics + ["id", "source"]]


def convert_images_to_pdf(config: dict, img_paths: list):
    with open(f"{config['output_dir']}/report.pdf", "wb") as f:
        f.write(img2pdf.convert([img for img in img_paths]))


def generate_distributions(config: dict, res: pd.DataFrame):
    metrics = [
        metric
        for metric in config["metrics"]
        if config["metrics"][metric] and metric != "distributions"
    ]
    for metric in metrics:
        print(f"Generating graphs for the metric {metric}..")
        sns.histplot(data=res, x=metric, hue="source", element="step")
        plt.xlabel(xlabel=metric)
        plt.title(metric.upper().replace("_", " "))
        plt.savefig(f'{config["output_dir"]}/res_{metric}.png')
        plt.figure()
    convert_images_to_pdf(config, [f"{config['output_dir']}/res_{i}.png" for i in metrics]
    )


def persist_metric_counts(
    src_name: str, df: pd.DataFrame, counts: pd.DataFrame, metrics: list
):
    for metric in metrics:
        counts.loc[src_name, metric] = (
            df[metric].mean() if "ratio" in metric else df[metric].sum()
        )
    return counts


def compute_metrics(config: dict):
    res = pd.DataFrame()
    bucket = config["s3"]["bucket"]
    sources = config["s3"]["sources"]
    column = config["s3"]["column"]
    key = config["s3"]["key"]
    metrics = [
        metric
        for metric in config["metrics"]
        if config["metrics"][metric] and metric != "distributions"
    ]
    secret = config["s3"]["secret"]
    aws_creds = {"key": key, "secret": secret}
    counts = pd.DataFrame(columns=metrics)
    os.makedirs(config["output_dir"], exist_ok=True)

    for src in sources:
        src_name = src.split("/")[-1].replace(".jsonl", "")
        if src_name=="*":
            src_name = src.split("/")[0]
        print(f"Computing metrics for src: {src}, src_name: {src_name}")
        df = pd.read_json(
            S3_PATH.format(bucket, src), storage_options=aws_creds, lines=True
        )
        print(f"File read complete: num_rows: {df.shape}")
        src_metrics_df = df.apply(
            compute_doc_level_metrics, config=config["metrics"], column=column, axis=1
        )
        res = pd.concat((res, src_metrics_df))
        counts = persist_metric_counts(src_name, src_metrics_df, counts, metrics)
    # save dataframes
    res.to_csv(f"{config['output_dir']}/FinalMetrics.csv")
    counts.to_csv(f"{config['output_dir']}/counts.csv")
    # generate distributions
    if config["metrics"]["distributions"]:
        generate_distributions(config, res)
    print("Saving graphs as a report..")


if __name__ == "__main__":
    with open("config.toml", "r") as f:
        config = toml.load(f)
    compute_metrics(config)
    exit(-1)