import os

import torch.cuda
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores.milvus import Milvus
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import CharacterTextSplitter, TokenTextSplitter, RecursiveCharacterTextSplitter, \
    TextSplitter
from langchain_community.vectorstores import Chroma
from parser.article import ArticleObject
from parser.parser import PubmedParser
import chromadb


def process_article(article: ArticleObject, vectordb: Chroma, splitter: TextSplitter):
    if len(article.abstract) < 10 or article.pdat is None:
        return

    # if "stroke" not in article.abstract and "lung" not in article.abstract:
    #     return

    print(f"processing {article.pmid}")
    documents = splitter.create_documents(texts=[article.title, article.abstract], metadatas=[{
        'pmid': article.pmid,
        'year': article.pdat.split('-')[0]
    }] * 2)
    vectordb.add_documents(documents)


if __name__ == '__main__':
    embedding = HuggingFaceEmbeddings(
        model_name='sentence-transformers/all-mpnet-base-v2',
        model_kwargs={'device': 'cuda'},
        encode_kwargs={'normalize_embeddings': False})
    splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=30)

    # import pymilvus
    # client = pymilvus.MilvusClient(uri="http://192.168.77.13:19530")
    # client.drop_collection('pubmed')

    # vectordb = Milvus(
    #     connection_args={"uri": "http://192.168.77.13:19530", "secure": False},
    #     collection_name='pubmed',
    #     embedding_function=embedding,
    #     index_params={"metric_type": 'IP'},
    #     search_params={"metric_type": 'IP'}
    # )

    # vectordb = Chroma(
    #     collection_name='pubmed',
    #     collection_metadata={'hnsw:space': 'cosine'},
    #     persist_directory=r'd:\cache\chroma', embedding_function=embedding)
    client = chromadb.HttpClient(host='192.168.77.13', port='38002')
    client.delete_collection('pubmed')

    vectordb = Chroma(
        collection_name='pubmed',
        collection_metadata={'hnsw:space': 'ip'},
        client=client,
        embedding_function=embedding)

    pubmed_parser = PubmedParser()

    for dirpath, dirnames, filenames in os.walk(r'F:\pubmed\ftp.ncbi.nlm.nih.gov\pubmed'):
        for filename in filenames:
            if not filename.endswith('.xml.gz'):
                continue

            results = pubmed_parser.parse(os.path.join(dirpath, filename))

            for article in results:
                process_article(article, vectordb, splitter)
