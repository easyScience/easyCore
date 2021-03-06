__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import inspect
from typing import List

from easyCore.Fitting.fitting_template import noneType, Union, Callable, FittingTemplate, np, FitResults

# Import bumps specific objects
from bumps.names import Curve, FitProblem
from bumps.parameter import Parameter as bumpsParameter
from bumps.fitters import fit as bumps_fit


class bumps(FittingTemplate):  # noqa: S101
    """
    This is a wrapper to bumps: https://bumps.readthedocs.io/
    It allows for the bumps fitting engine to use parameters declared in an `easyCore.Objects.Base.BaseObj`.
    """

    property_type = bumpsParameter
    name = 'bumps'

    def __init__(self, obj, fit_function: Callable):
        """
        Initialize the fitting engine with a `BaseObj` and an arbitrary fitting function.

        :param obj: Object containing elements of the `Parameter` class
        :type obj: BaseObj
        :param fit_function: function that when called returns y values. 'x' must be the first
                            and only positional argument. Additional values can be supplied by
                            keyword/value pairs
        :type fit_function: Callable
        """
        super().__init__(obj, fit_function)
        self._cached_pars_order = ()

    def make_model(self, pars: Union[noneType, List[bumpsParameter]] = None) -> Callable:
        """
        Generate a bumps model from the supplied `fit_function` and parameters in the base object.
        Note that this makes a callable as it needs to be initialized with *x*, *y*, *weights*

        :return: Callable to make a bumps Curve model
        :rtype: Callable
        """
        fit_func = self._generate_fit_function()

        def outer(obj):
            def make_func(x, y, weights):
                par = {}
                if not pars:
                    for name, item in obj._cached_pars.items():
                        par[name] = obj.convert_to_par_object(item)
                else:
                    for item in pars:
                        par[item.name] = obj.convert_to_par_object(item)
                return Curve(fit_func, x, y, weights, **par)

            return make_func

        return outer(self)

    def _generate_fit_function(self) -> Callable:
        """
        Using the user supplied `fit_function`, wrap it in such a way we can update `Parameter` on
        iterations.

        :return: a fit function which is compatible with bumps models
        :rtype: Callable
        """
        # Original fit function
        func = self._original_fit_function
        # Get a list of `Parameters`
        for parameter in self._object.get_parameters():
            self._cached_pars[parameter.name] = parameter

        # Make a new fit function
        def fit_function(x: np.ndarray, **kwargs):
            """
            Wrapped fit function which now has a bumps compatible form

            :param x: array of data points to be calculated
            :type x: np.ndarray
            :param kwargs: key word arguments
            :return: points calculated at `x`
            :rtype: np.ndarray
            """
            # Update the `Parameter` values and the callback if needed
            for name, value in kwargs.items():
                if name in self._cached_pars.keys():
                    self._cached_pars[name].value = value
                    update_fun = self._cached_pars[name]._callback.fset
                    if update_fun:
                        update_fun(value)
            # TODO Pre processing here
            return_data = func(x)
            # TODO Loading or manipulating data here
            return return_data

        # Fake the function signature.
        # This is done as lmfit wants the function to be in the form:
        # f = (x, a=1, b=2)...
        # Where we need to be generic. Note that this won't hold for much outside of this scope.

        self._cached_pars_order = tuple(self._cached_pars.keys())
        params = [inspect.Parameter('x',
                                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                    annotation=inspect._empty), *[inspect.Parameter(name,
                                                                                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                                                                    annotation=inspect._empty,
                                                                                    default=self._cached_pars[
                                                                                        name].raw_value)
                                                                  for name in self._cached_pars_order]]
        # Sign the function
        fit_function.__signature__ = inspect.Signature(params)
        self._fit_function = fit_function
        return fit_function

    def fit(self, x: np.ndarray, y: np.ndarray, weights: Union[np.ndarray, noneType] = None,
            model=None, parameters=None, xtol=1e-6, ftol=1e-8, **kwargs) -> FitResults:
        """
        Perform a fit using the lmfit engine.

        :param x: points to be calculated at
        :type x: np.ndarray
        :param y: measured points
        :type y: np.ndarray
        :param weights: Weights for supplied measured points * Not really optional*
        :type weights: np.ndarray
        :param model: Optional Model which is being fitted to
        :type model: lmModel
        :param parameters: Optional parameters for the fit
        :type parameters: List[bumpsParameter]
        :param kwargs: Additional arguments for the fitting function.
        :return: Fit results
        :rtype: ModelResult
        """

        if weights is None:
            weights = np.sqrt(x)

        if model is None:
            model = self.make_model(pars=parameters)
            model = model(x, y, weights)
        self._cached_model = model
        problem = FitProblem(model)
        # Why do we do this? Because a fitting template has to have borg instantiated outside pre-runtime
        from easyCore import borg
        borg.stack.beginMacro('Fitting routine')
        model_results = bumps_fit(problem, **kwargs)
        self._set_parameter_fit_result(model_results)
        borg.stack.endMacro()
        return self._gen_fit_results(model_results)

    def convert_to_pars_obj(self, par_list: Union[list, noneType] = None) -> List[bumpsParameter]:
        """
        Create a container with the `Parameters` converted from the base object.

        :param par_list: If only a single/selection of parameter is required. Specify as a list
        :type par_list: List[str]
        :return: bumps Parameters list
        :rtype: List[bumpsParameter]
        """
        if par_list is None:
            # Assume that we have a BaseObj for which we can obtain a list
            par_list = self._object.get_parameters()
        pars_obj = ([self.__class__.convert_to_par_object(obj) for obj in par_list])
        return pars_obj

    # For some reason I have to double staticmethod :-/
    @staticmethod
    def convert_to_par_object(obj) -> bumpsParameter:
        """
        Convert an `easyCore.Objects.Base.Parameter` object to a bumps Parameter object

        :return: bumps Parameter compatible object.
        :rtype: bumpsParameter
        """
        return bumpsParameter(name=obj.name, value=obj.raw_value, bounds=[obj.min, obj.max], fixed=obj.fixed)

    def _set_parameter_fit_result(self, fit_result):
        """
        Update parameters to their final values and assign a std error to them.

        :param fit_result: Fit object which contains info on the fit
        :return: None
        :rtype: noneType
        """
        pars = self._cached_pars
        for index, name in enumerate(self._cached_model._pnames):
            item = pars[name]
            item.value = fit_result.x[index]
            item.error = fit_result.dx[index]

    def _gen_fit_results(self, fit_results, **kwargs) -> FitResults:
        """
        Convert fit results into the unified `FitResults` format

        :param fit_result: Fit object which contains info on the fit
        :return: fit results container
        :rtype: FitResults
        """

        results = FitResults()
        for name, value in kwargs.items():
            if getattr(results, name, False):
                setattr(results, name, value)
        pars = self._cached_pars
        pars_dict = {}
        for name, par in pars.items():
            pars_dict[name] = par.raw_value

        results.success = fit_results.success
        pars = self._cached_pars
        item = {}
        for index, name in enumerate(self._cached_model._pnames):
            item[name] = pars[name].raw_value
        results.p = item
        results.x = self._cached_model.x
        results.y_obs = self._cached_model.y
        results.y_calc = self.evaluate(results.x)
        results.residual = results.y_obs - results.y_calc
        results.goodness_of_fit = fit_results.fun

        results.fitting_engine = self.__class__
        results.fit_args = None

        return results
