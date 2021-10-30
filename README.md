# CSCB532

### Setting up Python Virtual Environment

Virtual Environment is used to manage Python packages for different projects. Using virtualenv allows you to avoid installing Python packages globally which could break system tools or other projects.

We use such a virtual environment to work in the same conditions in order to use the same dependencies needed to develop the project.

#### Installing virtualenv

```bash
python -m pip install virtualenv
```

##### Creating and activating a virtual environment

- [PyCharm](https://www.youtube.com/watch?v=W8C097f6Hcg)

- [VS Code](https://www.youtube.com/watch?v=W--_EOzdTHk) - up to the 4th minute

- Creating virtualenv - Windows/Linux, where venv is the name of the environement

  ```shell
  python -m venv venv
  ```

- Activating virtualenv - Windows

  ```
  .\venv\Scripts\activate
  ```

  Activating virtualenv - Linux

  ```
  venv/bin/activate
  ```

  

## Installing packages

```bash
python -m pip install -r requirements.txt
```

## Setting up Flask environement

We use different configurations depending on the environment *(development, production, testing)* in which the application is running.

- Windows

  ```bash
  set FLASK_APP=run.py
  set FLASK_ENV=development
  ```

  

- Linux

  ```bash
  export FLASK_APP=run.py
  export FLASK_ENV=development 
  ```

  

## Starting the app

- Flask CLI

  ```bash
  flask run
  ```

  

- Python

  ```
  python run.py
  ```

  