# The `glm` Module

## Introduction



Generalized Linear Models (GLM) provide a flexible framework for modeling a variety of data types while establishing a relationship between multiple predictors and a response variable. A GLM extends the traditional linear regression by allowing for response variables that have error distribution models other than a normal distribution, such as binomial or Poisson distributions.

The `nemos.glm` module currently  offers implementations of two GLM classes:

1. **`GLM`:** A direct implementation of a feedforward GLM.
2. **`PopulationGLM`:** An implementation of a GLM for fitting a populaiton of neuron in a vectorized manner. This class inherits from `GLM` and redefines the `fit` and `_predict` to fit the model and predict the firing rate.

Our design aligns with the `scikit-learn` API, facilitating seamless integration of our GLM classes with the well-established `scikit-learn` pipeline and its cross-validation tools.

The classes provided here are modular by design offering a standard foundation for any GLM variant. 

Instantiating a specific GLM simply requires providing an observation model (Gamma, Poisson, etc.), a regularization strategies (Ridge, Lasso, etc.) and an optimization scheme during initialization. This is done using the [`nemos.observation_models.Observations`](../03-observation_models/#the-abstract-class-observations), [`nemos.regularizer.Regularizer`](../04-regularizer/#the-abstract-class-regularizer) objects as well as the compatible `jaxopt` solvers, respectively.


<figure markdown>
    <img src="../classes_nemos.png"/>
    <figcaption>Schematic of the module interactions.</figcaption>
</figure>



## The Concrete Class `GLM`

The `GLM` class provides a direct implementation of the GLM model and is designed with `scikit-learn` compatibility in mind.

### Inheritance

`GLM` inherits from [`BaseRegressor`](../02-base_class/#the-abstract-class-baseregressor). This inheritance mandates the direct implementation of methods like `predict`, `fit`, `score` `update`, and `simulate`, plus a number of validation methods.

### Attributes

- **`observation_model`**: Property that represents the GLM observation model, which is an object of the [`nemos.observation_models.Observations`](../03-observation_models/#the-abstract-class-observations) type. This model determines the log-likelihood and the emission probability mechanism for the `GLM`.
- **`coef_`**: Stores the solution for spike basis coefficients as `jax.ndarray` after the fitting process. It is initialized as `None` during class instantiation.
- **`intercept_`**: Stores the bias terms' solutions as `jax.ndarray` after the fitting process. It is initialized as `None` during class instantiation.
- **`dof_resid_`**: The degrees of freedom of the model's residual. this quantity is used to estimate the scale parameter, see below, and compute frequentist confidence intervals.
- **`scale_`**: The scale parameter of the observation distribution, which together with the rate, uniquely specifies a distribution of the exponential family. Example: a 1D Gaussian is specified by the mean which is the rate, and the standard deviation, which is the scale.
- **`solver_state_`**: Indicates the solver's state. For specific solver states, refer to the [`jaxopt` documentation](https://jaxopt.github.io/stable/index.html#).

Additionally, the `GLM` class inherits the attributes of `BaseRegressor`, see the [relative note](03-base_regressor.md) for more information.

### Public Methods

- **`predict`**: Validates input and computes the mean rates of the `GLM` by invoking the inverse-link function of the `observation_models` attribute.
- **`score`**: Validates input and assesses the Poisson GLM using either log-likelihood or pseudo-$R^2$. This method uses the `observation_models` to determine log-likelihood or pseudo-$R^2$.
- **`fit`**: Validates input and aligns the Poisson GLM with spike train data. It leverages the `observation_models` and `regularizer` to define the model's loss function and instantiate the regularizer.
- **`simulate`**: Simulates spike trains using the GLM as a feedforward network, invoking the `observation_models.sample_generator` method for emission probability.
- **`initialize_params`**: Initialize model parameters, setting to zero the coefficients, and setting the intercept by matching the firing rate.
- **`initialize_state`**: Initialize the state of the solver.
- **`update`**: Run a step of optimization and update the parameter and solver step.

### Private Methods

Here we list the private method related to the model computations:

- **`_predict`**: Forecasts rates based on current model parameters and the inverse-link function of the `observation_models`.
- **`_predict_and_compute_loss`**: Predicts the rate and calculates the mean Poisson negative log-likelihood, excluding normalization constants.

A number of `GLM` specific private methods are used for checking parameters and inputs, while the methods related for checking the solver-regularizer configurations/instantiation are inherited from `BaseRergessor`.


## The Concrete Class `PopulationGLM`

The `PopulationGLM` class is an extension of the `GLM`, designed to fit multiple neurons jointly. This involves vectorized fitting processes that efficiently handle multiple neurons simultaneously, leveraging the inherent parallelism.

### `PopulationGLM` Specific Attributes

- **`feature_mask`**: A mask that determines which features are used as predictors for each neuron. It can be a matrix of shape `(num_features, num_neurons)` or a `FeaturePytree` of binary values, where 1 indicates that a feature is used for a particular neuron and 0 indicates it is not.

### Overridden Methods

- **`fit`**: Overridden to handle fitting of the model to a neural population. This method validates input including the mask and fits the model parameters (coefficients and intercepts) to the data.
- **`_predict`**: Computes the predicted firing rates using the model parameters and the feature mask.



## Contributor Guidelines

### Implementing a `BaseRegressor` Subclasses

When crafting a functional (i.e., concrete) GLM class:

- You **must** inherit from `GLM` or one of its derivatives.
- If you inherit directly from  `BaseRegressor`, you **must** implement all the abstract methods, see the [`BaseRegressor` page](03-base_regressor.md)  for more details.
- If you inherit `GLM` or any of the other concrete classes directly, there won't be any abstract methods. 
- You **may** embed additional parameter and input checks if required by the specific GLM subclass.
- You **may** override some of the computations if needed by the model specifications.
