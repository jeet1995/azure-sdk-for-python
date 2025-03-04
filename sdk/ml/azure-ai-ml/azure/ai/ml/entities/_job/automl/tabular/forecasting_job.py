# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Any, Dict, List, Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import AutoMLJob as RestAutoMLJob
from azure.ai.ml._restclient.v2023_04_01_preview.models import Forecasting as RestForecasting
from azure.ai.ml._restclient.v2023_04_01_preview.models import ForecastingPrimaryMetrics, JobBase, TaskType
from azure.ai.ml._utils.utils import camel_to_snake, is_data_binding_expression
from azure.ai.ml.constants import TabularTrainingMode
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.constants._job.automl import AutoMLConstants
from azure.ai.ml.entities._credentials import _BaseJobIdentityConfiguration
from azure.ai.ml.entities._job._input_output_helpers import from_rest_data_outputs, to_rest_data_outputs
from azure.ai.ml.entities._job.automl.stack_ensemble_settings import StackEnsembleSettings
from azure.ai.ml.entities._job.automl.tabular.automl_tabular import AutoMLTabular
from azure.ai.ml.entities._job.automl.tabular.featurization_settings import TabularFeaturizationSettings
from azure.ai.ml.entities._job.automl.tabular.forecasting_settings import ForecastingSettings
from azure.ai.ml.entities._job.automl.tabular.limit_settings import TabularLimitSettings
from azure.ai.ml.entities._job.automl.training_settings import ForecastingTrainingSettings
from azure.ai.ml.entities._util import load_from_dict


class ForecastingJob(AutoMLTabular):
    """
    Configuration for AutoML Forecasting Task.

    :param primary_metric: The primary metric to use for model selection.
    :type primary_metric: Optional[str]
    :param forecasting_settings: The settings for the forecasting task.
    :type forecasting_settings:
        Optional[~azure.ai.ml.automl.ForecastingSettings]
    :param kwargs: Job-specific arguments
    :type kwargs: Dict[str, Any]
    """

    _DEFAULT_PRIMARY_METRIC = ForecastingPrimaryMetrics.NORMALIZED_ROOT_MEAN_SQUARED_ERROR

    def __init__(
        self,
        *,
        primary_metric: Optional[str] = None,
        forecasting_settings: Optional[ForecastingSettings] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a new AutoML Forecasting task."""
        # Extract any task specific settings
        featurization = kwargs.pop("featurization", None)
        limits = kwargs.pop("limits", None)
        training = kwargs.pop("training", None)

        super().__init__(
            task_type=TaskType.FORECASTING,
            featurization=featurization,
            limits=limits,
            training=training,
            **kwargs,
        )

        self.primary_metric = primary_metric or ForecastingJob._DEFAULT_PRIMARY_METRIC
        self._forecasting_settings = forecasting_settings

    @property
    def primary_metric(self) -> Optional[str]:
        """
        Return the primary metric to use for model selection.

        :return: The primary metric for model selection.
        :rtype: Optional[str]
        """
        return self._primary_metric

    @primary_metric.setter
    def primary_metric(self, value: Union[str, ForecastingPrimaryMetrics]) -> None:
        """
        Set the primary metric to use for model selection.

        :param value: The primary metric for model selection.
        :type: Union[str, ~azure.ai.ml.automl.ForecastingPrimaryMetrics]
        """
        if is_data_binding_expression(str(value), ["parent"]):
            self._primary_metric = value
            return
        self._primary_metric = (
            ForecastingJob._DEFAULT_PRIMARY_METRIC
            if value is None
            else ForecastingPrimaryMetrics[camel_to_snake(value).upper()]
        )

    @property  # type: ignore
    def training(self) -> ForecastingTrainingSettings:
        """
        Return the forecast training settings.

        :return: training settings.
        :rtype: ~azure.ai.ml.automl.ForecastingTrainingSettings
        """
        return self._training or ForecastingTrainingSettings()

    @training.setter
    def training(self, value: Union[Dict, ForecastingTrainingSettings]) -> None:  # pylint: disable=unused-argument
        ...

    @property
    def forecasting_settings(self) -> Optional[ForecastingSettings]:
        """
        Return the forecast settings.

        :return: forecast settings.
        :rtype: ~azure.ai.ml.automl.ForecastingSettings
        """
        return self._forecasting_settings

    def set_forecast_settings(
        self,
        *,
        time_column_name: Optional[str] = None,
        forecast_horizon: Optional[Union[str, int]] = None,
        time_series_id_column_names: Optional[Union[str, List[str]]] = None,
        target_lags: Optional[Union[str, int, List[int]]] = None,
        feature_lags: Optional[str] = None,
        target_rolling_window_size: Optional[Union[str, int]] = None,
        country_or_region_for_holidays: Optional[str] = None,
        use_stl: Optional[str] = None,
        seasonality: Optional[Union[str, int]] = None,
        short_series_handling_config: Optional[str] = None,
        frequency: Optional[str] = None,
        target_aggregate_function: Optional[str] = None,
        cv_step_size: Optional[int] = None,
        features_unknown_at_forecast_time: Optional[Union[str, List[str]]] = None,
    ) -> None:
        """Manage parameters used by forecasting tasks.

        :keyword time_column_name:
            The name of the time column. This parameter is required when forecasting to specify the datetime
            column in the input data used for building the time series and inferring its frequency.
        :paramtype time_column_name: Optional[str]
        :keyword forecast_horizon:
            The desired maximum forecast horizon in units of time-series frequency. The default value is 1.

            Units are based on the time interval of your training data, e.g., monthly, weekly that the forecaster
            should predict out. When task type is forecasting, this parameter is required. For more information on
            setting forecasting parameters, see `Auto-train a time-series forecast model <https://learn.microsoft.com/
            azure/machine-learning/how-to-auto-train-forecast>`_.
        :type forecast_horizon: Optional[Union[int, str]]
        :keyword time_series_id_column_names:
            The names of columns used to group a time series.
            It can be used to create multiple series. If time series id column names is not defined or
            the identifier columns specified do not identify all the series in the dataset, the time series identifiers
            will be automatically created for your data set.
        :paramtype time_series_id_column_names: Optional[Union[str, List[str]]]
        :keyword target_lags: The number of past periods to lag from the target column. By default the lags are turned
            off.

            When forecasting, this parameter represents the number of rows to lag the target values based
            on the frequency of the data. This is represented as a list or single integer. Lag should be used
            when the relationship between the independent variables and dependent variable do not match up or
            correlate by default. For example, when trying to forecast demand for a product, the demand in any
            month may depend on the price of specific commodities 3 months prior. In this example, you may want
            to lag the target (demand) negatively by 3 months so that the model is training on the correct
            relationship. For more information, see `Auto-train a time-series forecast model
            <https://learn.microsoft.com/azure/machine-learning/how-to-auto-train-forecast>`_.

            **Note on auto detection of target lags and rolling window size.
            Please see the corresponding comments in the rolling window section.**
            We use the next algorithm to detect the optimal target lag and rolling window size.

            #. Estimate the maximum lag order for the look back feature selection. In our case it is the number of
               periods till the next date frequency granularity i.e. if frequency is daily, it will be a week (7),
               if it is a week, it will be month (4). That values multiplied by two is the largest
               possible values of lags/rolling windows. In our examples, we will consider the maximum lag
               order of 14 and 8 respectively).
            #. Create a de-seasonalized series by adding trend and residual components. This will be used
               in the next step.
            #. Estimate the PACF - Partial Auto Correlation Function on the on the data from (2)
               and search for points, where the auto correlation is significant i.e. its absolute
               value is more then 1.96/square_root(maximal lag value), which correspond to significance of 95%.
            #. If all points are significant, we consider it being strong seasonality
               and do not create look back features.
            #. We scan the PACF values from the beginning and the value before the first insignificant
               auto correlation will designate the lag. If first significant element (value correlate with
               itself) is followed by insignificant, the lag will be 0 and we will not use look back features.

        :type target_lags: Optional[Union[str, int, List[int]]]
        :keyword feature_lags: Flag for generating lags for the numeric features with 'auto' or None.
        :paramtype feature_lags: Optional[str]
        :keyword target_rolling_window_size: The number of past periods used to create a rolling window average of the
            target column.

            When forecasting, this parameter represents `n` historical periods to use to generate forecasted values,
            <= training set size. If omitted, `n` is the full training set size. Specify this parameter
            when you only want to consider a certain amount of history when training the model.
            If set to 'auto', rolling window will be estimated as the last
            value where the PACF is more then the significance threshold. Please see target_lags section for details.
        :paramtype target_rolling_window_size: Optional[Union[str, int]]
        :keyword country_or_region_for_holidays: The country/region used to generate holiday features.
            These should be ISO 3166 two-letter country/region codes, for example 'US' or 'GB'.
        :paramtype country_or_region_for_holidays: Optional[str]
        :keyword use_stl: Configure STL Decomposition of the time-series target column.
            use_stl can take three values: None (default) - no stl decomposition, 'season' - only generate
            season component and season_trend - generate both season and trend components.
        :type use_stl: Optional[str]
        :keyword seasonality: Set time series seasonality as an integer multiple of the series frequency.
            If seasonality is set to 'auto', it will be inferred.
            If set to None, the time series is assumed non-seasonal which is equivalent to seasonality=1.
        :paramtype seasonality: Optional[Union[int, str]
        :keyword short_series_handling_config:
            The parameter defining how if AutoML should handle short time series.

            Possible values: 'auto' (default), 'pad', 'drop' and None.

            * **auto** short series will be padded if there are no long series,
                otherwise short series will be dropped.
            * **pad** all the short series will be padded.
            * **drop**  all the short series will be dropped".
            * **None** the short series will not be modified.

            If set to 'pad', the table will be padded with the zeroes and
            empty values for the regressors and random values for target with the mean
            equal to target value median for given time series id. If median is more or equal
            to zero, the minimal padded value will be clipped by zero:
            Input:

            +------------+---------------+----------+--------+
            | Date       | numeric_value | string   | target |
            +============+===============+==========+========+
            | 2020-01-01 | 23            | green    | 55     |
            +------------+---------------+----------+--------+

            Output assuming minimal number of values is four:

            +------------+---------------+----------+--------+
            | Date       | numeric_value | string   | target |
            +============+===============+==========+========+
            | 2019-12-29 | 0             | NA       | 55.1   |
            +------------+---------------+----------+--------+
            | 2019-12-30 | 0             | NA       | 55.6   |
            +------------+---------------+----------+--------+
            | 2019-12-31 | 0             | NA       | 54.5   |
            +------------+---------------+----------+--------+
            | 2020-01-01 | 23            | green    | 55     |
            +------------+---------------+----------+--------+

            **Note:** We have two parameters short_series_handling_configuration and
            legacy short_series_handling. When both parameters are set we are
            synchronize them as shown in the table below (short_series_handling_configuration and
            short_series_handling for brevity are marked as handling_configuration and handling
            respectively).

            +------------+--------------------------+----------------------+-----------------------------+
            | | handling | | handling               | | resulting          | | resulting                 |
            |            | | configuration          | | handling           | | handling                  |
            |            |                          |                      | | configuration             |
            +============+==========================+======================+=============================+
            | True       | auto                     | True                 | auto                        |
            +------------+--------------------------+----------------------+-----------------------------+
            | True       | pad                      | True                 | auto                        |
            +------------+--------------------------+----------------------+-----------------------------+
            | True       | drop                     | True                 | auto                        |
            +------------+--------------------------+----------------------+-----------------------------+
            | True       | None                     | False                | None                        |
            +------------+--------------------------+----------------------+-----------------------------+
            | False      | auto                     | False                | None                        |
            +------------+--------------------------+----------------------+-----------------------------+
            | False      | pad                      | False                | None                        |
            +------------+--------------------------+----------------------+-----------------------------+
            | False      | drop                     | False                | None                        |
            +------------+--------------------------+----------------------+-----------------------------+
            | False      | None                     | False                | None                        |
            +------------+--------------------------+----------------------+-----------------------------+

        :type short_series_handling_config: Optional[str]
        :keyword frequency: Forecast frequency.

            When forecasting, this parameter represents the period with which the forecast is desired,
            for example daily, weekly, yearly, etc. The forecast frequency is dataset frequency by default.
            You can optionally set it to greater (but not lesser) than dataset frequency.
            We'll aggregate the data and generate the results at forecast frequency. For example,
            for daily data, you can set the frequency to be daily, weekly or monthly, but not hourly.
            The frequency needs to be a pandas offset alias.
            Please refer to pandas documentation for more information:
            https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects
        :type frequency: Optional[str]
        :keyword target_aggregate_function: The function to be used to aggregate the time series target
            column to conform to a user specified frequency. If the target_aggregation_function is set,
            but the freq parameter is not set, the error is raised. The possible target aggregation
            functions are: "sum", "max", "min" and "mean".

                * The target column values are aggregated based on the specified operation.
                  Typically, sum is appropriate for most scenarios.
                * Numerical predictor columns in your data are aggregated by sum, mean, minimum value,
                  and maximum value. As a result, automated ML generates new columns suffixed with the
                  aggregation function name and applies the selected aggregate operation.
                * For categorical predictor columns, the data is aggregated by mode,
                  the most prominent category in the window.
                * Date predictor columns are aggregated by minimum value, maximum value and mode.

                +----------------+-------------------------------+--------------------------------------+
                |     | freq     | | target_aggregation_function | | Data regularity                    |
                |                |                               | | fixing mechanism                   |
                +================+===============================+======================================+
                | None (Default) | None (Default)                | | The aggregation                    |
                |                |                               | | is not applied.                    |
                |                |                               | | If the valid                       |
                |                |                               | | frequency can                      |
                |                |                               | | not be                             |
                |                |                               | | determined                         |
                |                |                               | | the error                          |
                |                |                               | | will be raised.                    |
                +----------------+-------------------------------+--------------------------------------+
                | Some Value     | None (Default)                | | The aggregation                    |
                |                |                               | | is not applied.                    |
                |                |                               | | If the number                      |
                |                |                               | | of data points                     |
                |                |                               | | compliant to                       |
                |                |                               | | given frequency                    |
                |                |                               | | grid is                            |
                |                |                               | | less then 90%                      |
                |                |                               | | these points                       |
                |                |                               | | will be                            |
                |                |                               | | removed,                           |
                |                |                               | | otherwise                          |
                |                |                               | | the error will                     |
                |                |                               | | be raised.                         |
                +----------------+-------------------------------+--------------------------------------+
                | None (Default) | Aggregation function          | | The error about                    |
                |                |                               | | missing                            |
                |                |                               | | frequency                          |
                |                |                               | | parameter is                       |
                |                |                               | | raised.                            |
                +----------------+-------------------------------+--------------------------------------+
                | Some Value     | Aggregation function          | | Aggregate to                       |
                |                |                               | | frequency using                    |
                |                |                               | | provided                           |
                |                |                               | | aggregation                        |
                |                |                               | | function.                          |
                +----------------+-------------------------------+--------------------------------------+

        :type target_aggregate_function: Optional[str]
        :keyword cv_step_size: Number of periods between the origin_time of one CV fold and the next fold.
            For example, if `n_step` = 3 for daily data, the origin time for each fold will be three days apart.
        :paramtype cv_step_size: Optional[int]
        :keyword features_unknown_at_forecast_time: The feature columns that are available for training but
            unknown at the time of forecast/inference. If features_unknown_at_forecast_time is set to an empty
            list, it is assumed that all the feature columns in the dataset are known at inference time. If this
            parameter is not set the support for future features is not enabled.
        :paramtype features_unknown_at_forecast_time: Optional[Union[str, List[str]]]
        """
        self._forecasting_settings = self._forecasting_settings or ForecastingSettings()

        self._forecasting_settings.country_or_region_for_holidays = (
            country_or_region_for_holidays
            if country_or_region_for_holidays is not None
            else self._forecasting_settings.country_or_region_for_holidays
        )
        self._forecasting_settings.cv_step_size = (
            cv_step_size if cv_step_size is not None else self._forecasting_settings.cv_step_size
        )
        self._forecasting_settings.forecast_horizon = (
            forecast_horizon if forecast_horizon is not None else self._forecasting_settings.forecast_horizon
        )
        self._forecasting_settings.target_lags = (
            target_lags if target_lags is not None else self._forecasting_settings.target_lags
        )
        self._forecasting_settings.target_rolling_window_size = (
            target_rolling_window_size
            if target_rolling_window_size is not None
            else self._forecasting_settings.target_rolling_window_size
        )
        self._forecasting_settings.frequency = (
            frequency if frequency is not None else self._forecasting_settings.frequency
        )
        self._forecasting_settings.feature_lags = (
            feature_lags if feature_lags is not None else self._forecasting_settings.feature_lags
        )
        self._forecasting_settings.seasonality = (
            seasonality if seasonality is not None else self._forecasting_settings.seasonality
        )
        self._forecasting_settings.use_stl = use_stl if use_stl is not None else self._forecasting_settings.use_stl
        self._forecasting_settings.short_series_handling_config = (
            short_series_handling_config
            if short_series_handling_config is not None
            else self._forecasting_settings.short_series_handling_config
        )
        self._forecasting_settings.target_aggregate_function = (
            target_aggregate_function
            if target_aggregate_function is not None
            else self._forecasting_settings.target_aggregate_function
        )
        self._forecasting_settings.time_column_name = (
            time_column_name if time_column_name is not None else self._forecasting_settings.time_column_name
        )
        self._forecasting_settings.time_series_id_column_names = (
            time_series_id_column_names
            if time_series_id_column_names is not None
            else self._forecasting_settings.time_series_id_column_names
        )
        self._forecasting_settings.features_unknown_at_forecast_time = (
            features_unknown_at_forecast_time
            if features_unknown_at_forecast_time is not None
            else self._forecasting_settings.features_unknown_at_forecast_time
        )

    # override
    def set_training(
        self,
        *,
        enable_onnx_compatible_models: Optional[bool] = None,
        enable_dnn_training: Optional[bool] = None,
        enable_model_explainability: Optional[bool] = None,
        enable_stack_ensemble: Optional[bool] = None,
        enable_vote_ensemble: Optional[bool] = None,
        stack_ensemble_settings: Optional[StackEnsembleSettings] = None,
        ensemble_model_download_timeout: Optional[int] = None,
        allowed_training_algorithms: Optional[List[str]] = None,
        blocked_training_algorithms: Optional[List[str]] = None,
        training_mode: Optional[Union[str, TabularTrainingMode]] = None,
    ) -> None:
        """
        The method to configure forecast training related settings.

        :keyword enable_onnx_compatible_models:
            Whether to enable or disable enforcing the ONNX-compatible models.
            The default is False. For more information about Open Neural Network Exchange (ONNX) and Azure Machine
            Learning, see this `article <https://learn.microsoft.com/azure/machine-learning/concept-onnx>`__.
        :type enable_onnx_compatible: Optional[bool]
        :keyword enable_dnn_training:
            Whether to include DNN based models during model selection.
            However, the default is True for DNN NLP tasks, and it's False for all other AutoML tasks.
        :paramtype enable_dnn_training: Optional[bool]
        :keyword enable_model_explainability:
            Whether to enable explaining the best AutoML model at the end of all AutoML training iterations.
            For more information, see `Interpretability: model explanations in automated machine learning
            <https://learn.microsoft.com/azure/machine-learning/how-to-machine-learning-interpretability-automl>`__.
            , defaults to None
        :type enable_model_explainability: Optional[bool]
        :keyword enable_stack_ensemble:
            Whether to enable/disable StackEnsemble iteration.
            If `enable_onnx_compatible_models` flag is being set, then StackEnsemble iteration will be disabled.
            Similarly, for Timeseries tasks, StackEnsemble iteration will be disabled by default, to avoid risks of
            overfitting due to small training set used in fitting the meta learner.
            For more information about ensembles, see `Ensemble configuration
            <https://learn.microsoft.com/azure/machine-learning/how-to-configure-auto-train#ensemble>`__
            , defaults to None
        :type enable_stack_ensemble: Optional[bool]
        :keyword enable_vote_ensemble:
            Whether to enable/disable VotingEnsemble iteration.
            For more information about ensembles, see `Ensemble configuration
            <https://learn.microsoft.com/azure/machine-learning/how-to-configure-auto-train#ensemble>`__
            , defaults to None
        :type enable_vote_ensemble: Optional[bool]
        :keyword stack_ensemble_settings:
            Settings for StackEnsemble iteration, defaults to None
        :paramtype stack_ensemble_settings: Optional[StackEnsembleSettings]
        :keyword ensemble_model_download_timeout:
            During VotingEnsemble and StackEnsemble model generation,
            multiple fitted models from the previous child runs are downloaded. Configure this parameter with a
            higher value than 300 secs, if more time is needed, defaults to None
        :paramtype ensemble_model_download_timeout: Optional[int]
        :keyword allowed_training_algorithms:
            A list of model names to search for an experiment. If not specified,
            then all models supported for the task are used minus any specified in ``blocked_training_algorithms``
            or deprecated TensorFlow models, defaults to None
        :paramtype allowed_training_algorithms: Optional[List[str]]
        :keyword blocked_training_algorithms:
            A list of algorithms to ignore for an experiment, defaults to None
        :paramtype blocked_training_algorithms: Optional[List[str]]
        :keyword training_mode:
            [Experimental] The training mode to use.
            The possible values are-

            * distributed- enables distributed training for supported algorithms.

            * non_distributed- disables distributed training.

            * auto- Currently, it is same as non_distributed. In future, this might change.

            Note: This parameter is in public preview and may change in future.
        :type training_mode: Optional[Union[~azure.ai.ml.constants.TabularTrainingMode, str]]
        """
        super().set_training(
            enable_onnx_compatible_models=enable_onnx_compatible_models,
            enable_dnn_training=enable_dnn_training,
            enable_model_explainability=enable_model_explainability,
            enable_stack_ensemble=enable_stack_ensemble,
            enable_vote_ensemble=enable_vote_ensemble,
            stack_ensemble_settings=stack_ensemble_settings,
            ensemble_model_download_timeout=ensemble_model_download_timeout,
            allowed_training_algorithms=allowed_training_algorithms,
            blocked_training_algorithms=blocked_training_algorithms,
            training_mode=training_mode,
        )

        # Disable stack ensemble by default, since it is currently not supported for forecasting tasks
        if enable_stack_ensemble is None:
            if self._training is not None:
                self._training.enable_stack_ensemble = False

    def _to_rest_object(self) -> JobBase:
        if self._forecasting_settings is not None:
            forecasting_task = RestForecasting(
                target_column_name=self.target_column_name,
                training_data=self.training_data,
                validation_data=self.validation_data,
                validation_data_size=self.validation_data_size,
                weight_column_name=self.weight_column_name,
                cv_split_column_names=self.cv_split_column_names,
                n_cross_validations=self.n_cross_validations,
                test_data=self.test_data,
                test_data_size=self.test_data_size,
                featurization_settings=self._featurization._to_rest_object() if self._featurization else None,
                limit_settings=self._limits._to_rest_object() if self._limits else None,
                training_settings=self._training._to_rest_object() if self._training else None,
                primary_metric=self.primary_metric,
                log_verbosity=self.log_verbosity,
                forecasting_settings=self._forecasting_settings._to_rest_object(),
            )
        else:
            forecasting_task = RestForecasting(
                target_column_name=self.target_column_name,
                training_data=self.training_data,
                validation_data=self.validation_data,
                validation_data_size=self.validation_data_size,
                weight_column_name=self.weight_column_name,
                cv_split_column_names=self.cv_split_column_names,
                n_cross_validations=self.n_cross_validations,
                test_data=self.test_data,
                test_data_size=self.test_data_size,
                featurization_settings=self._featurization._to_rest_object() if self._featurization else None,
                limit_settings=self._limits._to_rest_object() if self._limits else None,
                training_settings=self._training._to_rest_object() if self._training else None,
                primary_metric=self.primary_metric,
                log_verbosity=self.log_verbosity,
                forecasting_settings=None,
            )

        self._resolve_data_inputs(forecasting_task)
        self._validation_data_to_rest(forecasting_task)

        properties = RestAutoMLJob(
            display_name=self.display_name,
            description=self.description,
            experiment_name=self.experiment_name,
            tags=self.tags,
            compute_id=self.compute,
            properties=self.properties,
            environment_id=self.environment_id,
            environment_variables=self.environment_variables,
            services=self.services,
            outputs=to_rest_data_outputs(self.outputs),
            resources=self.resources,
            task_details=forecasting_task,
            identity=self.identity._to_job_rest_object() if self.identity else None,
            queue_settings=self.queue_settings,
        )

        result = JobBase(properties=properties)
        result.name = self.name
        return result

    @classmethod
    def _from_rest_object(cls, obj: JobBase) -> "ForecastingJob":
        properties: RestAutoMLJob = obj.properties
        task_details: RestForecasting = properties.task_details

        job_args_dict = {
            "id": obj.id,
            "name": obj.name,
            "description": properties.description,
            "tags": properties.tags,
            "properties": properties.properties,
            "experiment_name": properties.experiment_name,
            "services": properties.services,
            "status": properties.status,
            "creation_context": obj.system_data,
            "display_name": properties.display_name,
            "compute": properties.compute_id,
            "outputs": from_rest_data_outputs(properties.outputs),
            "resources": properties.resources,
            "identity": (
                _BaseJobIdentityConfiguration._from_rest_object(properties.identity) if properties.identity else None
            ),
            "queue_settings": properties.queue_settings,
        }

        forecasting_job = cls(
            target_column_name=task_details.target_column_name,
            training_data=task_details.training_data,
            validation_data=task_details.validation_data,
            validation_data_size=task_details.validation_data_size,
            weight_column_name=task_details.weight_column_name,
            cv_split_column_names=task_details.cv_split_column_names,
            n_cross_validations=task_details.n_cross_validations,
            test_data=task_details.test_data,
            test_data_size=task_details.test_data_size,
            featurization=(
                TabularFeaturizationSettings._from_rest_object(task_details.featurization_settings)
                if task_details.featurization_settings
                else None
            ),
            limits=(
                TabularLimitSettings._from_rest_object(task_details.limit_settings)
                if task_details.limit_settings
                else None
            ),
            training=(
                ForecastingTrainingSettings._from_rest_object(task_details.training_settings)
                if task_details.training_settings
                else None
            ),
            primary_metric=task_details.primary_metric,
            forecasting_settings=(
                ForecastingSettings._from_rest_object(task_details.forecasting_settings)
                if task_details.forecasting_settings
                else None
            ),
            log_verbosity=task_details.log_verbosity,
            **job_args_dict,
        )

        forecasting_job._restore_data_inputs()
        forecasting_job._validation_data_from_rest()

        return forecasting_job

    @classmethod
    def _load_from_dict(
        cls,
        data: Dict,
        context: Dict,
        additional_message: str,
        **kwargs: Any,
    ) -> "ForecastingJob":
        from azure.ai.ml._schema.automl.table_vertical.forecasting import AutoMLForecastingSchema
        from azure.ai.ml._schema.pipeline.automl_node import AutoMLForecastingNodeSchema

        if kwargs.pop("inside_pipeline", False):
            loaded_data = load_from_dict(AutoMLForecastingNodeSchema, data, context, additional_message, **kwargs)
        else:
            loaded_data = load_from_dict(AutoMLForecastingSchema, data, context, additional_message, **kwargs)
        job_instance = cls._create_instance_from_schema_dict(loaded_data)
        return job_instance

    @classmethod
    def _create_instance_from_schema_dict(cls, loaded_data: Dict) -> "ForecastingJob":
        loaded_data.pop(AutoMLConstants.TASK_TYPE_YAML, None)
        data_settings = {
            "training_data": loaded_data.pop("training_data"),
            "target_column_name": loaded_data.pop("target_column_name"),
            "weight_column_name": loaded_data.pop("weight_column_name", None),
            "validation_data": loaded_data.pop("validation_data", None),
            "validation_data_size": loaded_data.pop("validation_data_size", None),
            "cv_split_column_names": loaded_data.pop("cv_split_column_names", None),
            "n_cross_validations": loaded_data.pop("n_cross_validations", None),
            "test_data": loaded_data.pop("test_data", None),
            "test_data_size": loaded_data.pop("test_data_size", None),
        }
        job = ForecastingJob(**loaded_data)
        job.set_data(**data_settings)
        return job

    def _to_dict(self, inside_pipeline: bool = False) -> Dict:
        from azure.ai.ml._schema.automl.table_vertical.forecasting import AutoMLForecastingSchema
        from azure.ai.ml._schema.pipeline.automl_node import AutoMLForecastingNodeSchema

        schema_dict: dict = {}
        if inside_pipeline:
            schema_dict = AutoMLForecastingNodeSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        else:
            schema_dict = AutoMLForecastingSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return schema_dict

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ForecastingJob):
            return NotImplemented

        if not super(ForecastingJob, self).__eq__(other):
            return False

        return self.primary_metric == other.primary_metric and self._forecasting_settings == other._forecasting_settings

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
