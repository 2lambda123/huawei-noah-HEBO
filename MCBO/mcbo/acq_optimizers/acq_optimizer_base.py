# Copyright (C) 2020. Huawei Technologies Co., Ltd. All rights reserved.

# This program is free software; you can redistribute it and/or modify it under
# the terms of the MIT license.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the MIT License for more details.

from abc import ABC
from abc import abstractmethod
from typing import Optional, Callable, Dict, Union, List

import numpy as np
import pandas as pd
import torch

from mcbo.acq_funcs import AcqBase
from mcbo.models import ModelBase
from mcbo.search_space import SearchSpace
from mcbo.trust_region import TrManagerBase
from mcbo.utils.constraints_utils import input_eval_from_origx, input_eval_from_transfx, \
    sample_input_valid_points
from mcbo.utils.data_buffer import DataBuffer


class AcqOptimizerBase(ABC):
    color_1: str

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @staticmethod
    @abstractmethod
    def get_color_1():
        raise NotImplementedError()

    def __init__(self,
                 search_space: SearchSpace,
                 dtype: torch.dtype,
                 input_constraints: Optional[List[Callable[[Dict], bool]]],
                 **kwargs
                 ):
        """
        Args:
            search_space: optimization search space
            dtype: tensor type
            input_constraints: list of funcs taking a point as input and outputting whether the point
                                       is valid or not
        """
        self.search_space = search_space
        self.dtype = dtype
        self.input_constraints = input_constraints
        self.kwargs = kwargs

    @abstractmethod
    def optimize(self,
                 x: torch.Tensor,
                 n_suggestions: int,
                 x_observed: torch.Tensor,
                 model: ModelBase,
                 acq_func: AcqBase,
                 acq_evaluate_kwargs: dict,
                 tr_manager: Optional[TrManagerBase],
                 **kwargs
                 ) -> torch.Tensor:
        """
        Function used to optimize the acquisition function. Should return a 2D tensor with shape
        (n_suggestions, n_dims), where n_dims is the dimensionality of x.

        If an optimizer does not support return batches of data, this can be handled by imposing with "assert
        n_suggestions == 1"


        :param x:
        :param n_suggestions:
        :param x_observed:
        :param model:
        :param acq_func:
        :param acq_evaluate_kwargs:
        :param tr_manager: a trust region within which to perform the optimization
        :param kwargs:
        :return:
        """
        pass

    def post_observe_method(self, x: torch.Tensor, y: torch.Tensor, data_buffer: DataBuffer, n_init: int, **kwargs):
        """
        Function called at the end of observe method. Can be used to update the internal state of the acquisition
        optimizer based on the observed x and y values. Use cases may include updating the weights of a multi-armed
        bandit based on previously suggested nominal variables and the observed black-box function value.

        :param x:
        :param y:
        :param data_buffer:
        :param n_init:
        :param kwargs:
        :return:
        """

        pass

    def input_eval_from_transfx(self, transf_x: torch.Tensor) -> np.ndarray:
        """
        Evaluate the boolean constraint function on a set of transformed inputs

        Return:
            Array of `number of input points \times number of input constraint` booleans
                specifying at index `(i, j)` if input point `i` is valid regarding constraint function `j`        """
        return input_eval_from_transfx(transf_x=transf_x, search_space=self.search_space,
                                               input_constraints=self.input_constraints)

    def input_eval_from_origx(self, x: Union[pd.DataFrame, Dict]) -> np.ndarray:
        """
        Evaluate the boolean constraint function on a set of non-transformed inputs

        Args:
            x: can contain several input points as a Dataframe, can also be given as a single Dict {var_name: var_value}

        Return:
            Array of `number of input points \times number of input constraint` booleans
                specifying at index `(i, j)` if input point `i` is valid regarding constraint function `j`
        """
        return input_eval_from_origx(x=x, input_constraints=self.input_constraints)

    def sample_input_valid_points(self, n_points: int, point_sampler: Callable[[int], pd.DataFrame],
                                          max_trials: int = 100) -> pd.DataFrame:
        """ Get valid points in original space

        Args:
            n_points: number of points desired
            point_sampler: function that can be used to sample points
            max_trials: max number of trials
        """
        return sample_input_valid_points(
            n_points=n_points,
            point_sampler=point_sampler,
            input_constraints=self.input_constraints
        )
