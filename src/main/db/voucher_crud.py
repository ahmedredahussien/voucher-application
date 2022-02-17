from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('sqlite://', echo=False)

df = pd.DataFrame({'name' : ['User 1', 'User 2', 'User 3']})

df.to_sql('users', con=engine)

with engine.begin() as connection:
    df1 = pd.DataFrame({'name' : ['User 4', 'User 5']})
    df1.to_sql('users', con=connection, if_exists='append')

print(engine.execute("SELECT * FROM users").fetchall())

df2 = pd.DataFrame({'name': ['User 6', 'User 7']})

df2.to_sql('users', con=engine, if_exists='append')

df2.to_sql('users', con=engine, if_exists='replace',
           index_label='id')

print(engine.execute("SELECT * FROM users").fetchall())