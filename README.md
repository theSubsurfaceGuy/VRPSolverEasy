# VRPSolverEasy [![Python package](https://github.com/inria-UFF/VRPSolverEasy/actions/workflows/python-package.yml/badge.svg)](https://github.com/inria-UFF/VRPSolverEasy/actions/workflows/python-package.yml)

This project is an implementation of VRPSolver, a package allows you to resolve routing problems by using the bapCod solver,(COIN-OR) CLP and CPLEX solver.

## Installation

There is two differents way to install `VRPSolverEasy` :

The first way is to install it with `pip`  :
```
python -m pip install VRPSolverEasy
```
The second way is to following this steps:

- Download the package and extract it into a local directory
- Move to this local directory and enter:
```
 python setup.py install
```
![Python](https://commons.wikimedia.org/wiki/File:Python-logo-notext.svg)
`VRPSolverEasy` requires a version of python  >= 3.7

## Examples

### Initialisation of model

After installation, if you want to create your first model you have to import the solver like this:
```
import VRPSolverEasy.src.solver as solver
```
#### Create model
```
model = solver.create_model()
```
#### Add vehicle types
```
model.add_VehicleType(
            id=1,
            startPointId=0,
            endPointId=0,
            name="VEH1",
            capacity=100,
            maxNumber=3,
            varCostDist=10,
            varCostTime=0.0,
            maxNumber=1,
            twEnd=50)
```
#### Add Customers
```
model.add_Customer(
            id=1,
            name="Cust1",
            serviceTime=3,
            penalty=2,
            twBegin=4,
            twEnd=5,
            demand=300)
```
#### Add Depots
```
model.add_Depot(
            id=1,
            name="Depot1",
            serviceTime=3,
            cost=2,
            twBegin=4,
            twEnd=5,
            capacity=300)
```
#### Add Links
```
model.add_Link(
            id=1,
            name="Link1",
            isDirected=False,
            startPointId=0,
            endPointId=0,
            distance=25,
            time=42,
            fixedCost=4)
```
#### Set parameters
```
model.set_Parameters(

            timeLimit=5,
            printLevel=1)
```
#### Solve model
```
model.solve()
```
## Documentation
