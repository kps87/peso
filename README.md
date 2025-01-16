# PESO [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14633225.svg)](https://doi.org/10.5281/zenodo.14633225)

A Simple Potential Energy Surface Diagram Generator. 

![Animation](peso.gif)

# Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Input File Format](#input-file-format)
  - [PES Definition](#pes-definition)
  - [Reaction Formatting](#reaction-formatting)
    - [Colors](#colors)
    - [Linestyles](#linestyles)
    - [Linewidths](#linewidths)
    - [Labels](#labels)
  - [Global Formatting](#global-formatting)
    - [Fonts](#fonts)
    - [Global Colormaps](#global-colormaps)
- [PES Logic](#pes-logic)
- [Contributing](#contributing)
- [Citing](#citing)
- [License](#license)

## Installation

Install [anaconda](https://www.anaconda.com/download?utm_source=anacondadocs&utm_medium=documentation&utm_campaign=download&utm_content=installwindows) or [miniconda](https://docs.anaconda.com/miniconda/) for package management.

Once installed, verify the installation via

```bash
conda --version
conda info
```

The environment.yml file contained in the root directory of the repo can be used to install all required packages.

```bash
conda env create -f environment.yml
conda activate peso
python --version
```

## Usage

Before running, ensure you have activated the correct conda environment
```bash
conda activate peso
```

You can place your input files wherever you like, the ```./inputs/``` folder is recommended.

Outputs will automatically be written to the ```./outputs/``` folder.

To show the help menu containing the groups of commands you can run:
```bash
python peso.py --help
```
To show the help menu for a specific command:
```bash
python peso.py run --help
python peso.py run-all --help
```

To run an input file called ```pes.dat``` in the ```./inputs/``` folder and write it to a file called ```./outputs/pes.png```:
```bash
python peso.py run -i ./inputs/pes.dat -o pes.png
```

To run all input files in a folder called ```./inputs/``` and write those to the ```./outputs/``` directory
```bash
python peso.py run-all -i ./inputs/
```

## Input File Format
Input files are composed of sections, with three sections currently defined:
1. PES Definition (required)
2. Reaction Formatting (optional)
3. Global Formatting (optional)


### PES Definition
```
section: pes
name       energy    type     reactant   product
M1         0.0       MIN      nan        nan      
M2         50        MIN      nan        nan      
M3         60        MIN      nan        nan      
TS1        50        TS       M1         M2       
TS2        70        TS       M2         M3       
```

Two type codes are supported, *MIN* and *TS*. Both *MIN* and *TS* are stationary points on a PES, 
but *TS* are unique in that they also require definition of the reactant and product which the connect, hence the use of ```nan``` for the reactant and product specification for the minima.

Energies must be defined in kJ/mol.

### Reaction Formatting
Optional formatting can be applied on a per-reaction basis, based on the transition state label, in the *reactionFormat* section e.g.:

Four options are currently supported:
1. color
2. linestyle
3. linewidth
4. transition state labels (e.g. to remove labels for barrierless reactions)

A number of functional examples are provided in the ```./inputs/``` directory.

Generally, one can define different styles for a single reaction on multiple lines:

```
section: reactionFormat
TS1 color k
TS1 linestyle --
TS1 linewidth 2
TS1 label false
```

One can equally use the following to apply multiple styles to a single reaction in a single line:

```
section: reactionFormat
TS1 color k linestyle -- linewidth 2 label false
```

or the following to apply multiple styles to multiple reactions on multiple lines:

```
TS1 color k linestyle --
TS1 linewidth 2 label false
TS2 color #FF5733 linestyle :
```

The general format is:
```
TSName option1 value1 option2 value2 ... optionN valueN
```

The order of options does not matter, but option-value pairs must be ordered sensibly e.g. the following format is not sensible:

```
TS1 color linestyle linewidth b -. 2
```


#### Colors
Colors can be defined by a shorthand one-letter code which is directly compatible with matplotlib:

+ b: Blue
+ g: Green
+ r: Red
+ c: Cyan
+ m: Magenta
+ y: Yellow
+ k: Black

Hex codes, e.g. #FF5733, can also be applied in lieu of, and along with, one-letter codes:

```
section: reactionFormat
TS1 color b linestyle
TS2 color #FF5733 linestyle
```

#### Linestyles
Four shorthand codes which are directly compatible with matplotlib are supported:

+ *-* This is the default style.
+ -- Used for a line with dashes.
+ : Creates a dotted line.
+ -. Combines dashes and dots.

#### Linewidths
A floating point number. The default is 1.

#### Labels
Labels can optionally be disabled *via* ```label false```.
Use of ```label true``` has no effect since labels are included by default.

### Global Formatting
Some formatting options may apply to all parts of a PES.

The format for globals follows a similar approach to reaction-specific formatting:

```
section: global
option1 value1
option2 value2
...
optionN valueN
```

A number of global options are currently supported:
1. **pad-bimolecular**: adds spaces around "+" symbols for bimolecular reactions
2. **resolution**: defines the output image resolution, defaults to 1200 dpi. Lower resolutions are useful for testing with a high resolution suitable for publications.
3. **label-font**: allows users to [control the font applied](#fonts) to labels for minima and ts. Note that spaces **are** allowed in the font definition.
4. **label-loc**: allows users to apply a simple in-line labelling system rather using the global default of offset labels with energies
5. **show-labels**: disables all labels if included and set to false
6. **colormap**: allows users to select from a list of [pre-configured colormaps](#global-colormaps) 

```
section: global
pad-bimolecular true
resolution 600
label-font DejaVu Serif
colormap brg
label-loc inline
show-labels false
```

Examples are provided in ```./inputs/```.

See the sections on [fonts](#fonts) and [colormaps](#global-colormaps) for further information on styling.

### Fonts
Matplotlib comes with default font styles and also searches a specific subset of directories for any fonts the user may have installed on their system.

Fonts and their locations vary from operating system to operating system.

A utility is provided to get a list of fonts which the matplotlib font manager is aware of. To run this utility:

```bash
python -m utils.fonts.list
```

The fonts will be written to screen and to a file called ```fonts.txt```.

A second utility is provided to generate example inputs for each available font:

```bash
python -m utils.fonts.gen
python peso.py run-all
```

The first command above will generate examples in ```./inputs``` and the second command will run all examples in the ```./inputs``` directory.

### Global Colormaps
A set of pre-configured colormaps are provided based on matplotlib defaults.

These colormaps are opt-in:
1. by default no global colormap will be applied and the entire surface will be black.
2. users can override the global colormap at the reaction level via [reaction-specific options](#colors)

To view a list of supported colormap codes, generate a set of example inputs, and run those inputs use the following commands respectively: 

```bash
python -m utils.colormap.list
python -m utils.colormap.gen
python peso.py run-all
```

## PES Logic
Drawing a potential energy surface requires defining the *x* and *y* coordinates of *stationary points*, and then connecting those coordinates *via*
some arbitrary curve.

Since the *y* coordinates are fixed by the input energies, initially we must define some logic to place *stationary points* along the *x*-axis (the reaction coordinates).

Minima (defined by type *MIN* in the input file) are placed at equally spaced but arbitrary *x*-coordinates **in the order they are defined in the input file**.

Transition states are placed **halfway between** the minima to which they are connected.

Once all minima and transition states have had their *x*-coordinates fixed, and together with the *y*-coordinates defined by the input energies, 
we can proceed to connect each stationary point *via* some arbitrary curve. These curves are drawn on a *per-reaction basis*.

Each reaction is split into 4 components:
+ Reactant → Reactant-TS midpoint
+ Reactant-TS midpoint → TS
+ TS → TS-Product midpoint
+ TS-Product midpoint → Product

and a harmonic curve is drawn for each component, giving a pleasing visual representation of the potential energy surface.


## Contributing

Pull requests and feature requests are welcome.

## Citing
If you use this project in your research, please cite it as follows:

Kieran Patrick Somers. (2025). PESO: A Simple Potential Energy Surface Diagram Generator, Zenodo DOI: [https://doi.org/10.5281/zenodo.14633225](https://doi.org/10.5281/zenodo.14633225)

## License

[MIT](https://choosealicense.com/licenses/mit/)