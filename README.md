## Running the project
Project can be run failry easily with the use of docker compose. You can get docker with all the components [here](https://docs.docker.com/get-docker/).
1. Clone the repository
2. Fill the `.env` file with your environmental variables. (optionaly change some things in Dockerfile and docker-compose.yaml)
   so that it will look like (without '):
   'EMAIL = "your_email"
    PASSWORD = "your_emails_password'
   If this file is not present create it in vehicle-delivery/VehicleDelivery/VehicleDelivery (at same folder where is settings.py).
   This email is for sending confirmation mails to customers and users.
4. Fill the `admin.env` file like look like (without '):
   'Admin_username=your_username
    Admin_mail=your_email
    Admin_password=your_password'
   If this file is not present create it in vehicle-delivery/VehicleDelivery/Main
   This is important so that default user will be created. Later this user can be changed.
6. run `docker compose build`
7. run `docker compose up -d`
