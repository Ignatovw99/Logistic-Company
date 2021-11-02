class Config():
    DEBUG = False
    TESTING = False

    DB_NAME = "logistics_company"
    DB_USERNAME = "root"
    DB_PASSWORD = "1234"
    DB_HOST = "localhost"
    DB_PORT = 3306

    SQLALCHEMY_DATABASE_URI = f"mysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO=True


class ProductionConfig(Config):
    pass


class TestingConfig(Config):
    TESTING = True


env_config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig
}