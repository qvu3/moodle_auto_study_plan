from sqlalchemy import create_engine, text
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

def create_db_engine():
    """Create a SQLAlchemy engine for the MySQL database."""
    try:
        # Create connection string for MySQL
        connection_string = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
        engine = create_engine(connection_string)
        return engine
    except Exception as e:
        print(f"Error creating database engine: {e}")
        return None

def get_wrongly_answered_questions(user_id, days=7):
    """Get the questions a user answered wrongly in the last x days."""
    engine = create_db_engine()
    if engine is None:
        return None

    query = text("""
    SELECT
        q.id AS question_id,
        q.questiontext AS question_text,
        qas.responsesummary AS user_answer,
        qas.rightanswer AS correct_answer,
        FROM_UNIXTIME(qa.timefinish) AS answered_at
    FROM mdl_quiz_attempts qa
    JOIN mdl_question_usages qu ON qa.uniqueid = qu.id
    JOIN mdl_question_attempts qas ON qu.id = qas.questionusageid
    JOIN mdl_question q ON qas.questionid = q.id
    WHERE qa.userid = :user_id
    AND qa.state = 'finished'
    AND qas.responsesummary IS NOT NULL
    AND qas.rightanswer IS NOT NULL
    AND qas.responsesummary != qas.rightanswer
    AND qa.timefinish >= UNIX_TIMESTAMP(NOW() - INTERVAL :days DAY)
    ORDER BY qa.timefinish DESC;
    """)

    try:
        with engine.connect() as connection:
            result = connection.execute(query, {'user_id': user_id, 'days': days})
            rows = result.fetchall()
            
            # Convert to a simple data structure that mimics pandas DataFrame
            if rows:
                columns = result.keys()
                data = []
                for row in rows:
                    data.append(dict(zip(columns, row)))
                
                # Create a simple object that has the methods we need
                class SimpleDataFrame:
                    def __init__(self, data):
                        self.data = data
                    
                    @property
                    def empty(self):
                        return len(self.data) == 0
                    
                    def iterrows(self):
                        for i, row in enumerate(self.data):
                            yield i, SimpleRow(row)
                    
                    def __len__(self):
                        return len(self.data)
                
                class SimpleRow:
                    def __init__(self, data):
                        for key, value in data.items():
                            setattr(self, key, value)
                
                return SimpleDataFrame(data)
            else:
                return SimpleDataFrame([])
                
    except Exception as e:
        print(f"Error reading data from MySQL: {e}")
        return None
    finally:
        engine.dispose()

    return None 

def get_correctly_answered_questions(user_id, days=7):
    """Get the questions a user answered correctly in the last x days."""
    engine = create_db_engine()
    if engine is None:
        return None

    query = text("""
    SELECT
        q.id AS question_id,
        q.questiontext AS question_text,
        qas.responsesummary AS user_answer,
        qas.rightanswer AS correct_answer,
        FROM_UNIXTIME(qa.timefinish) AS answered_at
    FROM mdl_quiz_attempts qa
    JOIN mdl_question_usages qu ON qa.uniqueid = qu.id
    JOIN mdl_question_attempts qas ON qu.id = qas.questionusageid
    JOIN mdl_question q ON qas.questionid = q.id
    WHERE qa.userid = :user_id
    AND qa.state = 'finished'
    AND qas.responsesummary IS NOT NULL
    AND qas.rightanswer IS NOT NULL
    AND qas.responsesummary = qas.rightanswer
    AND qa.timefinish >= UNIX_TIMESTAMP(NOW() - INTERVAL :days DAY)
    ORDER BY qa.timefinish DESC;
    """)

    try:
        with engine.connect() as connection:
            result = connection.execute(query, {'user_id': user_id, 'days': days})
            rows = result.fetchall()
            
            # Convert to a simple data structure that mimics pandas DataFrame
            if rows:
                columns = result.keys()
                data = []
                for row in rows:
                    data.append(dict(zip(columns, row)))
                
                # Create a simple object that has the methods we need
                class SimpleDataFrame:
                    def __init__(self, data):
                        self.data = data
                    
                    @property
                    def empty(self):
                        return len(self.data) == 0
                    
                    def iterrows(self):
                        for i, row in enumerate(self.data):
                            yield i, SimpleRow(row)
                    
                    def __len__(self):
                        return len(self.data)
                
                class SimpleRow:
                    def __init__(self, data):
                        for key, value in data.items():
                            setattr(self, key, value)
                
                return SimpleDataFrame(data)
            else:
                return SimpleDataFrame([])
                
    except Exception as e:
        print(f"Error reading data from MySQL: {e}")
        return None
    finally:
        engine.dispose()

    return None 