# Eclectic Eclipses | Python Code Jam 2024

> What about confusing clutter? Information overload? Doesn't data have to be "boiled down" and "simplified"? These common questions miss the point, for the quantity of detail is an issue completely separate from the difficulty of reading. Clutter and confusion are failures of design, not attributes of information.”
> ― Edward R. Tufte, Envisioning Information

 This project has been created keeping this quote in mind, what are we to do with ourselves when we are bombared with the information from all sides, as quoted clutter and confusion are failures of design, to properly navigate the information given the best we can do is organize it and handle the load of information.

Welcome to the code repository of `Eclectic Eclipses` for the Python Discord Code Jam 2024!


## Features

Our discord bot has following features:

- [ToDo app](./app/features/README.md/#ToDo)
- [Dictionary](./app/features/README.md/#Dictionary)
- [Calculator](./app/features/README.md/#Calculator)
- [Reminder](./app/features/README.md/#Reminder)

The user guide for each features can be found in the README in features folder

## User Guide

Before you can use the bot, there are some setup steps you need to follow. This ensures the application works flawlessly on your local machine.


### Prerequisites

1. **Installation**: Before anything else, you need to set up the environment. Please follow our detailed [installation](#installation) guide to get everything in place.

2. **Create an application on Discord**: You need an application to run the bot, you can create an application (bot) by following the instructions on this [page](https://discord.com/developers/docs/quick-start/getting-started)

3. **Invite the bot**: You need to invite the bot so it can run commands on your channels / server for your self. You can invite the bot by following the instructions on this [page](https://discordpy.readthedocs.io/en/stable/discord.html#inviting-your-bot)

3. **Running the discord bot**: Once installed, the next step is to run the bot. To start the bot, please follow the guide on [how to run the project](#how-to-run-the-project).


### Using the App

## Installation

Below are instructions to install this project.

To develop this project on your local machine, follow the steps outlined below.

> **Note**: Ensure you have Python version 3.12 installed. If not, download it from [here](https://www.python.org/downloads/).

1. This project uses [Poetry](https://python-poetry.org/) as a dependency manager. Run the following command to install Poetry:

```bash
python -m pip install poetry==1.8.3
```


2. Next, navigate to the folder where you want the repository to be stored and run the following command to clone the git repository:

```bash
git clone https://github.com/Istalantar/scj2024-eclectic-eclipses
```

3. Navigate to the root of the repository and run the following command. Poetry will create a virtual environment and install all the necessary dependencies in it.

```bash
poetry install
```

4. Optionally, if you want to contribute to this project, install the pre-commit hook for your local repository by running the following command:

```bash
poetry run pre-commit install
```

5. You're all set! You can now run, develop, build, and test the project in your local development environment.

## How to Run the Project

1. Add the TOKEN for bot and DICTIONARY_KEY to the .env file

2. Run the bot.py script in app folder

3. That's it, now you can run all the commands and functionalities of our bot !

## Dictionary feature
The dictionary uses Merriam Webster online dictionary to get word definitions.
To be able to use the dictionaries API a KEY is required.
Add the following to your `.env` file in the `app` folder.
```shell
DICTIONARY_KEY=3bd9767c-ba7d-4f88-b283-7c1e0e346463
```

## Contributors

This project was built by `Eclectic Eclipses` team as part of the Python Discord Code Jam 2024. These are the team members and their main contributions:

| Avatar                                                     | Name                                        | Main contributions            |
| ---------------------------------------------------------- | ------------------------------------------- | ----------------------------- |
| <img src="https://github.com/Istalantar.png" width="50">   | [Istalantar](https://github.com/Istalantar) | Repository setup, ToDo functionality |
| <img src="https://github.com/HyTurtle.png" width="50">     | [HyTurtle](https://github.com/HyTurtle)     | DB Implementation             |
| <img src="https://github.com/maxyodedara5.png" width="50"> | [Maxy](https://github.com/maxyodedara5)     | Dictionary functionality |
| <img src="https://github.com/Ryan-Har.png" width="50">     | [Ryan](https://github.com/Ryan-Har)         | Reminder functionality         |
| <img src="https://github.com/KeshAzar.png" width="50">     | [Azargeth](https://github.com/KeshAzar)     | Calculator functionality      |
