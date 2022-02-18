from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.main.config.yaml_config import YamlConfig

config_dict = YamlConfig.get_config()

#db url
MYSQL_DATABASE_URL = config_dict['mysql']['dburl']
DATABASE_SCHEMA = config_dict['mysql']['db_schemaname']
SQLALCHEMY_DATABASE_URL = MYSQL_DATABASE_URL + "/" + DATABASE_SCHEMA
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
print("SQLALCHEMY_DATABASE_URL="+SQLALCHEMY_DATABASE_URL)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

#database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#used for creating database models or classes (the ORM models)
Base = declarative_base()