# Vehicle Allocation System

This project is a FastAPI-based vehicle allocation system for employees of a company. The system allows employees to allocate a vehicle for themselves for a day, provided the vehicle has not already been allocated on that date. It also includes the ability to update or delete allocations before the allocation date, and to generate a history report of allocations with appropriate filters.

## Features
- **Vehicle Allocation:** Allocate a vehicle to an employee, ensuring the vehicle is available for that day.
- **CRUD Operations:** Create, update, and delete allocations before the allocation date.
- **History Report:** View a history of allocations with filter options (e.g., date, employee, vehicle).
- **Optimized for Load:** Optimized for performance, including caching with Redis.
- **Swagger Documentation:** Automatic API documentation available.
- **Dockerized:** Fully containerized using Docker and Docker Compose.

---

## Technologies Used

  - **FastAPI:** Backend framework for building APIs.
  - **MongoDB:** NoSQL database for storing allocations.
  - **Redis:** In-memory data structure store for caching.
  - **Docker:** Containerization platform.
  - **Uvicorn:** ASGI server for FastAPI applications.

## Installation and Setup

### Prerequisites
- **Docker**: Make sure you have Docker and Docker Compose installed on your system.

### Step-by-Step Instructions

1. **Clone the Repository**:
   ```bash
   git clone git@github.com:kamrulhasan2020/vehicle_allocation.git
   cd vehicle_allocation
   ```
   
2. **Environment Variables:**

    Before running the application, you need to configure the environment variables. A sample environment variable file named .env.example is included in the repository.

    Rename .env.example to .env to set up your local environment.
    Ensure to fill in the necessary values in the .env file according to your configuration.
   
3. **Build and Run the Application:**
    ```
   docker-compose up --build
   ```
4. **Access the Application:**
Once the app is running, you can access it via:
API Documentation (Swagger UI):
> http://localhost:8000/docs

OpenAPI Schema:
> http://localhost:8000/openapi.json


## Running Unit Tests

To run the unit tests for this FastAPI application, follow these steps:

1. **Open a terminal** and navigate to the project directory.

2. **Switch to the test environment** by renaming the environment file:
   ```bash
   mv .env.test .env
   ```
   This command will replace the current .env file with the test configuration.
3.  **Access the FastAPI Docker container by running the following command:**
    ``` 
    docker exec -it <container_name_or_id> /bin/bash
    ```
    Replace **<container_name_or_id>** with the actual name or ID of your FastAPI container.

4. **Run the unit tests using pytest:**
    ```
   pytest app/tests.py
   ```
   


## Deployment Thoughts
### Running the Application

To deploy the FastAPI application in a production environment, I recommend using Gunicorn as the ASGI server.

Here are my thoughts on setting it up:

***Gunicorn Configuration:***

Utilize Gunicorn to run the FastAPI application, setting the number of workers based on the server's CPU cores. A common formula is (2 * number_of_cores) + 1. For instance, if the server has 2 CPU cores, set the number of workers to 5.
Example Command:

    ```
    gunicorn app.main:app --workers 5 --bind 0.0.0.0:8000 --worker-class uvicorn.workers.UvicornWorker
    ```

Important: I would ensure to omit the --reload flag in production to prevent the application from restarting on code changes.

***Redis Connection Pool:***


Optimize the Redis connection pool size based on your application's needs. This can be adjusted in the application settings:

    import redis

    redis_pool = redis.ConnectionPool(
        host='redis',
        port=6379,
        db=0,
        max_connections=20  # Adjust this based on expected load
    )
    redis_client = redis.Redis(connection_pool=redis_pool)


***MongoDB Connection Pool:***

Similarly, configure the MongoDB connection pool size to accommodate your application's requirements:

        from motor.motor_asyncio import AsyncIOMotorClient

        mongo_client = AsyncIOMotorClient(
            'mongodb://mongo:27017',
            maxPoolSize=20  # Adjust based on expected load
        )
        db = mongo_client.your_database_name

## Maintenance Considerations

- **Monitoring:** I would implement monitoring tools to track the performance and load on Redis and MongoDB. Regularly review these metrics to adjust connection pool sizes as necessary.
- **Scaling:** As the application grows, I would consider horizontal scaling by deploying multiple instances of the application to manage increased load effectively.
- **Backup and Recovery:** I would regularly back up MongoDB and Redis data to prevent data loss. Plan a recovery strategy in case of failures.


## Security Considerations

- **Environment Variables:** In a real-world scenario, I would not include the .env file in the GitHub repository to protect sensitive information such as database credentials and API keys. This file is critical for maintaining security, and it should be handled with care.
- **For testing purposes,** I have included the .env file in this repository. However, it is crucial to use tools like .gitignore to prevent sensitive files from being tracked in version control.