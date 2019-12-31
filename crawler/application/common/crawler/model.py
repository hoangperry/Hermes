from crawler.application.common.crawler.environments import create_environments
from sqlalchemy.dialects.postgresql import JSON
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from crawler.application.common.helpers import logger
from sqlalchemy.sql import func


config = create_environments()


class DatabaseService:
    Base = declarative_base()
    connection = None

    def __init__(self, host, user, password, port, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.dbname = database
        self.engine = None
        self.connect()

    def connect(self):
        # connection string
        connection_string = 'postgresql+psycopg2://__USERNAME__:__PASSWORD__@__HOST__:__PORT__/__DATABASE__' \
            .replace('__USERNAME__', self.user) \
            .replace('__PASSWORD__', self.password) \
            .replace('__HOST__', self.host) \
            .replace('__PORT__', str(self.port)) \
            .replace('__DATABASE__', self.dbname)
        # create engine
        self.engine = sqlalchemy.create_engine(connection_string, echo=False, convert_unicode=True)
        # create database if not exists
        try:
            self.create_database()
        except Exception as ex:
            logger.error_log.exception(str(ex))

        SessionMaker = sessionmaker(bind=self.engine)
        self.connection = SessionMaker()
        print("Engine created!!!")

    def create_database(self):
        self.Base.metadata.create_all(bind=self.engine)

    def query(self, query):
        rs = self.connection.execute(query)
        return rs

    def insert_one(self, new_document):
        try:
            self.connection.add(new_document)
            self.connection.commit()
        except Exception as ex:
            logger.error_log.exception(str(ex))
            self.connection.rollback()


class DatabaseModel(DatabaseService.Base):
    __tablename__ = config.crawl_type

    id = sqlalchemy.Column(sqlalchemy.BigInteger,
                           sqlalchemy.Sequence('prop_seq', start=1, increment=1),
                           primary_key=True)

    data = sqlalchemy.Column(JSON)
    created_time = sqlalchemy.Column(sqlalchemy.DateTime, default=func.now())


# import nltk
# nltk.download('words')
# nltk.download('maxent_ne_chunker')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('punkt')
#
# def get_continuous_chunks(text):
#     chunked = ne_chunk(pos_tag(word_tokenize(text)))
#     continuous_chunk = []
#     current_chunk = []
#     for i in chunked:
#         if type(i) == Tree:
#             current_chunk.append(" ".join([token for token, pos in i.leaves()]))
#         elif current_chunk:
#             named_entity = " ".join(current_chunk)
#             if named_entity not in continuous_chunk:
#                 continuous_chunk.append(named_entity)
#                 current_chunk = []
#         else:
#             continue
#
#     return continuous_chunk
