# Catalog Project

Build an online catalog, where users can view catalog items. Logged in users are able to add items to the catalog database, and can edit and delete items that they created.

## Installation
You will need a Unix-Style terminal;
Mac / Linux: Use the regular terminal program
Windows: Download and install the Git Bash terminal. Download from git-scm.com.

You will need to run a Virtual Machine on your computer to run the SQL database server. To install and manage the Virtual Machine you will need to Download and install Vagrant and VirtualBox.

VirtualBox
Runs the Virtual Machine.
Download version 5.1, as newer versions are not compatible with Vagrant.
Ubuntu: Install using Ubuntu Software Center
All other systems: Download from https://www.virtualbox.org/wiki/Download_Old_Builds_5_1

Do not launch VirtualBox after installing it.

Vagrant
This is the software that configures the Virtual Machine and lets you share files between your computer and your Virtual Machine.

Download from https://www.vagrantup.com/downloads.html.

Windows: If you are prompted please allow network permissions to Vagrant.

Once Vagrant is installed, open your terminal and run vagrant --version
It should return the version number. This lets you know that Vagrant has successfully installed.

Virtual Machine Configuration
Download http://github.com/udacity/fullstack-nanodegree-vm

This will create a new directory containing the Virtual Machine files.
In your terminal cd to the vagrant file and start the virtual machine by running vagrant up (This can take a while).

Once you have started your Virtual Machine run vagrant ssh to login. You are now logged in to your Virtual Machine. cd to /vagrant so you are in the vagrant folder on the Virtual Machine.

Database Setup
In the terminal navigate to the catalog directory (\fullstack-nanodegree-vm\vagrant\catalog). Once in the catalog directory setup the database by entering: python database_setup.py

Once the database is complete, populate the database by running:
python addcategories.py
This will populate the database with categories, items and a user.
You will get a confirmation message in your terminal once the database has finished populating.

## Usage
Now the database is ready run: python application.py 
Open your web browser and go to localhost:8000/

This will run the code for my Online Catalog Application.