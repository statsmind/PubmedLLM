import chromadb
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.vectorstores.milvus import Milvus

if __name__ == '__main__':
    embedding = HuggingFaceEmbeddings(
        model_name='sentence-transformers/all-mpnet-base-v2',
        model_kwargs={'device': 'cuda'},
        encode_kwargs={'normalize_embeddings': False})
    splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=30)

    # vectordb = Milvus(
    #     connection_args={"uri": "http://192.168.77.13:19530", "secure": False},
    #     collection_name='pubmed',
    #     embedding_function=embedding,
    #     index_params={"metric_type": 'IP'},
    #     search_params={"metric_type": 'IP'}
    # )
    #
    # vectordb = Chroma(
    #     collection_name='pubmed',
    #     collection_metadata={'hnsw:space': 'cosine'},
    #     persist_directory=r'd:\cache\chroma', embedding_function=embedding)
    vectordb = Chroma(
        collection_name='pubmed',
        collection_metadata={'hnsw:space': 'ip'},
        client=chromadb.HttpClient(host='192.168.77.13', port='38002'),
        embedding_function=embedding)

    while True:
        question = input("Question: ")
        if len(question.strip()) == 0:
            continue

        results = vectordb.similarity_search_with_relevance_scores(question)

        print(f"searched {len(results)} documents")
        for idx, result in enumerate(results):
            print(idx, result[1], result[0].page_content)
