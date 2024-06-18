import os
import json
import hashlib
import urllib.request
from datetime import datetime

from config import SIMPLERAG_PATHS
from config import GNEWS_API_KEY
from config import OPENAI_API_KEY

class GNewsDownloader():
    _API_KEY = GNEWS_API_KEY
    _ARTICLE_HASHER = hashlib.sha256
    def __init__(self, ):
        self.data_store = os.path.join(SIMPLERAG_PATHS["PROJ_DIR"], SIMPLERAG_PATHS["DATA_DIR"], "downloaded_articles.db")
        if not os.path.isfile(self.data_store):
            db = SqliteDict(self.data_store, autocommit=False, flag='n')
            db.commit()

    def headlines(self, filters = dict() ):
        category  = filters.get("category", "general")
        from_date = filters.get("from_date", datetime.today().strftime("%Y-%m-%d"))
        to_date   = filters.get("to_date", datetime.today().strftime("%Y-%m-%d"))
        max_arts  = filters.get("max_arts", 10)
        lang      = "en"
        country   = "us"
        
        url = \
        "https://gnews.io/api/v4/top-headlines?" \
        f"category={category}" \
        f"&lang={lang}&country={country}" \
        f"&from={from_date}T00:00:00Z&to={to_date}T23:59:59Z" \
        f"&max={max_arts}&apikey={self._API_KEY}"

        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode("utf-8"))
            articles = data["articles"]

            with SqliteDict(self.data_store, flag='c') as db:
                for article in articles:
                    article_hash = self._ARTICLE_HASHER(str(article).encode('UTF-8')).digest()
                    db[article_hash] = article
                db.commit()

class InterestedEntityManager:
    _USER_TAGS_DB = os.path.join(SIMPLERAG_PATHS['PROJ_DIR'], SIMPLERAG_PATHS['DATA_PATH'], 'user_ne.db')
    def __init__(self, ):
        pass



if __name__ == "__main__":
    import os
    os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

    import faiss
    from sqlitedict import SqliteDict
    from llama_index.core import VectorStoreIndex
    from llama_index.readers.web import BeautifulSoupWebReader
    from llama_index.core import StorageContext
    from llama_index.vector_stores.faiss import FaissVectorStore

    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
    
    urls = []
    with SqliteDict('../data/downloaded_articles.db', flag='r') as db:
        for k in db:
            urls.append(db[k]['url'])
    documents = BeautifulSoupWebReader().load_data(urls)

    d = 1536
    faiss_index = faiss.IndexFlatL2(d)
    vector_store = FaissVectorStore(faiss_index=faiss_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    vector_store = VectorStoreIndex(documents, storage_context=storage_context)
    import pdb; pdb.set_trace()