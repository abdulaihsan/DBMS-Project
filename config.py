from configparser import ConfigParser

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'sorting_viz_db',
    'user': 'postgres',
    'password': 'abdullah',  
    'port': '5432'
}

# Table names
TABLES = {
    'comparison_logs': 'comparison_logs',
    'performance_logs': 'performance_logs',
    'user_settings': 'user_settings',
    'user_feedback': 'user_feedback',
    'sorting_algorithms': 'sorting_algorithms',
    'users': 'users'
}

# SQL queries for table creation
CREATE_TABLES = {
    'users': '''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(64) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''',
    'sorting_algorithms': '''
        CREATE TABLE IF NOT EXISTS sorting_algorithms (
            algorithm_id SERIAL PRIMARY KEY,
            name VARCHAR(50) UNIQUE NOT NULL,
            description TEXT NOT NULL,
            time_complexity VARCHAR(50) NOT NULL,
            space_complexity VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''',
    'user_settings': '''
        CREATE TABLE IF NOT EXISTS user_settings (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            default_color VARCHAR(20) NOT NULL,
            complete_color VARCHAR(20) NOT NULL,
            animation_speed INTEGER NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id)
        )
    ''',
    'comparison_logs': '''
        CREATE TABLE IF NOT EXISTS comparison_logs (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            left_algorithm_id INTEGER NOT NULL,
            right_algorithm_id INTEGER NOT NULL,
            array_size INTEGER NOT NULL,
            winner_algorithm_id INTEGER NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (left_algorithm_id) REFERENCES sorting_algorithms(algorithm_id) ON DELETE RESTRICT,
            FOREIGN KEY (right_algorithm_id) REFERENCES sorting_algorithms(algorithm_id) ON DELETE RESTRICT,
            FOREIGN KEY (winner_algorithm_id) REFERENCES sorting_algorithms(algorithm_id) ON DELETE RESTRICT
        )
    ''',
    'performance_logs': '''
        CREATE TABLE IF NOT EXISTS performance_logs (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            algorithm_id INTEGER NOT NULL,
            execution_time_ms FLOAT NOT NULL,
            array_size INTEGER NOT NULL,
            array_data TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (algorithm_id) REFERENCES sorting_algorithms(algorithm_id) ON DELETE RESTRICT
        )
    ''',
    'user_feedback': '''
        CREATE TABLE IF NOT EXISTS user_feedback (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    '''
}

def load_config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    # get section, default to postgresql
    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return config

if __name__ == '__main__':
    config = load_config()
    print(config)