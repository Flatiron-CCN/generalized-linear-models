import jax
import jax.numpy as jnp
import numpy as np
import pytest

import nemos as nmo


@pytest.mark.parametrize(
    "non_linearity",
    [
        jnp.exp,
        jax.nn.softplus,
        lambda x: jnp.exp(x),
        jax.nn.sigmoid,
    ],
)
@pytest.mark.parametrize(
    "output_y",
    [np.random.uniform(0, 1, size=(10,)), np.random.uniform(0, 1, size=(10, 2))],
)
def test_invert_non_linearity(non_linearity, output_y):
    inv_y = nmo.initialize_regressor.initialize_intercept_matching_mean_rate(
        inverse_link_function=non_linearity, y=output_y
    )
    assert jnp.allclose(non_linearity(inv_y), jnp.mean(output_y, axis=0), rtol=10**-5)


@pytest.mark.parametrize(
    "non_linearity, expectation",
    [
        (jnp.exp, pytest.raises(ValueError, match=".+The mean firing rate assumes")),
        (
            jax.nn.softplus,
            pytest.raises(ValueError, match=".+The mean firing rate assumes"),
        ),
        (
            lambda x: jnp.exp(x),
            pytest.raises(
                ValueError, match=".+Please, provide initial parameters instead"
            ),
        ),
        (
            jax.nn.sigmoid,
            pytest.raises(
                ValueError, match=".+Please, provide initial parameters instead"
            ),
        ),
    ],
)
def test_initialization_error(non_linearity, expectation):
    """Initialize invalid."""
    output_y = np.full((10, 2), np.nan)
    with expectation:
        nmo.initialize_regressor.initialize_intercept_matching_mean_rate(
            inverse_link_function=non_linearity, y=output_y
        )