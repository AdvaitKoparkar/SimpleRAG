import os
import ssl
import torch
import faiss
from datetime import datetime
from sqlitedict import SqliteDict
from llama_index.core import VectorStoreIndex
from llama_index.readers.web import BeautifulSoupWebReader
from llama_index.core import StorageContext
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings
from utils.sr_utils import GNewsDownloader, EntityExtractor
from utils.config import SIMPLERAG_PATHS
from transformers import AutoTokenizer
from llama_index.llms.ollama import Ollama

if __name__ == '__main__':
    ssl._create_default_https_context = ssl._create_unverified_context

    # download data
    data_folder = os.path.join(SIMPLERAG_PATHS["PROJ_DIR"], SIMPLERAG_PATHS["DATA_DIR"], datetime.today().strftime("%Y-%m-%d"))
    # if not os.path.isdir(data_folder):
    #     os.mkdir(data_folder) 
    # data_store = os.path.join(data_folder, SIMPLERAG_PATHS['GNEWS_HEADLINES'])
    # g = GNewsDownloader(data_store).save_headlines()

    embed_model = OpenAIEmbedding(model="text-embedding-3-small")
    llm = Ollama(model='llama2', timeout=100.0)
    Settings.embed_model = embed_model
    Settings.llm = llm
    d = 1536
    urls = []
    with SqliteDict('./data/downloaded_articles.db', flag='r') as db:
        for k in db:
            urls.append(db[k]['url'])
    documents = BeautifulSoupWebReader().load_data(urls)
    faiss_index = faiss.IndexFlatL2(d)
    vector_store = FaissVectorStore(faiss_index=faiss_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(
        documents , storage_context=storage_context, 
    )
    import pdb; pdb.set_trace()
    query_engine = index.as_query_engine()
    resp = query_engine.query("what happened in the nasdaq today?")

    # extract labels
    # ner_model = torch.load('./utils/bert-pretrained.pt')
    # tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
    # e = EntityExtractor(ner_model, tokenizer=tokenizer)




