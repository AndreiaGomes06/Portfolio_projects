# ELT project with docker
This project is a custom Extract-Load-Transform (ELT) project that leverages Docker, Postgres, and Airflow to execute a basic ELT workflow.

## Project summary
This project was built from scratch, using a source PostgreSQL database with sample data, a destination PostgreSQL database, and a Python environment to execute the ELT script.
Then, DBT was used to transform the data from the destination database, and a CRON job was also applied to automate the ELT, scheduled to run the ELT script at specified intervals, ensuring that the data in the destination PostgreSQL database is regularly updated with the latest data from the source database.
To automate this process more efficiently, the Airflow orchestration tool was used, creating DAG's to run the ELT script and DBT transformation.

### To Start the project
1. Begin by confirming that Docker and Docker Compose are installed on your system.
2. Next, clone this repository to your local machine.
3. Navigate to the repository directory and execute ```docker compose up init-airflow -d``` to initialize the Airflow container and than run ```docker compose up```.
