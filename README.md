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

### NUS HPC

Miniconda is stored as a module on NUS HPC. The instructions for accessing it was taken from their [Python guide](https://drive.google.com/drive/u/0/folders/1za8jGiPqaNLR3ys74CXMPDXKwIUKgUEB).
Simply run the following commands to setup

```bash
echo ". /app1/bioinfo/miniconda/4.9/etc/profile.d/conda.sh" >> ~/.bashrc
mkdir ~/conda_envs
echo "export CONDA_ENVS_PATH=~/conda_envs/" >> ~/.bashrc
```

Now to enable conda run the following:

```bash
. ~/.bashrc # This is only needed if you just edited your .bashrc file. A .bashrc file is run automatically everytime you login, so if you restarted terminal again this is unnecessary.
module load miniconda
conda activate base
```

You should see the `(base)` prefix added to your prompt.

## Development

### GitHub

To start working on this repository, first clone it into your workspace

```bash
git clone https://github.com/Charlie-X-Ray/Charlie-Vision.git
cd Charlie-Vision
```

### Creating Conda Environment

Conda is an environment and package manager that supposedly helps install packages and check their dependencies.

First start by creating an environment that uses `python3.11`. This will also give us access to `pip`:

```bash
conda create env -n cxr-pip python=3.11 -y
conda activate cxr-pip
```

You should see a `(cxr-pip)` suffix added to your prompt

Next we pip install a bunch of packages

```bash
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu121 #this also gives access to PIL
pip install pydicom pandas matplotlib opencv-python
```

This should be everything you need.

### Creating Conda Env From File (WIP)

Note that **This is bug prone, so I recommend following the steps above**

Run the following to load from a `.yml` file:

```bash
conda env create -f environment-pip.yml
```

To activate your environment run:

```bash
conda activate cxr-pip
```

You should see a prefix `(cxr-pip)` added to your prompt.

### Test Conda Envrionment

To test that the environment was created correctly run in the `Charlie-Vision` directory:

```bash
python test.py
```

If some of the imports fail, it means not all the pacakges were installed correctly.
Try deleting the created envrionment and repeating the creating conda environment steps.

If this all works, run `main.py` to draw boxes using the following:

```bash
python main.py
```
