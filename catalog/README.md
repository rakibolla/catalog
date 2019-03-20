# Item Catalog Web App
By Bolla Rakesh
This web app is a project for the Udacity Full Stack Nano Degree

## About This Project
This project is mainly used for authorization and authentication of an user.

## In This Project
--> This Project contains Data_Setup file which contains classes with tables and columns
-->This Project contains database_init file which contains the data to be inserted into the tables and columns
-->This project contains main file which gives the working of adding,editing,deleting.

## Skills Required
1. Python
2. HTML
3. CSS
4. OAuth
5. Flask Framework
6.DataBaseModels


## How to Run
1. First install Vagrant in your computer.
2. Now install Virtual Box.
3. Open command prompt in your Item Catalog folder.
3. Now first initialize the Vagrant using the command:
	$ vagrant init ubuntu/xenial64
4. Log into Vagrant VM (`vagrant ssh`)
5. Navigate to `cd /vagrant` as instructed in terminal
6. The app imports requests which is not on this vm. Run pip install requests
7. Setup application database `python /Department_Hub/Data_Setup.py`
8. *Insert sample data `python /Department_Hub/database_init.py`
9. Run application using `python /Department_Hub/main.py`
10. Access the application locally using http://localhost:8086

--> Here you cannot perform any operations such as add, update and delete.

## Using Google Login
To perform working operations follow these steps:

1. Go to [Google Dev Console](https://console.developers.google.com)
2. Sign up or Login if prompted
3. Go to Credentials
4. Select Create Crendentials > OAuth Client ID
5. Select Web application
6. Enter name 'Department Hub'
7. Authorized JavaScript origins = 'http://localhost:8086'
8. Authorized redirect URIs = 'http://localhost:8086/login' && 'http://localhost:8086/gconnect'
9. Select Create
10. Copy the Client ID and paste it into the `data-clientid` in login.html
11. On the Dev Console Select Download JSON
12. Rename JSON file to client_secrets.json
13. Place JSON file in department hub directory that you cloned from here
14. Run application using python main.py

## JSON Endpoints
The following are open to the public:

allDepartmentJSON: `/DepartmentHub/JSON`
    - Displays the whole departments and employee details.

categoriesJSON: `/DepartmentHub/departmentName/JSON`
    - Displays all Departments.
	
employJSON: `/DepartmentHub/department/JSON`
	- Displays all Employee details

categoryEmployJSON: `/DepartmentHub/<path:department_name>/department/JSON`
    - Displays all Employee details of a specific Department.

EmployJSON: `/DepartmentHub/<path:department_name>/<path:departmentemploy_name>/JSON`
    - Displays a specific Employee details of a specific Department.
