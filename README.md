# **SIL Store API**

An API for a simple grocery store built with Django Rest Framework.

## **Table of Contents**

-   [Project Overview](#project-overview)
-   [Getting Started](#getting-started)
-   [Authentication](#authentication)
-   [API Endpoints](#api-endpoints)
-   [Testing](#testing)
-   [CI/CD](#cicd)

## **Project Overview**

This is an API for a simple grocery store that has the following capabilities:

-   Maintaining the store’s catalog \- product categories, products
-   Processing customer orders (with confirmation notifications for successful orders)

It is built using [Django REST Framework](https://www.django-rest-framework.org/) and a [PostgreSQL](https://www.postgresql.org/about/) database backend.

### **Prerequisites**

The following external dependencies are required/recommended to successfully run this project:

-   [Docker desktop](https://www.docker.com/products/docker-desktop/) (recommended)
-   [AfricasTalking](https://africastalking.com/) credentials (for SMS notifications)
-   An optional SMTP server (you can use [Mailpit](https://mailpit.axllent.org/), [Mailtrap](https://mailtrap.io/) or other SMTP testing tool).
-   [PostgreSQL](https://www.postgresql.org/about/) (required if you'll not be running the project using Docker compose)
-   An OpenID Connect provider for authentication (you can use [Keycloak](https://www.keycloak.org/) for dev/testing)

## **Getting Started**

### Installation using Docker (recommended)

1. Clone this repository

```bash
git clone https://github.com/AngeloKarugo/sil_store_api.git && cd sil_store_api
```

2. Create `.env` file

```bash
cp .env.example .env
```

Add your environment variables for the different services

3. Build and start the docker containers

```bash
docker-compose up --build
```

4. That's it, the app should be running now. Try accessing it at `http://localhost:8010`

### Manual setup

1. Perform step 1 & 2 from the [installation with docker procedure](#installation-using-docker-recommended).

2. Activate a Python virtual environment

3. Install packages

```bash
pip install -r requirements.txt
```

4. Run database migrations

```bash
python manage.py migrate
```

5. Run the app

```bash
python manage.py runserver
```

## **Authentication**

The APP uses OIDC authentication, and you will therefore need to create a profile on your OIDC provider to use for authentication.
For session-based auth (to use the browsable API), open `http://localhost:8010/oidc/authenticate` to authenticate with your auth provider.
For token-based auth (to use the API in http clients such as Postman) obtain an auth token from your provider and append it to your requests under the `Bearer` header.

## **API Endpoints**

The endpoints available for performing different actions in the app are documented in [the JSON schema](https://github.com/AngeloKarugo/sil_store_api/blob/main/api/api-schema.json). You can use the OpenAPI JSON schema to generate a Postman collection.

## **Testing**

To run tests:

```bash
python manage.py test
```

If you're interested in the test coverage, run

```bash
coverage run manage.py test && coverage report
```

## **CI/CD**

The project has a [GitHub Actions](https://github.com/features/actions) CI/CD workflow that:

-   runs tests
-   deploys the app to a Kind cluster
