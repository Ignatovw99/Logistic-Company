import pytest
import tempfile
import os
from app import create_app, db


flask_app = create_app("testing")


@pytest.fixture(scope="function")
def test_app_db_client():
    db_fd, db_file_path = tempfile.mkstemp()

    flask_app.config["SQLALCHEMY_DATABASE_URI"] = flask_app.config["TEST_DATABASE_PREFIX"] + db_file_path

    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            db.create_all()
        
        yield testing_client
    
    os.close(db_fd)
    os.unlink(db_file_path)


@pytest.fixture(scope="module")
def test_app_client():
    with flask_app.test_client() as testing_client:
        return testing_client
    