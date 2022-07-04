# Staycation Portal

<p align="center">
  <img src="./misc/portal.png">
</p>

<p align="center">
    <img src="https://www.vectorlogo.zone/logos/pocoo_flask/pocoo_flask-icon.svg">
    <img src="https://www.vectorlogo.zone/logos/w3_html5/w3_html5-icon.svg">
    <img src="https://www.vectorlogo.zone/logos/getbootstrap/getbootstrap-icon.svg">
    <img src="https://www.vectorlogo.zone/logos/javascript/javascript-icon.svg">
    <img src="https://www.vectorlogo.zone/logos/mongodb/mongodb-icon.svg">
</p>

The **Staycation Portal** is a full stack web application developed with the [Flask](https://flask.palletsprojects.com/en/2.1.x/) framework. This project is developed as part of the [ICT239: Web Application Development](https://www.suss.edu.sg/courses/detail/ict239) module at Singapore University of Social Sciences (SUSS).

## Table of Contents
- [Staycation Portal](#staycation-portal)
  - [Table of Contents](#table-of-contents)
  - [Description](#description)
  - [Getting Started](#getting-started)
    - [Requirements](#requirements)
    - [Poetry](#poetry)
    - [Docker](#docker)
  - [Project Organisation](#project-organisation)

## Description

The **Staycation Portal** is a platform that designed to enable consumer to register themselves to view staycation packages available, and book the package if they found that a particular one of the packages is what they need.

Meanwhile, from a business adminstrator point-of-view, they can login the website as an admin user to batch upload staycation packages, registered users, and booking records; while also view dashboad that summarizes incoming staycation booking over a certain period of time.



## Getting Started

To run the project, I highly advised you create a virtual environment to self-contain the necessary dependencies required to generate recommendations.

### Requirements

```
TBC
```

### Poetry

This project adopts [poetry](https://python-poetry.org/) for dependency management.

To install all require packages and dependencies:
```bash
poetry install
```
Subsequently, to enter the virtual env created by poetry and execute the application:
```bash
poetry shell

# make shell script executable
chmod +x ./start.sh
# run shell script to start application
./start.sh
```

### Docker

Other than poetry, [Docker]() is also available to run the application in a docker container.

```docker
TBC
```

## Project Organisation

```
.
├── LICENSE
├── README.md
├── app
│   ├── __init__.py
│   ├── app.py
│   ├── assets
│   │   ├── css
│   │   │   └── custom.css
│   │   ├── data
│   │   │   ├── booking.csv
│   │   │   ├── staycation.csv
│   │   │   └── users.csv
│   │   ├── img
│   │   │   ├── admin.jpeg
│   │   │   └── sidebar_background.jpeg
│   │   └── js
│   │       ├── dashboard.js
│   │       ├── dashboard_barchart_hotel.js
│   │       └── dashboard_barchart_user.js
│   ├── auth.py
│   ├── book.py
│   ├── dashboard.py
│   ├── forms.py
│   ├── staycation.py
│   ├── templates
│   │   ├── _render_field.html
│   │   ├── bar_chart.html
│   │   ├── base.html
│   │   ├── booking.html
│   │   ├── dashboard.html
│   │   ├── login.html
│   │   ├── packages.html
│   │   ├── register.html
│   │   ├── trend_chart.html
│   │   └── upload.html
│   └── users.py
├── poetry.lock
├── pyproject.toml
├── requirements.txt
└── start.sh
```
