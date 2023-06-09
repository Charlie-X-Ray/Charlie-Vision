# Charlie-Vision

The AI behind Charlie X


## Setup

To start working on this repository, you will need to have miniconda/ anaconda installed,
I recommend installing miniconda.

The list of installers can be foudn on the [miniconda docs](https://docs.conda.io/en/latest/miniconda.html).

The installation guide was written with reference to their [macos install instructions](https://conda.io/projects/conda/en/stable/user-guide/install/macos.html)

### M1

If you are using a Mac running on M1, you should be able to use the following instructions.
First to install miniconda in your `$HOME` directory, run the following command to download the appropriate setup file:

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh -O ~/miniconda.sh
bash ~/miniconda.sh -p $HOME/miniconda
```

The installer prompts “Do you wish the installer to initialize Miniconda3 by running `conda init`?”
The website and I recommend “yes”.

To verify your install, check that you have conda version 22 or later by running:

```bash
conda --version
```

## Development

### GitHub

To start working on this repository, first clone it into your workspace

```bash
git clone https://github.com/Charlie-X-Ray/Charlie-Vision.git
cd Charlie-Vision
```

### Creating Conda Environment

Conda is an environment manager that lets us share the correct environment settings between everyone.
To use it run the following:

```bash
conda env create -f environment-opencv.yml
```
