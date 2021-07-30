[![Build Status](https://travis-ci.org/iRB-Lab/py-ga-VRPTW.svg)][travis-ci]
[![Python](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8%20%7C%203.9-blue.svg)][python]
[![License](https://img.shields.io/github/license/iRB-Lab/py-ga-VRPTW.svg)][license]
[![Last Commit](https://img.shields.io/github/last-commit/iRB-Lab/py-ga-VRPTW.svg)][commit]

# Customer crowdshipping model
A project aimed to simulate the customer crowd-shipping scenario. 
The agent-based model is built in AnyLogic, while data preparation, vehicle routing and data analysis is performed using Python. 
The Pypeline library is used to enable communication between AnyLogic and Python.
## Important Notes
### Project Origin (Backstory)
This project forms part of a Master's Thesis in Industrial Engineering.


#### Some Outstanding Forks:

## Contents
- [Installation](#installation)
    - [Requirements](#requirements)
    - [Installing with Virtualenv](#installing-with-virtualenv)
- [Quick Start](#quick-start)
- [Problem Sets](#problem-sets)
    - [Solomon's VRPTW Benchmark Problems](#solomons-vrptw-benchmark-problems1)
    - [Instance Definitions](#instance-definitions)
        - [Text File Format](#text-file-format)
        - [JSON Format](#json-format)
        - [Use Customized Instance Data](#use-customized-instance-data)
            - [Supported File Format](#supported-file-format)
            - [Directory Set-up](#directory-set-up)
            - [Convert `*.txt` to `*.json`](#convert-txt-to-json)
- [GA Implementation](#ga-implementation)
   
- [API Reference](#api-reference)
    - [Module: `gavrptw`](#module-gavrptw)
    - [Module: `gavrptw.core`](#module-gavrptwcore)
    - [Module: `gavrptw.utils`](#module-gavrptwutils)
- [File Structure](#file-structure)
- [Further Reading](#further-reading)
- [References](#references)
- [License](#license)

## Installation
### Requirements
- [Python 3.6 | 3.7 | 3.8][python]
- [Pip][pip]
- [Virtualenv][virtualenv]

### Installing with Virtualenv
On Unix, Linux, BSD, macOS, and Cygwin:

```sh
git clone https://github.com/iRB-Lab/py-ga-VRPTW.git
cd py-ga-VRPTW
virtualenv --python=python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

### Installing Pypeline on AnyLogic
Clone the Pypeline repository onto your local device: https://github.com/t-wolfeadam/AnyLogic-Pypeline. 
A guide to installing and use of the library is found there (on the readme file, as well as the user guide pdf). I will, however give a quick overview to enable a start.

In AnyLogic, under the palette tab, look in the bottom-left corner for the + button to add a library.

Select `Manage Libraries`. Click the `Add` button.

In the *Pypeline*  repository on your local device, open the `Export` folder.

Select the `Pypeline.jar` file as your new library. Your *Pypeline* library should now appear under the *palette* tab.

Drag the `Py Communicator` agent onto your `main` agent (working environment) and give it an appropriate name (e.g. 'pyCommunicator'). 
Under the new `Py Communicator` *properties* tab, for *"Command to call Python"*, select `path`. 

Under *"Python executable path"*, provide the path to the `python.exe` file in your virtual environment. (e.g. `"C:/Users/PC_Malan_ASUS/Customer_Crowdshipping_Model/venv/Scripts/python.exe"`)

(Include the quotations and note forward slashes for Windows users.)


## Model Quick Start
See [sample codes](#sample-codes).

### Data preparation

Run the `text2json.py` function in order to convert all problem sets from *txt* to the appropriate *json* format.

### Initialisation of AnyLogic model
The data contained on a benchmark problem json file are used to initialise the `customer`, `depot` and `delivery_Vehicle` agent populations.

Through use of the pyCommunicator, we import the data from the json file and use it to define the agents.
This is done at the initialisation of the model.

The parameter `fullDataPath` defines which json file to use. It is given form the current directory (e.g. `data/json/C101.json`)
The function `init_data` is run in Main `on startup`. 
It uses `pyCommunicator` to split the data into customer, depot and vehicle data (number of vehicles and capacity is seperate).

`init_data` then uses the seperated data to define and create the customer agent populations and the depot as a single agent. 
Delivery vehicles are added and their capacities set in a for loop based on the values from the json file*.

The key-value pairs in the json file are mapped onto the corresponding parameters in agents. 
The function furthermore explicitly places the agents on the correct location on the map. 

*If this problem is converted to include heterogeneous vehicles, I reccomend initialising the vehicle population similar to how the customer population is done currently.
This requires the vehicle data to be in a similar format.

## Problem Sets
### Solomon's VRPTW Benchmark Problems<sup>[1][solomon]</sup>
|Problem Set|Random|Clustered|Random & Clustered|
|:--|:--|:--|:--|
|Short Scheduling Horizon|R1-type|C1-type|RC1-type|
|Long Scheduling Horizon|R2-type|C2-type|RC2-type|

**Remarks:**

1. Solomon generated six sets of problems. Their design highlights several factors that affect the behavior of routing and scheduling algorithms. They are:
    - geographical data;
    - the number of customers serviced by a vehicle;
    - percent of time-constrained customers; and
    - tightness and positioning of the time windows.
2. The geographical data are randomly generated in problem sets R1 and R2, clustered in problem sets C1 and C2, and a mix of random and clustered structures in problem sets by RC1 and RC2.
3. Problem sets R1, C1 and RC1 have a short scheduling horizon and allow only a few customers per route (approximately 5 to 10). In contrast, the sets R2, C2 and RC2 have a long scheduling horizon permitting many customers (more than 30) to be serviced by the same vehicle.
3. The customer coordinates are identical for all problems within one type (i.e., R, C and RC).
4. The problems differ with respect to the width of the time windows. Some have very tight time windows, while others have time windows which are hardly constraining. In terms of time window density, that is, the percentage of customers with time windows, I created problems with 25, 50, 75 and 100% time windows.
4. The larger problems are 100 customer euclidean problems where travel times equal the corresponding distances. For each such problem, smaller problems have been created by considering only the first 25 or 50 customers.

### Instance Definitions
See [Solomon's website][solomon].

#### Text File Format
The text files corresponding to the problem instances can be found under the `data/text/` directory. Each text file is named with respect to its corresponding instance name, e.g.: the text file corresponding to problem instance **C101** is `C101.txt`, and locates at `data/text/C101.txt`.

Below is a description of the format of the text file that defines each problem instance (assuming 100 customers).

```
<Instance name>
<empty line>
VEHICLE
NUMBER     CAPACITY
  K           Q
<empty line>
CUSTOMER
CUST NO.  XCOORD.   YCOORD.    DEMAND   READY TIME  DUE DATE   SERVICE TIME
<empty line>
    0       x0        y1         q0         e0          l0            s0
    1       x1        y2         q1         e1          l1            s1
  ...      ...       ...        ...        ...         ...           ...
  100     x100      y100       q100       e100        l100          s100
```

**Remarks:**

1. All constants are integers.
2. `CUST NO.` 0 denotes the depot, where all vehicles must start and finish.
3. `K` is the maximum number of vehicles.
4. `Q` the capacity of each vehicle.
5. `READY TIME` is the earliest time at which service may start at the given customer/depot.
6. `DUE DATE` is the latest time at which service may start at the given customer/depot.
7. The value of time is equal to the value of distance.
8. As a backup, you can download a zip-file with the 100 customers instance definitions<sup>[2][100-customers]</sup> [here][100-customers-zip].

#### JSON Format
For the further convenience, a Python script named `text2json.py` is written to convert all problem instances from the **text file format** to **JSON format** and stored under the `data/json/` directory. 
Like the text files, each JSON file is named with respect to its corresponding instance name, e.g.: the JSON file corresponding to problem instance **C101** is `C101.json`, and locates at `data/json/C101.json`.

Below is a description of the format of the JSON file that defines each problem instance (assuming 100 customers).


```
{
    "instance_name" : "<Instance name>",
    "max_vehicle_number" : K,
    "vehicle_capacity" : Q,
    "depot" : {
        "x" : x0,
        "y" : y0
        "demand" : q0,
        "ready_time" : e0,
        "due_time" : l0,
        "service_time" : s0
    },
    "customers": [
            {
                "id": id1,
                "x" : x1,
                "y" : y2
                "demand" : q1,
                "ready_time" : e1,
                "due_time" : l1,
                "service_time" : s1
            },
    ...
            {
                "id": id100,
                "x" : x100,
                "y" : y100
                "demand" : q100,
                "ready_time" : e100,
                "due_time" : l100,
                "service_time" : s100
            }
        ],
}
```

**Remarks:**

1. It is crucial that the customer data is in this format, as AnyLogic defines the customer population from this.
2. `dist1_1` denotes the distance between Customer 1 and Customer 1, which should be 0, obviously.
3. To obtain the distance value between Customer 1 and Customer 2 in Python can be done by using `<json_data>['distance_matrix'][1][2]`, where `<json_data>` denotes the name of a Python `dict` object.

#### Use Customized Instance Data
You can customize your own problem instances.

##### Supported File Format
The customized problem instance data file should be either **text file format** or **JSON format**, exactly the same as the above given examples.

##### Directory Set-up
Customized `*.txt` files should be put under the `data\text_customize\` directory, and customized `*.json` files should be put under the `data\json_customize\` directory.

##### Convert `*.txt` to `*.json`
Run the `text2json_customize.py` script to convert `*.txt` file containing customized problem instance data to `*.json` file.

```sh
python text2json_customize.py
```

## GA Implementation



## API Reference
### Module: `gavrptw`
Excerpt from `gavrptw/__init__.py`:

```python
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
```

### Module: `gavrptw.core`
```python
route = ind2route(individual, instance)
```
```python
print_route(route, merge=False)
```
```python
eval_vrptw(individual, instance, unit_cost=1.0, init_cost=0, wait_cost=0, delay_cost=0)
```
```python
ind1, ind2 = cx_partialy_matched(ind1, ind2)
```
```python
individual, = mut_inverse_indexes(individual)
```
```python
run_gavrptw(instance_name, unit_cost, init_cost, wait_cost, delay_cost, ind_size, pop_size, \
    cx_pb, mut_pb, n_gen, export_csv=False, customize_data=False)
```

### Module: `gavrptw.utils`
```python
make_dirs_for_file(path)
```
```python
exist(path, overwrite=False, display_info=True)
```
```python
load_instance(json_file)
```
```python
text2json(customize=False)
```

## File Structure
```
├── data/
│   ├── json/
│   │   ├── <Instance name>.json
│   │   └── ...
│   ├── json_customize/
│   │   ├── <Customized instance name>.json
│   │   └── ...
│   ├── text/
│   │   ├── <Instance name>.txt
│   │   └── ...
│   └── text_customize/
│       ├── <Customized instance name>.txt
│       └── ...
├── results/
│   └── ...
├── gavrptw/
│   ├── __init__.py
│   ├── core.py
│   └── utils.py
├── text2json.py
├── text2json_customize.py
├── sample_R101.py
├── sample_C204.py
├── sample_customized_data.py
├── requirements.txt
├── README.md
├── LICENSE
├── .travis.yml
└── .gitignore
```

## Further Reading
**Distributed Evolutionary Algorithms in Python (DEAP)**

## References
1. [Solomon's VRPTW Benchmark Problems][solomon]
2. [100 Customers Instance Definitions][100-customers]
3. [Distributed Evolutionary Algorithms in Python (DEAP)][deap-pypi]

## License
[python]: https://docs.python.org/ "Python"
[pip]: https://pypi.python.org/pypi/pip "Pip"
[virtualenv]: https://virtualenv.pypa.io/en/stable/ "Virtualenv"

[solomon]: http://web.cba.neu.edu/~msolomon/problems.htm "Solomon's VRPTW Benchmark Problems"
[100-customers]: http://www.sintef.no/projectweb/top/vrptw/solomon-benchmark/100-customers/ "100 Customers Instance Definitions"
[100-customers-zip]: http://www.sintef.no/globalassets/project/top/vrptw/solomon/solomon-100.zip "100 Customers Instance Definitions (Zip)"

[deap-docs]: http://deap.readthedocs.org/ "Distributed Evolutionary Algorithms in Python (DEAP) Docs"
[deap-github]: https://github.com/deap/deap/ "Distributed Evolutionary Algorithms in Python (DEAP) GitHub"
[deap-pypi]: https://pypi.python.org/pypi/deap/ "Distributed Evolutionary Algorithms in Python (DEAP) PyPI"
