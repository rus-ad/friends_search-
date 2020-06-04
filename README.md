# Friends search - Non-profit project for the closed use of a narrow circle of people

To start the service:
1. Create a database PosgreSQL in docker
2. Collect data from the Internet in the database (folder)
3. Create an image service from the docker file
4. Bind the database image and service
5. Run the image

The models used in the project are very demanding on the packages on which they depend. 
All dependencies are listed in src/requirements.txt
