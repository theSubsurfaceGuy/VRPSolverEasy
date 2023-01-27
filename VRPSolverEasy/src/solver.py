"""This module solves vehicle routing problems using branch&cut&price methods"""

import ctypes as _c
import json
import platform
import os
import sys
from VRPSolverEasy.src import constants
if sys.version_info > (3, 7):
    import collections.abc as collections
else:
    import collections

########
__version__ = "0.0.1"
__author__ = "Najib ERRAMI Ruslan SADYKOV Eduardo UCHOA Eduardo QUEIROGA"
__copyright__ = "Copyright VRPYSolver, all rights reserved"
__email__ = "najib.errami@inria.fr"


class PropertyError(Exception):
    """Exception raised for errors in the input property.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, prefix=str(), code=0, str_list=""):
        self.message = prefix + constants.ERRORS_PROPERTY[code] + str_list
        super().__init__(self.message)


class ModelError(Exception):
    """ Exception raised for errors in the model.

    Attributes:
        message -- explanation of the error
   """

    def __init__(self, code=0):
        self.message = constants.ERRORS_MODEL[code]
        super().__init__(self.message)


class VehicleTypesDict(collections.MutableMapping, dict):
    """Dictionary of vehicle types

    key (int): Id of vehicle type
    value: class Vehicle type

    """

    def __getitem__(self, key):
        return dict.__getitem__(self, key)

    def __setitem__(self, key, value):
        if not isinstance(key, (int)):
            raise PropertyError(constants.KEY_STR, constants.INTEGER_PROPERTY)
        if not isinstance(value, (VehicleType)):
            raise PropertyError(str(), constants.VEHICLE_TYPE_PROPERTY)
        if value.id != key:
            raise PropertyError(str(), constants.DICT_PROPERTY)
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        dict.__delitem__(self, key)

    def __iter__(self):
        return dict.__iter__(self)

    def __len__(self):
        return dict.__len__(self)

    def __contains__(self, x):
        return dict.__contains__(self, x)

    def values(self, debug=False):
        if len(dict.values(self)) == 0:
            raise ModelError(constants.MIN_VEHICLE_TYPES_ERROR)
        return list(value.get_vehicle_type(debug)
                    for value in dict.values(self))


class PointsDict(collections.MutableMapping, dict):
    """Dictionary of points ( depots and customers)

    key (int): Id of point
    value: class Customer or Depot

    """

    def __getitem__(self, key):
        return dict.__getitem__(self, key)

    def __setitem__(self, key, value):
        if not isinstance(key, (int)):
            raise PropertyError(constants.KEY_STR, constants.INTEGER_PROPERTY)
        if not isinstance(value, (Point)):
            raise PropertyError(str(), constants.POINT_PROPERTY)
        if value.id != key:
            raise PropertyError(str(), constants.DICT_PROPERTY)
        if dict.__len__(self) + 1 > 1022:
            raise PropertyError(
                constants.NB_POINTS_STR,
                constants.LESS_MAX_POINTS_PROPERTY)
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        dict.__delitem__(self, key)

    def __iter__(self):
        return dict.__iter__(self)

    def __len__(self):
        return dict.__len__(self)

    def __contains__(self, x):
        return dict.__contains__(self, x)

    def values(self, debug=False):
        if len(dict.values(self)) == 0:
            raise ModelError(constants.MIN_POINTS_ERROR)
        return list(value.get_point(debug) for value in dict.values(self))


class LinksDict(collections.MutableMapping, dict):
    """Dictionary of links

    key (str): name of link
    value: class Customer or Depot

    """

    def __getitem__(self, key):
        return dict.__getitem__(self, key)

    def __setitem__(self, key, value):
        if not isinstance(key, (str)):
            raise PropertyError(constants.KEY_STR, 3)
        if not isinstance(value, (Link)):
            raise PropertyError(str(), 12)
        if value.name != key:
            raise PropertyError(str(), constants.DICT_PROPERTY)
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        dict.__delitem__(self, key)

    def __iter__(self):
        return dict.__iter__(self)

    def __len__(self):
        return dict.__len__(self)

    def __contains__(self, x):
        return dict.__contains__(self, x)

    def values(self, debug=False):
        if len(dict.values(self)) == 0:
            raise ModelError(constants.MIN_LINKS_ERROR)
        return list(value.get_link(debug) for value in dict.values(self))


class VehicleType:
    """Define a vehicle type with different attributes.

    Additional informations:
        max_number ---- number of vehicles available
        var_cost_dist -- variable cost per unit of distance
        var_cost_time -- variable cost per unit of time
        tw_begin -- time windows begin
        tw_end -- time windows end
    """

    def __init__(
            self,
            id: int,
            start_point_id: int,
            end_point_id: int,
            name=str(),
            capacity=0,
            fixed_cost=0.0,
            var_cost_dist=0.0,
            var_cost_time=0.0,
            max_number=1,
            tw_begin=0,
            tw_end=0):
        self.name = name
        self.id = id
        self.capacity = capacity
        self.fixed_cost = fixed_cost
        self.var_cost_dist = var_cost_dist
        self.var_cost_time = var_cost_time
        self.max_number = max_number
        self.start_point_id = start_point_id
        self.end_point_id = end_point_id
        self.tw_begin = tw_begin
        self.tw_end = tw_end

    # a getter function of id
    @property
    def id(self):
        return self._id

    # a setter function of id
    @id.setter
    def id(self, id):
        if not isinstance(id, (int)):
            raise PropertyError(constants.ID_STR, constants.INTEGER_PROPERTY)
        if id < 1:
            raise PropertyError(
                constants.ID_STR,
                constants.GREATER_ONE_PROPERTY)
        self._id = id

    @property
    def name(self):
        """getter function of name"""
        return self._name

    @name.setter
    def name(self, name):
        """setter function of name"""
        if not isinstance(name, (str)):
            raise PropertyError(constants.VEHICLE_TYPE.NAME.value,
                                constants.STRING_PROPERTY)
        self._name = name

    @property
    def capacity(self):
        """getter function of capacity"""
        return self._capacity

    @capacity.setter
    def capacity(self, capacity):
        """setter function of capacity"""
        if not isinstance(capacity, (int)):
            raise PropertyError(constants.VEHICLE_TYPE.CAPACITY.value,
                                constants.INTEGER_PROPERTY)
        if capacity < 0:
            raise PropertyError(constants.VEHICLE_TYPE.CAPACITY.value,
                                constants.GREATER_ZERO_PROPERTY)
        self._capacity = capacity

    @property
    def fixed_cost(self):
        """getter function of fixed_cost"""
        return self._fixed_cost

    @fixed_cost.setter
    def fixed_cost(self, fixed_cost):
        """setter function of fixed_cost"""
        if not isinstance(fixed_cost, (int, float)):
            raise PropertyError(constants.VEHICLE_TYPE.FIXED_COST.value,
                                constants.NUMBER_PROPERTY)
        self._fixed_cost = fixed_cost

    @property
    def var_cost_dist(self):
        """getter function of var_cost_dist"""
        return self._var_cost_dist

    @var_cost_dist.setter
    def var_cost_dist(self, var_cost_dist):
        """setter function of var_cost_dist"""
        if not isinstance(var_cost_dist, (int, float)):
            raise PropertyError(constants.VEHICLE_TYPE.VAR_COST_DIST.value,
                                constants.NUMBER_PROPERTY)
        self._var_cost_dist = var_cost_dist

    @property
    def var_cost_time(self):
        """getter function of var_cost_time"""
        return self._var_cost_time

    @var_cost_time.setter
    def var_cost_time(self, var_cost_time):
        """setter function of var_cost_time"""
        if not isinstance(var_cost_time, (int, float)):
            raise PropertyError(constants.VEHICLE_TYPE.VAR_COST_TIME.value,
                                constants.NUMBER_PROPERTY)
        self._var_cost_time = var_cost_time

    # a getter function of max_number

    @property
    def max_number(self):
        """getter function of max_number"""
        return self._max_number

    @max_number.setter
    def max_number(self, max_number):
        """setter function of max_number"""
        if not isinstance(max_number, (int)):
            raise PropertyError(constants.VEHICLE_TYPE.MAX_NUMBER.value,
                                constants.INTEGER_PROPERTY)
        if max_number < 0:
            raise PropertyError(constants.VEHICLE_TYPE.MAX_NUMBER.value,
                                constants.GREATER_ZERO_PROPERTY)
        self._max_number = max_number

    @property
    def start_point_id(self):
        """getter function of start_point_id"""
        return self._start_point_id

    @start_point_id.setter
    def start_point_id(self, start_point_id):
        """setter function of start_point_id"""
        if not isinstance(start_point_id, (int)):
            raise PropertyError(constants.VEHICLE_TYPE.START_POINT_ID.value,
                                constants.INTEGER_PROPERTY)
        if start_point_id < 0:
            raise PropertyError(constants.VEHICLE_TYPE.START_POINT_ID.value,
                                constants.GREATER_ZERO_PROPERTY)
        self._start_point_id = start_point_id

    @property
    def end_point_id(self):
        """getter function of end_point_id"""
        return self._end_point_id

    @end_point_id.setter
    def end_point_id(self, end_point_id):
        """setter function of end_point_id"""
        if not isinstance(end_point_id, (int)):
            raise PropertyError(constants.VEHICLE_TYPE.END_POINT_ID.value,
                                constants.INTEGER_PROPERTY)
        if end_point_id < 0:
            raise PropertyError(constants.VEHICLE_TYPE.END_POINT_ID.value,
                                constants.GREATER_ZERO_PROPERTY)
        self._end_point_id = end_point_id

    @property
    def tw_begin(self):
        """getter function of tw_begin"""
        return self._tw_begin

    @tw_begin.setter
    def tw_begin(self, tw_begin):
        """setter function of tw_begin"""
        if not isinstance(tw_begin, (int, float)):
            raise PropertyError(
                constants.VEHICLE_TYPE.TIME_WINDOWS_BEGIN.value,
                constants.NUMBER_PROPERTY)
        self._tw_begin = tw_begin

    @property
    def tw_end(self):
        """getter function of tw_end"""
        return self._tw_end

    @tw_end.setter
    def tw_end(self, tw_end):
        """setter function of tw_end"""
        if not isinstance(tw_end, (int, float)):
            raise PropertyError(
                constants.VEHICLE_TYPE.TIME_WINDOWS_END.value,
                constants.NUMBER_PROPERTY)
        self._tw_end = tw_end

    def get_vehicle_type(self, debug=False):
        """Get all components of a VehicleType which are differents of
        default value"""
        veh_type = {}
        veh_type[constants.VEHICLE_TYPE.ID.value] = self.id
        veh_type[constants.VEHICLE_TYPE.
                 START_POINT_ID.value] = self.start_point_id
        veh_type[constants.VEHICLE_TYPE.END_POINT_ID.value] = self.end_point_id
        if self._name != str() or debug:
            veh_type[constants.VEHICLE_TYPE.NAME.value] = self.name
        if self._capacity != 0 or debug:
            veh_type[constants.VEHICLE_TYPE.CAPACITY.value] = self.capacity
        if self._fixed_cost != 0 or debug:
            veh_type[constants.VEHICLE_TYPE.FIXED_COST.value] = self.fixed_cost
        if self._var_cost_dist != 0 or debug:
            veh_type[constants.VEHICLE_TYPE.
                     VAR_COST_DIST.value] = self.var_cost_dist
        if self._var_cost_time != 0 or debug:
            veh_type[constants.VEHICLE_TYPE.
                     VAR_COST_TIME.value] = self.var_cost_time
        if self._max_number != 0 or debug:
            veh_type[constants.VEHICLE_TYPE.MAX_NUMBER.value] = self.max_number
        if self._tw_begin != 0 or debug:
            veh_type[constants.VEHICLE_TYPE.
                     TIME_WINDOWS_BEGIN.value] = self.tw_begin
        if self._tw_end != 0 or debug:
            veh_type[constants.VEHICLE_TYPE.
                     TIME_WINDOWS_END.value] = self.tw_end
        return veh_type

    def __repr__(self):
        return repr(self.get_vehicle_type())


class Point:
    """Define a point of graph(customer or depot).

    Additional informations:
        service_time -- It can represent the time of
            loading or unloading.
        penalty_or_cost -- if the point is a customer
            we can specify penalty for not visiting the customer
        ---------------- otherwise, if the point is a depot we can
            specify a cost to using the depot
        tw_begin -- time windows begin
        tw_end -- time windows end
        incompatible_vehicles -- id of vehicles that cannot deliver
            the customer or not accepted in a depot
    """

    def __init__(self, id, name=str(), id_customer=0, penalty_or_cost=0.0,
                 service_time=0, tw_begin=0, tw_end=0, demand_or_capacity=0,
                 incompatible_vehicles=[]):
        self.name = name
        self.id_customer = id_customer
        self.id = id
        self.service_time = service_time
        self.tw_begin = tw_begin
        self.tw_end = tw_end
        self.time_windows = (self.tw_begin, self.tw_end)
        self.penalty_or_cost = penalty_or_cost
        self.demand_or_capacity = demand_or_capacity
        self.demand = demand_or_capacity
        self.capacity = demand_or_capacity
        self.incompatible_vehicles = incompatible_vehicles

    # using property decorator
    @property
    def id(self):
        """getter function of id"""
        return self._id

    @id.setter
    def id(self, id):
        """setter function of id"""
        if not isinstance(id, (int)):
            raise PropertyError(constants.POINT.ID.value,
                                constants.INTEGER_PROPERTY)
        if id < 0:
            raise PropertyError(constants.POINT.ID.value,
                                constants.GREATER_ZERO_PROPERTY)
        if id > 10000:
            raise PropertyError(constants.POINT.ID.value,
                                constants.LESS_MAX_POINTS_ID_PROPERTY)
        self._id = id

    @property
    def name(self):
        """getter function of name"""
        return self._name

    @name.setter
    def name(self, name):
        """setter function of name"""
        if not isinstance(name, (str)):
            raise PropertyError(constants.POINT.NAME.value,
                                constants.STRING_PROPERTY)
        self._name = name

    @property
    def id_customer(self):
        """getter function of capacity"""
        return self._id_customer

    @id_customer.setter
    def id_customer(self, id_customer):
        """setter function of capacity"""
        if not isinstance(id_customer, (int)):
            raise PropertyError(constants.POINT.ID_CUSTOMER.value,
                                constants.INTEGER_PROPERTY)
        if id_customer < 0:
            raise PropertyError(constants.POINT.ID_CUSTOMER.value,
                                constants.GREATER_ZERO_PROPERTY)
        if id_customer > 1022:
            raise PropertyError(constants.POINT.ID_CUSTOMER.value,
                                constants.LESS_MAX_POINTS_PROPERTY)
        self._id_customer = id_customer

    @property
    def penalty(self):
        """getter function of penalty"""
        return self._penalty_or_cost

    @penalty.setter
    def penalty(self, penalty):
        """setter function of penalty"""
        if not isinstance(penalty, (int, float)):
            raise PropertyError(constants.POINT.PENALTY.value,
                                constants.INTEGER_PROPERTY)
        self._penalty_or_cost = penalty

    @property
    def cost(self):
        """getter function of cost"""
        return self._penalty_or_cost

    @cost.setter
    def cost(self, cost):
        """setter function of cost"""
        if not isinstance(cost, (int, float)):
            raise PropertyError(constants.POINT.COST.value,
                                constants.INTEGER_PROPERTY)
        self._penalty_or_cost = cost

    @property
    def service_time(self):
        """getter function of service_time"""
        return self._service_time

    @service_time.setter
    def service_time(self, service_time):
        """setter function of service_time"""
        if not isinstance(service_time, (int, float)):
            raise PropertyError(constants.POINT.SERVICE_TIME.value,
                                constants.NUMBER_PROPERTY)
        self._service_time = service_time

    @property
    def tw_begin(self):
        """getter function of tw_begin"""
        return self._tw_begin

    @tw_begin.setter
    def tw_begin(self, tw_begin):
        """setter function of tw_begin"""
        if not isinstance(tw_begin, (int, float)):
            raise PropertyError(constants.POINT.TIME_WINDOWS_BEGIN.value,
                                constants.NUMBER_PROPERTY)
        self._tw_begin = tw_begin

    @property
    def tw_end(self):
        """getter function of tw_end"""
        return self._tw_end

    @tw_end.setter
    def tw_end(self, tw_end):
        """setter function of tw_end"""
        if not isinstance(tw_end, (int, float)):
            raise PropertyError(constants.POINT.TIME_WINDOWS_END.value,
                                constants.NUMBER_PROPERTY)
        self._tw_end = tw_end

    @property
    def time_windows(self):
        """getter function of time windows"""
        return self._time_windows

    @time_windows.setter
    def time_windows(self, timeWindow):
        """setter function of time windows"""
        if not isinstance(timeWindow, (tuple)):
            raise PropertyError(
                constants.POINT.TIME_WINDOWS.value,
                constants.TUPLE_PROPERTY)
        else:
            if len(timeWindow) != 2:
                raise PropertyError(
                    constants.POINT.TIME_WINDOWS.value,
                    constants.TUPLE_PROPERTY)
            if not isinstance(timeWindow[0], (int, float)
                              ) or not isinstance(timeWindow[1], (int, float)):
                raise PropertyError(constants.POINT.TIME_WINDOWS_BEGIN.value,
                                    constants.NUMBER_PROPERTY)

        self._tw_begin = timeWindow[0]
        self._tw_end = timeWindow[1]
        self._time_windows = timeWindow

    @property
    def demand(self):
        """getter function of demand"""
        return self._demand_or_capacity

    # a setter function of demand
    @demand.setter
    def demand(self, demand):
        """setter function of demand"""
        if not isinstance(demand, (int)):
            raise PropertyError(constants.POINT.DEMAND.value,
                                constants.INTEGER_PROPERTY)
        if demand < 0:
            raise PropertyError(constants.POINT.DEMAND.value,
                                constants.GREATER_ZERO_PROPERTY)
        self._demand_or_capacity = demand
        self._demand = demand

    # a getter function of capacity
    @property
    def capacity(self):
        """getter function of capacity"""
        return self._demand_or_capacity

    # a setter function of capacity
    @capacity.setter
    def capacity(self, capacity):
        """setter function of capacity"""
        if not isinstance(capacity, (int)):
            raise PropertyError(constants.POINT.CAPACITY.value,
                                constants.INTEGER_PROPERTY)
        if capacity < 0:
            raise PropertyError(constants.POINT.CAPACITY.value,
                                constants.GREATER_ZERO_PROPERTY)
        self._demand_or_capacity = capacity
        self._capacity = capacity

    # a getter function of demand_or_capacity
    @property
    def demand_or_capacity(self):
        """getter function of demand_or_capacity"""
        return self._demand_or_capacity

    @demand_or_capacity.setter
    def demand_or_capacity(self, demand_or_capacity):
        """setter function of demand_or_capacity"""
        if not isinstance(demand_or_capacity, (int)):
            raise PropertyError(constants.POINT.DEMAND_OR_CAPACITY.value,
                                constants.INTEGER_PROPERTY)
        if demand_or_capacity < 0:
            raise PropertyError(constants.POINT.DEMAND_OR_CAPACITY.value,
                                constants.GREATER_ZERO_PROPERTY)
        self._demand_or_capacity = demand_or_capacity

    @property
    def incompatible_vehicles(self):
        """getter function of incompatible_vehicles"""
        return self._incompatible_vehicles

    @incompatible_vehicles.setter
    def incompatible_vehicles(self, incompatible_vehicles):
        """setter function of incompatible_vehicles"""
        if not isinstance(incompatible_vehicles, (list)):
            raise PropertyError(constants.POINT.INCOMPATIBLE_VEHICLES.value,
                                constants.LIST_INTEGER_PROPERTY)
        if len(incompatible_vehicles) > 0:
            if not all(isinstance(x, int) for x in incompatible_vehicles):
                raise PropertyError(
                    constants.POINT.INCOMPATIBLE_VEHICLES.value,
                    constants.LIST_INTEGER_PROPERTY)
        self._incompatible_vehicles = incompatible_vehicles

    def get_point(self, debug=False):
        """Get all components of a Point which are
         different of default value"""
        point = {}
        point["id"] = self.id
        if self.name != str() or debug:
            point[constants.POINT.NAME.value] = self.name
        if self.id_customer != 0 or debug:
            point[constants.POINT.ID_CUSTOMER.value] = self.id_customer
        if self.service_time != 0 or debug:
            point[constants.POINT.SERVICE_TIME.value] = self.service_time
        if self.tw_begin != 0 or debug:
            point[constants.POINT.TIME_WINDOWS_BEGIN.value] = self.tw_begin
        if self.tw_end != 0 or debug:
            point[constants.POINT.TIME_WINDOWS_END.value] = self.tw_end
        if self.penalty_or_cost != 0 or debug:
            point[constants.POINT.PENALTY_OR_COST.value] = self.penalty_or_cost
        if self.demand_or_capacity != 0 or debug:
            point[constants.POINT.DEMAND_OR_CAPACITY
                  .value] = self.demand_or_capacity
        if self.incompatible_vehicles != [] or debug:
            point[constants.POINT.INCOMPATIBLE_VEHICLES
                  .value] = self.incompatible_vehicles
        return point

    def __repr__(self):
        return repr(self.get_point())


class Customer(Point):
    """Define a point customer of graph.

    Additional informations:
        id_customer(int): must be inferior or equal to 1022
        penalty(float): represents the penalty of non visited customer
        tw_begin(float): time window begin
        tw_end(float): time window end
        demand: must be an integer
    """

    def __init__(
            self,
            id,
            name=str(),
            id_customer=0,
            penalty=0.0,
            service_time=0,
            tw_begin=0,
            tw_end=0,
            demand=0,
            incompatible_vehicles=[]):
        super().__init__(
            id,
            name,
            id_customer,
            penalty,
            service_time,
            tw_begin,
            tw_end,
            demand,
            incompatible_vehicles)


class Depot(Point):
    """Define a point depot of graph.

    Additional informations:
        capacity: must be an integer
    """

    def __init__(
            self,
            id,
            name=str(),
            cost=0,
            service_time=0,
            tw_begin=0,
            tw_end=0,
            capacity=0,
            incompatible_vehicles=[]):
        super().__init__(id, name, -1, cost, service_time, tw_begin, tw_end,
                         capacity, incompatible_vehicles)


class Link:
    """Define a link of graph.

    Additional informations:
        is_directed ---- it's equal to True if we cannot return at
        start point with the same time and distance
    """

    def __init__(self, name=str(), is_directed=False, start_point_id=0,
                 end_point_id=0, distance=0.0, time=0.0, fixed_cost=0.0):
        self.name = name
        self.is_directed = is_directed
        self.start_point_id = start_point_id
        self.end_point_id = end_point_id
        self.distance = distance
        self.time = time
        self.fixed_cost = fixed_cost

    @property
    def name(self):
        """getter function of name"""
        return self._name

    @name.setter
    def name(self, name):
        """setter function of name"""
        if not isinstance(name, (str)):
            raise PropertyError(constants.LINK.NAME.value,
                                constants.STRING_PROPERTY)
        self._name = name

    @property
    def is_directed(self):
        """getter function of is_directed"""
        return self._is_directed

    @is_directed.setter
    def is_directed(self, is_directed):
        """setter function of is_directed"""
        if not isinstance(is_directed, (bool)):
            raise PropertyError(constants.LINK.NAME.value,
                                constants.BOOLEAN_PROPERTY)
        self._is_directed = is_directed

    @property
    def start_point_id(self):
        """getter function of start_point_id"""
        return self._start_point_id

    @start_point_id.setter
    def start_point_id(self, start_point_id):
        """setter function of start_point_id"""
        if not isinstance(start_point_id, (int)):
            raise PropertyError(constants.LINK.START_POINT_ID.value,
                                constants.INTEGER_PROPERTY)
        if start_point_id < 0:
            raise PropertyError(constants.LINK.START_POINT_ID.value,
                                constants.GREATER_ZERO_PROPERTY)
        self._start_point_id = start_point_id

    @property
    def end_point_id(self):
        """getter function of end_point_id"""
        return self._end_point_id

    @end_point_id.setter
    def end_point_id(self, end_point_id):
        """setter function of end_point_id"""
        if not isinstance(end_point_id, (int)):
            raise PropertyError(constants.LINK.END_POINT_ID.value,
                                constants.INTEGER_PROPERTY)
        if end_point_id < 0:
            raise PropertyError(constants.LINK.END_POINT_ID.value,
                                constants.GREATER_ZERO_PROPERTY)
        self._end_point_id = end_point_id

    @property
    def distance(self):
        """getter function of distance"""
        return self._distance

    @distance.setter
    def distance(self, distance):
        """setter function of distance"""
        if not isinstance(distance, (int, float)):
            raise PropertyError(constants.LINK.DISTANCE.value,
                                constants.NUMBER_PROPERTY)
        if distance < 0:
            raise PropertyError(constants.LINK.DISTANCE.value,
                                constants.GREATER_ZERO_PROPERTY)
        self._distance = distance

    @property
    def time(self):
        """getter function of time"""
        return self._time

    @time.setter
    def time(self, time):
        """setter function of time"""
        if not isinstance(time, (int, float)):
            raise PropertyError(constants.LINK.TIME.value,
                                constants.NUMBER_PROPERTY)
        if time < 0:
            raise PropertyError(constants.LINK.TIME.value,
                                constants.GREATER_ZERO_PROPERTY)
        self._time = time

    @property
    def fixed_cost(self):
        """getter function of fixed_cost"""
        return self._fixed_cost

    @fixed_cost.setter
    def fixed_cost(self, fixed_cost):
        """setter function of fixed_cost"""
        if not isinstance(fixed_cost, (int, float)):
            raise PropertyError(constants.LINK.FIXED_COST.value,
                                constants.NUMBER_PROPERTY)
        self._fixed_cost = fixed_cost

    def get_link(self, debug=False):
        """Get all components of a Link which are different of
        default value"""
        link = {}
        link[constants.LINK.START_POINT_ID.value] = self._start_point_id
        link[constants.LINK.END_POINT_ID.value] = self._end_point_id
        if self._name != str() or debug:
            link[constants.LINK.NAME.value] = self._name
        if self._is_directed or debug:
            link[constants.LINK.IS_DIRECTED.value] = self._is_directed
        if self._distance != 0 or debug:
            link[constants.LINK.DISTANCE.value] = self._distance
        if self._time != 0 or debug:
            link[constants.LINK.TIME.value] = self._time
        if self._fixed_cost != 0 or debug:
            link[constants.LINK.FIXED_COST.value] = self._fixed_cost
        return link

    def __repr__(self):
        return repr(self.get_link())


class Parameters:
    """Define a point of graph(customer or depot).

    Additional informations:
        time_limit(int) ---- It can represent the limit time of resolution
        upper_bound(float) --indicates the cost we want to reach
        config_file(str) -- indicates the path of the config file for
                            more advanced settings
        solver_name(str) -- indicates the solver used during the resolution,
                            we can choose "CLP" or "CPLEX" solver
        print_level(int) -- indicates the level of print from Bapcod
                            during the resolution, we can choose (-2,-1,0)
        action(str) -- indicates if we want to solve the problem ("solve")
                     or enumerate all feasible routes("enumAllFeasibleRoutes")
    """

    def __init__(
            self,
            time_limit=300,
            upper_bound=1000000,
            heuristic_used=False,
            time_limit_heuristic=20,
            config_file=str(),
            solver_name="CLP",
            print_level=-1,
            action="solve",
            cplex_path=""):
        self.time_limit = time_limit
        self.upper_bound = upper_bound
        self.heuristic_used = heuristic_used
        self.time_limit_heuristic = time_limit_heuristic
        self.config_file = config_file
        self.solver_name = solver_name
        self.print_level = print_level
        self.action = action
        self.cplex_path = cplex_path

    @property
    def time_limit(self):
        """getter function of time_limit"""
        return self._time_limit

    @time_limit.setter
    def time_limit(self, time_limit):
        """setter function of time_limit"""
        if not isinstance(time_limit, (int, float)):
            raise PropertyError(constants.PARAMETERS.TIME_LIMIT.value,
                                constants.NUMBER_PROPERTY)
        if time_limit < 0:
            raise PropertyError(constants.PARAMETERS.TIME_LIMIT.value,
                                constants.GREATER_ZERO_PROPERTY)
        self._time_limit = time_limit

    @property
    def upper_bound(self):
        """getter function of upper_bound"""
        return self._upper_bound

    @upper_bound.setter
    def upper_bound(self, upper_bound):
        """setter function of upper_bound"""
        if not isinstance(upper_bound, (int, float)):
            raise PropertyError(constants.PARAMETERS.UPPER_BOUND.value,
                                constants.NUMBER_PROPERTY)
        self._upper_bound = upper_bound

    # a getter function of heuristic_used

    @property
    def heuristic_used(self):
        """getter function of heuristic_used"""
        return self._heuristic_used

    @heuristic_used.setter
    def heuristic_used(self, heuristic_used):
        """setter function of heuristic_used"""
        if not isinstance(heuristic_used, (bool)):
            raise PropertyError(constants.PARAMETERS.
                                HEURISTIC_USED.value,
                                constants.BOOLEAN_PROPERTY)
        self._heuristic_used = heuristic_used

    @property
    def time_limit_heuristic(self):
        """getter function of time_limit_heuristic"""
        return self._time_limit_heuristic

    @time_limit_heuristic.setter
    def time_limit_heuristic(self, time_limit_heuristic):
        """setter function of time_limit_heuristic"""
        if not isinstance(time_limit_heuristic, (int, float)):
            raise PropertyError(constants.PARAMETERS.
                                TIME_LIMIT_HEURISTIC.value,
                                constants.NUMBER_PROPERTY)
        if time_limit_heuristic < 0:
            raise PropertyError(constants.PARAMETERS.
                                TIME_LIMIT_HEURISTIC.value,
                                constants.GREATER_ZERO_PROPERTY)
        self._time_limit_heuristic = time_limit_heuristic

    @property
    def config_file(self):
        """getter function of config_file"""
        return self._config_file

    @config_file.setter
    def config_file(self, config_file):
        """setter function of config_file"""
        if not isinstance(config_file, (str)):
            raise PropertyError(constants.PARAMETERS.CONFIG_FILE.value,
                                constants.STRING_PROPERTY)
        self._config_file = config_file

    @property
    def solver_name(self):
        """getter function of solver_name"""
        return self._solver_name

    @solver_name.setter
    def solver_name(self, solver_name):
        """setter function of solver_name"""
        if not isinstance(solver_name, (str)):
            raise PropertyError(constants.PARAMETERS.SOLVER_NAME.value,
                                constants.STRING_PROPERTY)
        if solver_name not in constants.SOLVERS:
            raise PropertyError(constants.PARAMETERS.SOLVER_NAME.value,
                                constants.ENUM_STR_PROPERTY,
                                str(constants.SOLVERS))
        self._solver_name = solver_name

    @property
    def print_level(self):
        """getter function of print_level"""
        return self._print_level

    @print_level.setter
    def print_level(self, print_level):
        """setter function of print_level"""
        if not isinstance(print_level, (int)):
            raise PropertyError(constants.PARAMETERS.PRINT_LEVEL.value,
                                constants.NUMBER_PROPERTY)
        if print_level not in constants.PRINT_LEVEL_LIST:
            raise PropertyError(constants.PARAMETERS.PRINT_LEVEL.value,
                                constants.ENUM_INT_PROPERTY,
                                str(constants.PRINT_LEVEL_LIST))
        self._print_level = print_level

    @property
    def action(self):
        """getter function of action"""
        return self._action

    @action.setter
    def action(self, action):
        """setter function of action"""
        if not isinstance(action, (str)):
            raise PropertyError(constants.PARAMETERS.ACTION.value,
                                constants.STRING_PROPERTY)
        if action not in constants.ACTIONS:
            raise Exception(constants.PARAMETERS.ACTION.value,
                            constants.ENUM_STR_PROPERTY,
                            str(constants.ACTIONS))
        self._action = action

    @property
    def cplex_path(self):
        """getter function of cplex_path"""
        return self._cplex_path

    @cplex_path.setter
    def cplex_path(self, cplex_path):
        """setter function of cplex_path"""
        if not isinstance(cplex_path, (str)):
            raise PropertyError(constants.PARAMETERS.CPLEX_PATH.value,
                                constants.STRING_PROPERTY)
        self._cplex_path = cplex_path

    def get_parameters(self, debug=False):
        """Get all parameters which are different of
        default value"""
        param = {}
        param[constants.PARAMETERS.TIME_LIMIT.value] = self.time_limit
        param[constants.PARAMETERS.ACTION.value] = self.action
        if self.upper_bound != 1000000 or debug:
            param[constants.PARAMETERS.
                  UPPER_BOUND.value] = self.upper_bound
        if self.heuristic_used or debug:
            param[constants.PARAMETERS.
                  HEURISTIC_USED.value] = self.heuristic_used
        if self.time_limit_heuristic != 20 or debug:
            param[constants.PARAMETERS.
                  TIME_LIMIT_HEURISTIC.value] = self.time_limit_heuristic
        if self.config_file != str() or debug:
            param[constants.PARAMETERS.CONFIG_FILE.value] = self.config_file
        if self.solver_name != "CLP" or debug:
            param[constants.PARAMETERS.SOLVER_NAME.value] = self.solver_name
        if self.print_level != -1 or debug:
            param[constants.PARAMETERS.PRINT_LEVEL.value] = self.print_level
        return param

    def __repr__(self):
        return repr(self.get_parameters())


class Statistics:
    """Define a statistics from solution

    Attributes
    ----------
    json_input : str
        a formatted string to print statistics in json format
    solution_time : float
        the time computed by the resolution of problem
    best_lb : float
        the best lower bound find during the resolution
    root_lb : float
        the root lower bound find during the resolution
    root_time : float
        TODO
    nb_branch_and_bound_nodes : float
        the number of branch and bound nodes from tree structure.

    """

    def __init__(self, json_input=str()):
        if json_input != str():
            self.__json_input = json_input
            self.__solution_time = json_input[constants.STATISTICS.
                                              SOLUTION_TIME.value]
            self.__solution_value = json_input[constants.STATISTICS.
                                               SOLUTION_VALUE.value]
            self.__best_lb = json_input[constants.STATISTICS.
                                        BEST_LOWER_BOUND.value]
            self.__root_lb = json_input[constants.STATISTICS.
                                        ROOT_LOWER_BOUND.value]
            self.__root_time = json_input[constants.STATISTICS.
                                          ROOT_TIME.value]
            self.__nb_branch_and_bound_nodes = json_input[
                constants.STATISTICS. NB_BRANCH_AND_BOUND_NODES. value]

    @property
    def nb_branch_and_bound_nodes(self):
        """getter function of nb_branch_and_bound_nodes"""
        return self.__nb_branch_and_bound_nodes

    @property
    def root_time(self):
        """getter function of root_time"""
        return self.__root_time

    @property
    def root_lb(self):
        """getter function of root_lb"""
        return self.__root_lb

    @property
    def best_lb(self):
        """getter function of best_lb"""
        return self.__best_lb

    @property
    def solution_value(self):
        """getter function of solution_value"""
        return self.__solution_value

    @property
    def solution_time(self):
        """getter function of solution_time"""
        return self.__solution_time

    def __repr__(self):
        return repr(self.__json_input)


class Route:
    """Define a route from solution

    Attributes
    ----------
    route : str
        a formatted string to print out what the animal says
    vehicle_type_id : int
        the name of the animal
    route_cost : list(float)
        the sound that the animal makes
    point_ids : list(int)
        the number of legs the animal has (default 4)
    point_names : list(str)
        the number of legs the animal has (default 4)
    cap_consumption : list(float)
        the number of legs the animal has (default 4)
    time_consumption : list(float)
        the number of legs the animal has (default 4)
    incoming_arc_names : list(str)
        the number of legs the animal has (default 4)
    """

    def __init__(self, json_input):
        self.__route = json_input
        self.__vehicle_type_id = json_input[constants.ROUTE.VEHICLE_TYPE_ID.value]
        self.__route_cost = json_input[constants.ROUTE.ROUTE_COST.value]
        self.__point_ids = []
        self.__point_names = []
        self.__cap_consumption = []
        self.__time_consumption = []
        self.__incoming_arc_names = []
        for point in json_input[constants.ROUTE.VISITED_POINTS.value]:
            self.__point_ids.append(point[constants.ROUTE.POINT_ID.value])
            self.__point_names.append(point[constants.ROUTE.POINT_NAME.value])
            self.__cap_consumption.append(point[constants.ROUTE.LOAD.value])
            self.__time_consumption.append(point[constants.ROUTE.TIME.value])
            self.__incoming_arc_names.append(point[
                constants.ROUTE.INCOMING_ARC_NAME.value])

    @property
    def route(self):
        """getter function of route"""
        return self.__route

    @property
    def vehicle_type_id(self):
        """getter function of vehicle_type_id"""
        return self.__vehicle_type_id

    @property
    def route_cost(self):
        """getter function of route_cost"""
        return self.__route_cost

    @property
    def point_ids(self):
        """getter function of point_ids"""
        return self.__point_ids

    @property
    def point_names(self):
        """getter function of point_names"""
        return self.__point_names

    @property
    def cap_consumption(self):
        """getter function of cap_consumption"""
        return self.__cap_consumption

    @property
    def time_consumption(self):
        """getter function of time_consumption"""
        return self.__time_consumption

    @property
    def incoming_arc_names(self):
        """getter function of incoming_arc_names"""
        return self.__incoming_arc_names

    def __repr__(self):
        return repr(self.__route)


class Solution:
    """Define a statistics from solution

    Attributes
    ----------
    solution : str
        a formatted string to print statistics in json format
    routes : float
        the time computed by the resolution of problem
    statistics : float
        the best lower bound find during the resolution
    status : int
        the root lower bound find during the resolution
    message : float
        TODO
    nb_branch_and_bound_nodes : float
        the number of branch and bound nodes from tree structure.

    """

    def __init__(self, json_input=str()):
        self.json = {}
        self.routes = []
        self.statistics = Statistics()
        self.status = 0
        self.message = str()
        if json_input != str():
            self.json = json.loads(json_input)
            self.status = self.json["Status"]["code"]
            self.message = self.json["Status"]["message"]
            if self.status > 2 and self.status < 6:
                self.statistics = Statistics(self.json["Statistics"])
            if (self.status > 2 and self.status < 6) or self.status == 8:
                if len(self.json["Solution"]) > 0:
                    for route in self.json["Solution"]:
                        self.routes.append(Route(route))

    def __str__(self):
        return json.dumps(self.json, indent=1)

    def __repr__(self):
        return repr(self.__str__())

    def export(self, name="instance"):
        """Export solution for sharing or debugging model,
        we can specify the name of file"""
        with open(name + ".json", "w") as outfile:
            outfile.write(json.dumps(self.json, indent=1))


class CreateModel:
    """Define a routing model.

    Additional informations:
        json(dict) -- contains the model in json format
        vehicle_types(dict) -- contains the set of vehicle types
        points(dict) -- contains the set of customers and depots
        links(dict) -- contains the set of links
        output(str) -- defines the json output after solving the problem
    """

    def __init__(self):
        self.__json = {}
        self.vehicle_types = VehicleTypesDict()
        self.points = PointsDict()
        self.links = LinksDict()
        self.parameters = Parameters()
        self.__output = str()
        self.solution = Solution()

    @property
    def vehicle_types(self):
        """getter function of vehicle_types"""
        return self._vehicle_types

    @vehicle_types.setter
    def vehicle_types(self, vehicle_types):
        """setter function of vehicle_types"""
        if not isinstance(vehicle_types, (VehicleTypesDict)):
            raise PropertyError(constants.JSON_OBJECT.VEHICLE_TYPES.value,
                                constants.LIST_INTEGER_PROPERTY)
        self._vehicle_types = vehicle_types

    @property
    def points(self):
        """getter function of points"""
        return self._points

    # a setter function of points
    @points.setter
    def points(self, points):
        """setter function of points"""
        if not isinstance(points, (PointsDict)):
            raise PropertyError(constants.JSON_OBJECT.POINTS.value, 0)
        self._points = points

    @property
    def links(self):
        """getter function of links"""
        return self._links

    # a setter function of links
    @links.setter
    def links(self, links):
        """setter function of links"""
        if not isinstance(links, (LinksDict)):
            raise PropertyError(constants.JSON_OBJECT.LINKS.value, 0)
        self._links = links

    @property
    def parameters(self):
        """getter function of parameters"""
        return self._parameters

    # a setter function of parameters
    @parameters.setter
    def parameters(self, parameters):
        """setter function of parameters"""
        if not isinstance(parameters, (Parameters)):
            raise PropertyError(constants.JSON_OBJECT.PARAMETERS.value, 0)
        self._parameters = parameters

    def add_vehicle_type(
            self,
            id: int,
            start_point_id: int,
            end_point_id: int,
            name=str(),
            capacity=0,
            fixed_cost=0.0,
            var_cost_dist=0.0,
            var_cost_time=0.0,
            max_number=1,
            tw_begin=0.0,
            tw_end=0.0):
        """Add VehicleType in dictionary self.vehicle_types"""
        if id in self.vehicle_types:
            raise ModelError(constants.ADD_VEHICLE_TYPE_ERROR)
        self.vehicle_types[id] = VehicleType(
            id,
            start_point_id,
            end_point_id,
            name,
            capacity,
            fixed_cost,
            var_cost_dist,
            var_cost_time,
            max_number,
            tw_begin,
            tw_end)

    def delete_vehicle_type(self, id: int):
        """ Delete a vehicle type by giving his id """
        if id not in self.vehicle_types:
            raise ModelError(constants.DEL_VEHICLE_TYPE_ERROR)
        del self.vehicle_types[id]

    def add_link(
            self,
            name=str(),
            is_directed=False,
            start_point_id=0,
            end_point_id=0,
            distance=0.0,
            time=0.0,
            fixed_cost=0.0):
        """Add Link in dictionary self.links"""
        if name in self.links:
            raise ModelError(constants.ADD_LINK_ERROR)
        self.links[name] = Link(
            name,
            is_directed,
            start_point_id,
            end_point_id,
            distance,
            time,
            fixed_cost)

    def delete_Link(self, id: int):
        """ Delete a link by giving his id """
        if id not in self.links:
            raise ModelError(constants.DEL_LINK_ERROR)
        del self.links[id]

    def add_point(
            self,
            id,
            name=str(),
            id_customer=0,
            service_time=0.0,
            penalty_or_cost=0.0,
            tw_begin=0.0,
            tw_end=0.0,
            demand_or_capacity=0,
            incompatible_vehicles=[]):
        """Add Point in dictionary self.points, if we want to add Depot
           id_customer must be equal to 0 otherwise it cannot be superior
           to 1022 for a Customer"""
        if id in self.points:
            raise ModelError(constants.ADD_POINT_ERROR)
        self.points[id] = Point(
            id,
            name,
            id_customer,
            penalty_or_cost,
            service_time,
            tw_begin,
            tw_end,
            demand_or_capacity,
            incompatible_vehicles)

    def add_depot(
            self,
            id,
            name=str(),
            service_time=0.0,
            cost=0.0,
            tw_begin=0.0,
            tw_end=0.0,
            capacity=0,
            incompatible_vehicles=[]):
        """Add Depot in dictionary self.points"""
        if id in self.points:
            raise ModelError(constants.ADD_POINT_ERROR)
        self.add_point(id=id, name=name, id_customer=0,
                       service_time=service_time, penalty_or_cost=cost,
                       tw_begin=tw_begin, tw_end=tw_end,
                       demand_or_capacity=capacity,
                       incompatible_vehicles=incompatible_vehicles)

    def delete_depot(self, id: int):
        """ Delete a depot by giving his id """
        self.delete_customer(id)

    def add_customer(
            self,
            id,
            name=str(),
            id_customer=0,
            service_time=0.0,
            penalty=0.0,
            tw_begin=0.0,
            tw_end=0.0,
            demand=0,
            incompatible_vehicles=[]):
        """Add Customer in dictionary self.points ,
           id must be between 0 and 1022 and all id must be different"""
        if id in self.points:
            raise ModelError(constants.ADD_POINT_ERROR)
        id_cust = id_customer
        if id_cust == 0:
            id_cust = id
        self.add_point(id=id, name=name, id_customer=id_cust,
                       service_time=service_time, penalty_or_cost=penalty,
                       tw_begin=tw_begin, tw_end=tw_end,
                       demand_or_capacity=demand,
                       incompatible_vehicles=incompatible_vehicles)

    def delete_customer(self, id: int):
        """ Delete a customer by giving his id """
        if id not in self.points:
            raise ModelError(constants.DEL_POINT_ERROR)
        del self.points[id]

    def set_parameters(self, time_limit=300, upper_bound=1000000,
                       heuristic_used=False, time_limit_heuristic=20,
                       config_file=str(), solver_name="CLP",
                       print_level=-1, action="solve", cplex_path=""):
        """Set parameters of model. For more advanced parameters please
       indicates a configuration file on config_file variable.
       solver_name : [CLP,CPLEX]
       action : [solve,enumAllFeasibleRoutes],
       print_level = [-2,-1,0,1,2]"""

        self.parameters = Parameters(
            time_limit,
            upper_bound,
            heuristic_used,
            time_limit_heuristic,
            config_file,
            solver_name,
            print_level,
            action,
            cplex_path)

    def set_json(self):
        """Set model in json format with all properties of model"""
        self.__json = json.dumps({constants.JSON_OBJECT.POINTS.value:
                                  list(self.points.values()),
                                  constants.JSON_OBJECT.
                                  VEHICLE_TYPES.value:
                                  list(self.vehicle_types.values()),
                                  constants.JSON_OBJECT.LINKS.value:
                                  list(self.links.values()),
                                  constants.JSON_OBJECT.
                                  PARAMETERS.value:
                                  self.parameters.get_parameters()},
                                 indent=1)

    def __str__(self):
        self.set_json()
        return self.__json

    def __repr__(self):
        return self.__str__()

    def export(self, name="instance"):
        """Export model for debugging model,
           we can specify the name of file"""
        model = json.dumps({constants.JSON_OBJECT.POINTS.
                            value: list(self.points.values(True)),
                            constants.JSON_OBJECT.VEHICLE_TYPES.value:
                           list(self.vehicle_types.values(True)),
                            constants.JSON_OBJECT.LINKS.value:
                           list(self.links.values(True)),
                            constants.JSON_OBJECT.PARAMETERS.value:
                           self.parameters.get_parameters(True)},
                           indent=1)
        # Writing to sample.json
        with open(name + ".json", "w") as outfile:
            outfile.write(model)

    def solve(self):
        """Solve the routing problem by using the shared library
           bapcod and fill the solution.

        Additional informations:
            VRPSolverEasy is compatible with Windows 64x,  Linux and macOS only
        """
        _lib_bapcod = None
        _lib_name = None
        _lib_candidates = []

        new_lib = os.path.realpath(__file__ + "/../../lib/Dependencies/")

        if platform.system() == constants.WINDOWS_PLATFORM:
            _lib_name = constants.LIBRARY_WINDOWS
        elif platform.system() == constants.LINUX_PLATFORM:
            _lib_name = constants.LIBRARY_LINUX
            if new_lib not in os.environ[constants.PATH_SYSTEM[platform.system(
            )]]:
                os.environ[constants.PATH_SYSTEM[platform.system()]
                           ] += ':' + new_lib
                try:
                    os.execv(sys.argv[0], sys.argv)
                except Exception:
                    print('Failed re-exec')
                    sys.exit(1)
        elif platform.system() == constants.MAC_PLATFORM:
            _lib_name = constants.LIBRARY_MAC
            _c.cdll.LoadLibrary(new_lib + "/libCoinUtils.0.dylib")
            _c.cdll.LoadLibrary(new_lib + "/libClp.0.dylib")
            _c.cdll.LoadLibrary(new_lib + "/libOsi.0.dylib")
            _c.cdll.LoadLibrary(new_lib + "/libOsiClp.0.dylib")

        else:
            raise ModelError(constants.PLATFORM_ERROR)

        # Load solver
        if self.parameters.cplex_path != str():
            try:
                _c.cdll.LoadLibrary(
                    os.path.realpath(
                        self.parameters.cplex_path))
            except BaseException:
                raise ModelError(constants.BAPCOD_ERROR)

        # Try three different locations to load the native library:
        # 1. The current folder
        # 2. The platform folder (lib/Windows for example)
        # 3. The system folders (delegates the loading behavior to the system)

        _lib_candidates.append(os.path.join(os.path.dirname
                                            (os.path.realpath(__file__)),
                                            _lib_name))

        _lib_candidates.append(os.path.join(
            os.path.join(os.path.realpath(__file__ + "/../../lib/"),
                         platform.system()), _lib_name))

        _lib_candidates.append(_lib_name)

        _loaded_library = None
        for candidate in _lib_candidates:
            try:
                # Python 3.8 has changed the behavior of CDLL on Windows.
                if hasattr(os, 'add_dll_directory'):
                    _lib_bapcod = _c.CDLL(candidate, winmode=0)
                else:
                    _lib_bapcod = _c.CDLL(candidate)
                _loaded_library = candidate
                break
            except BaseException:
                pass

        if _loaded_library is None:
            raise ModelError(constants.LOAD_LIB_ERROR)
        self.set_json()
        input = _c.c_char_p(self.__json.encode('UTF-8'))
        solve = _lib_bapcod.solveModel
        solve.argtypes = [_c.c_char_p]
        solve.restype = _c.POINTER(_c.c_char_p)
        free_memory = _lib_bapcod.freeMemory
        free_memory.argtypes = [_c.POINTER(_c.c_char_p)]
        free_memory.restype = _c.c_void_p

        try:
            output = solve(input)
            self.__output = (_c.c_char_p.from_buffer(output)).value
            self.solution = Solution(self.__output)
            free_memory(output)
        except BaseException:
            raise ModelError(constants.BAPCOD_ERROR)
