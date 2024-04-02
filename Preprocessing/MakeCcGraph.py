from pyspark.sql import SparkSession
import pyspark.sql.functions as F
import pyspark.sql.types as T
import numpy as np
import pandas as pd
import ast
import datetime
import matplotlib.pyplot as plt
import networkx as nx
import config

# 세션 생성 및 MongoDB 연동
spark = SparkSession.builder\
    .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.0")\
    .appName("egg").getOrCreate()

# 월 기준 현재 한 달전 
current_datetime = datetime.datetime.now()
year = current_datetime.year
month = current_datetime.month
one_month_ago = current_datetime - datetime.timedelta(days=current_datetime.day)
one_month_ago = one_month_ago.month

# 문자열 -> 리스트 변환 함수
def parse_list(value):
    return ast.literal_eval(value) if value else []

# udf 등록
parse_list_udf = F.udf(parse_list, T.ArrayType(T.StringType()))

# Raw 데이터 가져오기
def get_kci_data(db_name, col_name):
    
    print('Get ',col_name,"!")

    schema = T.StructType([
        T.StructField("articleID", T.StringType(), True),
        T.StructField("titleEng", T.StringType(), True),
        T.StructField("abstractEng", T.StringType(), True),
        T.StructField("journalID", T.StringType(), True),
        T.StructField("pubYear", T.StringType(), True),
        T.StructField("refereceTitle", T.StringType(), True),
        T.StructField("class", T.StringType(), True),
        T.StructField("keys", T.StringType(), True),
        T.StructField("ems", T.StringType(), True)

    ])

    kci_api_uri = f"mongodb://{config.mongo_user}:{config.mongo_pass}@mongodb:27017/{db_name}.{col_name}?authSource=admin"

    df = spark.read.format("mongo") \
        .option("uri", kci_api_uri) \
        .schema(schema)\
        .load()
    df = df.withColumn("refereceTitle", parse_list_udf(df["refereceTitle"]))
    df = df.withColumn("keys", parse_list_udf(df["keys"]))

    return df

def union_df(df, new_df):
    print("Union df!")

    df = df.union(new_df)
    df = df.drop_duplicates()
    save_df(df,"kci_union_data","kci_union_data_:04d}{:02d}".format(year, month))

    return df

def generate_relation(df):
    print("generate_relation!")

    df_exploded1 = df.select("articleID", F.explode(F.col("refereceTitle")).alias("referenceTitle"))
    df_exploded2 = df.select(F.col("articleID").alias("RelationArticleID"), F.explode(F.col("refereceTitle")).alias("referenceTitle2"))

    joined_df = df_exploded1.join(df_exploded2, df_exploded1["referenceTitle"] == df_exploded2["referenceTitle2"], "left")
    selected_columns = ["articleID", "RelationArticleID"]
    joined_df = joined_df.select(selected_columns)
    joined_df = joined_df.filter(joined_df["articleID"] != joined_df["RelationArticleID"])

    return joined_df

def generate_and_save_graph(df):
    print("Generate CcGrpah")
    G = nx.Graph()

    for row in df.rdd.collect():
        article_id = row['articleID']
        G.add_node(article_id)

    # 아티클 리스트를 기준으로 엣지(링크)를 추가
    for row in df.rdd.collect():
        article_id = row['articleID']
        article_list = row['RelationArticleID']
        for reference in article_list:
            G.add_edge(article_id, reference)
            
    graphname = "CcGraph.graphml"
    nx.write_graphml(G, graphname)
    print('Saved',graphname)

def convert_col_list(df):
    df = df.groupby("articleID").agg(F.collect_set(F.col("RelationArticleID")).alias("RelationArticleID"))
    df = df.withColumn("length", F.size(F.col("RelationArticleID")))
    df = df.orderBy("length", ascending=False)

    return df


def generate_final_df(df, rel_df):
    print("generate_final_df")

    col_df = convert_col_list(rel_df)
    res_df = df.join(col_df, df["articleID"] == col_df["articleID"], "left")
    res_df = res_df.drop(col_df["articleID"])
    res_df = res_df.select(
        "articleID",
        "titleEng",
        "abstractEng",
        "journalID",
        "pubYear",
        "refereceTitle",
        "class",
        "keys",
        "ems",
        "RelationArticleID",
        "length"
    )

    save_df(res_df,"EGG_","Egg_CCgraph_Data")

    return res_df

def save_df(df, db_name, col_name):
    save_uri = f"mongodb://{config.mongo_user}:{config.mongo_pass}@mongodb:27017/{db_name_}.{col_name}?authSource=admin"
    df.write.format("mongo") \
        .option("uri", save_uri) \
        .mode("overwrite") \
        .save()

previous_kci_db_name= "kci_trained_api"
now_kci_db_name = "kci_union_data"
previous_col_name = "kci_trained_{:04d}{:02d}".format(year, one_month_ago)
current_col_name = "kci_trained_{:04d}{:02d}".format(year, month)


origin_df = get_kci_data(previous_kci_db_name,previous_col_name)
new_df = get_kci_data(now_kci_db_name,current_col_name)
uni_df = union_df(origin_df,new_df)
ref_df = generate_relation(uni_df)
generate_and_save_graph(ref_df)
final_df = generate_final_df(uni_df,ref_df)

