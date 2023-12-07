# RSS-MS-Authorization

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)


This project is a part of a bigger project maintained [here](https://github.com/Ramin-RX7/RSS-Feed) called `RSS-Feed`.

> Although `RSS-Feed` is a complete project, several microservices are also implemented so it can be deployed with in multiple services.

This microservice is responsible to handle `authorization` section of the `RSS-Feed`.



## Responsibilities

- Register (client side)
- Login (client side)
- Get new refresh token
- Logout



## Setup

Docker file to start the project is placed inside the main repo directory. Though it's better to read more about how to deploy all `RSS-Feed` microservices together in [RSS-Feed docs](https://github.com/Ramin-RX7/RSS-Feed/tree/develop/docs/microservices/microservices.md).



## License

`RSS-MS-Authorization` is maintained under `GNU General Public License v3.0` license (read more [here](/LICENSE))
