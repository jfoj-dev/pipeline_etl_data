from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
import os
from pathlib import Path
from dotenv import load_dotenv

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

env_path = Path(__file__).resolve().parent.parent / 'config' / '.env'
load_dotenv(env_path)


def get_engine():
    # lê as credenciais só quando a função é chamada (não no import)
    user = os.getenv('user')
    password = os.getenv('password')
    database = os.getenv('database')
    host = os.getenv('db_host', 'host.docker.internal')

    if not all([user, password, database]):
        raise ValueError("Credenciais do Postgres ausentes (user, password, database) no ambiente")

    logging.info(f"→ Conectando em {host}:5432/{database}")
    return create_engine(
        f"postgresql+psycopg2://{user}:{quote_plus(password)}@{host}:5432/{database}"
    )


def load_weather_data(table_name: str, df):
    engine = get_engine()
    try:
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists='append',
            index=False
        )
        logging.info("✅ Dados carregados com sucesso!")

        with engine.connect() as conn:
            total = conn.execute(text(f'SELECT COUNT(*) FROM {table_name}')).scalar()
        logging.info(f"Total de registros na tabela: {total}")
    finally:
        engine.dispose()