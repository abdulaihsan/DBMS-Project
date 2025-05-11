CREATE TABLE users (
    username VARCHAR(255) PRIMARY KEY,
    password_hash VARCHAR(255)
);

CREATE TABLE sorting_algorithms (
    AlgorithmID INTEGER PRIMARY KEY,
    Name VARCHAR(255) UNIQUE NOT NULL,
    Description TEXT,
    TimeComplexity VARCHAR(255),
    SpaceComplexity VARCHAR(255)
);

CREATE TABLE comparison_logs (
    timestamp TIMESTAMP,
    username VARCHAR(255) REFERENCES users(username),
    left_algorithm VARCHAR(255) REFERENCES sorting_algorithms(Name),
    right_algorithm VARCHAR(255) REFERENCES sorting_algorithms(Name),
    array_size INTEGER,
    winner VARCHAR(255) REFERENCES sorting_algorithms(Name)
);

CREATE TABLE performance_logs (
    timestamp TIMESTAMP,
    username VARCHAR(255) REFERENCES users(username),
    algorithm VARCHAR(255) REFERENCES sorting_algorithms(Name),
    execution_time_ms INTEGER,
    array_size INTEGER,
    array_data TEXT
);

CREATE TABLE user_feedback (
    timestamp TIMESTAMP,
    username VARCHAR(255) REFERENCES users(username),
    message TEXT,
    PRIMARY KEY (timestamp, username)
);

CREATE TABLE user_settings (
    username VARCHAR(255) PRIMARY KEY REFERENCES users(username),
    default_color VARCHAR(7),
    complete_color VARCHAR(7),
    animation_speed INTEGER
);