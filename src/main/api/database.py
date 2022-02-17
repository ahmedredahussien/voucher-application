from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.main.app.yaml_config import YamlConfig

config_dict = YamlConfig.get_config()

#db url
SQLALCHEMY_DATABASE_URL = config_dict['mysql']['dburl']
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

#database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#used for creating database models or classes (the ORM models)
Base = declarative_base()