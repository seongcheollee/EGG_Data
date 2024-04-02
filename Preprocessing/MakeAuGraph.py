from pyspark.sql import SparkSession
import pyspark.sql.functions as F
import pyspark.sql.types as T
import numpy as np
import pandas as pd
import ast
import networkx as nx
import datetime

# SparkSession을 생성
spark = SparkSession.builder\
    .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.0")\
    .appName("egg").getOrCreate()

# 날짜
current_datetime = datetime.datetime.now()
year = current_datetime.year
month = current_datetime.month
one_month_ago = (current_datetime - datetime.timedelta(days=current_datetime.day)).month

# UDF 정의
def parse_lists(list_str):
    return ast.literal_eval(list_str) if list_str.strip() else ['None']

# UDF 등록
parse_lists_udf = F.udf(parse_lists, T.ArrayType(T.StringType()))

def get_kci_data(db_name, col_name):
    
    print('Get ',col_name,"!")

    schema = T.StructType([
        T.StructField("articleID", T.StringType(), True),
        T.StructField("titleKor", T.StringType(), True),
        T.StructField("journalID", T.StringType(), True),
        T.StructField("journalName", T.StringType(), True),
        T.StructField("issn", T.StringType(), True),
        T.StructField("citations", T.StringType(), True),
        T.StructField("pubYear", T.StringType(), True),
        T.StructField("author1ID", T.StringType(), True),
        T.StructField("author1Name", T.StringType(), True),
        T.StructField("author1Inst", T.StringType(), True),
        T.StructField("author2IDs", T.StringType(), True),
        T.StructField("author2Names", T.StringType(), True),
        T.StructField("author2Insts", T.StringType(), True),
        T.StructField("class", T.StringType(), True),
        T.StructField("keywords",T.StringType(), True)
    ])

    kci_api_uri = f"mongodb://{config.mongo_user}:{config.mongo_pass}@mongodb:27017/{db_name}.{col_name}?authSource=admin"

    df = spark.read.format("mongo") \
        .option("uri", kci_api_uri) \
        .schema(schema)\
        .load()
        
    df = df.withColumn("author2IDs", parse_lists_udf(df["author2IDs"]))
    df = df.withColumn("author2Names", parse_lists_udf(df["author2Names"]))
    df = df.withColumn("author2Insts", parse_lists_udf(df["author2Insts"]))
    df = df.withColumn("keywords", parse_lists_udf(df["keywords"]))

    return df

def get_author_data(db_name, col_name):
    
    print('Get ',col_name,"!")

    schema = T.StructType([
        T.StructField("authorID", T.StringType(), True),
        T.StructField("kiiscArticles", T.StringType(), True),
        T.StructField("totalArticles", T.StringType(), True),
        T.StructField("if", T.StringType(), True),
        T.StructField("H-index", T.StringType(), True)
    ])

    kci_api_uri = f"mongodb://{config.mongo_user}:{config.mongo_pass}@mongodb:27017/{db_name}.{col_name}?authSource=admin"

    df = spark.read.format("mongo") \
        .option("uri", kci_api_uri) \
        .schema(schema)\
        .load()

    return df

def merge_df(origin_df , new_df):
    print("Merge!")
    union_df = origin_df.union(new_df)
    return union_df

def exploded_df(df):
    print('Exploded!')
    df = df.withColumn("temp", F.explode_outer(F.arrays_zip("author2IDs", "author2Names", "author2Insts"))) \
        .drop("author2IDs", "author2Names", "author2Insts") \
        .selectExpr("*", "temp.*") \
        .withColumnRenamed("author2IDs", "author2ID") \
        .withColumnRenamed("author2Names", "author2Name") \
        .withColumnRenamed("author2Insts", "author2Inst") \
        .drop("temp")
    df = df.select(
        "articleID",
        "titleKor",
        "journalID",
        "journalName",
        "issn",
        "citations",
        "pubYear",
        "author1ID",
        "author1Name",
        "author1Inst",
        "author2ID",
        "author2Name",
        "author2Inst",
        'class',
        'keywords'
        )

    return df

def joined_df(df):
    print("Outer join")
    df = df.dropDuplicates(["articleID", "author1ID", "author2ID"])

    # authorID 종합
    df1 = df.select("author1ID","author1Name","author1Inst")
    df2 = df.select("author2ID","author2Name","author2Inst")
    merged_df = df1.union(df2).withColumnRenamed("author1ID", "authorID")
    merged_df = merged_df.dropDuplicates(["authorID"])
    merged_df = merged_df.distinct().na.drop()

    selected_columns = df.select(
        "author1ID",
        "author2ID",
        "articleID",
        "titleKor",
        "journalID",
        "journalName",
        "pubYear",
        "citations",
        "class",
        "keywords",
    )
    joined_df = merged_df.join(selected_columns, merged_df.authorID == selected_columns.author1ID, "outer")

    return joined_df

def grouping(df):
    print("Grouping")
    grouped_df = df.groupBy("authorID", "author1Name","author1Inst").agg(
        F.collect_list("articleID").alias("articleIDs"),
        F.collect_list("titleKor").alias("titleKor"),
        F.collect_list("author2ID").alias("with_author2IDs"),
        F.collect_list("author1ID").alias("with_author1IDs"),
        F.collect_list("citations").alias("citations"),
        F.collect_list("journalID").alias("journalIDs"),
        F.collect_list("pubYear").alias("pubYears"),
        F.collect_list("class").alias("class"),
        F.collect_list("keywords").alias("word_cloud"),

    )
    grouped_df = grouped_df.withColumn("with_author1IDs", F.array())
    grouped_df = grouped_df.withColumn("word_cloud", F.flatten(grouped_df["word_cloud"]))

    return grouped_df
    

def join_author_info(grouped_df, author_info_df):
    joined_df = grouped_df.join(author_info_df, on="authorID", how="left")
    drop_column = ['authorName','authorInst']
    joined_df = joined_df.drop(*drop_column)
    joined_df = joined_df.withColumnRenamed("if", "impactfactor")
    joined_df = joined_df.withColumnRenamed("H-index", "H_index")
    joined_df = joined_df.withColumnRenamed("class", "category")
    return joined_df

def save_final_kci_data(df, db_name, col_name):
    save_uri = f"mongodb://{config.mongo_user}:{config.mongo_pass}@mongodb:27017/{db_name_}.{col_name}?authSource=admin"
    df.write.format("mongo") \
        .option("uri", save_uri) \
        .mode("overwrite") \
        .save()

def generate_and_save_graph(df):
    print("Generate AuGraph")
    G = nx.Graph()

    # 저자 아이디 노드 추가
    for row in df.rdd.collect():
        article_id = row['authorID']
        G.add_node(article_id)

    # with_author2IDs를 기준으로 엣지 추가
    for row in df.rdd.collect():
        author_id = row['authorID']
        author_list = row['with_author2IDs']
        for reference in author_list:
            G.add_edge(author_id, reference)
    
    graphname = "AuGraph{:04d}{:02d}.graphml".format(year, month)
    nx.write_graphml(G, graphname)
    print('Saved', graphname)



kci_db = "kci_trained_api"
au_db = "kci_author_info"
kau_db = "kci_AuGraph"

previous_col_name = "kci_trained_{:04d}{:02d}".format(year, one_month_ago)
current_col_name = "kci_trained_{:04d}{:02d}".format(year, month)
previous_col_name_author_info = "author_{:04d}{:02d}".format(year, one_month_ago)
current_col_name_author_info = "kci_AuGraph_{:04d}{:02d}".format(year, month)

origin_df = get_kci_data(kci_db,previous_col_name)
new_df = get_kci_data(kci_db, current_col_name)
author_df = get_author_data(au_db,previous_col_name_author_info)
merged_df = merge_df(origin_df, new_df)
exploded_df = exploded_df(merged_df)
joined_df = joined_df(exploded_df)
grouped_df = grouping(joined_df)
final_df = join_author_info(grouped_df, author_df)
save_final_kci_data(final_df,kau_db  ,current_col_name_author_info)
#generate_and_save_graph(grouped_df)
