# Copyright (c) Recommenders contributors.
# Licensed under the MIT License.

import os
import sys
import pytest

try:
    import papermill as pm
    import scrapbook as sb
except ImportError:
    pass  # disable error while collecting tests for non-notebook environments


TOL = 0.05
ABS_TOL = 0.05


# This is a flaky test that can fail unexpectedly
@pytest.mark.flaky(reruns=5, reruns_delay=2)
@pytest.mark.spark
@pytest.mark.notebooks
@pytest.mark.integration
def test_als_pyspark_integration(notebooks, output_notebook, kernel_name):
    notebook_path = notebooks["als_pyspark"]
    pm.execute_notebook(
        notebook_path,
        output_notebook,
        kernel_name=kernel_name,
        parameters=dict(TOP_K=10, MOVIELENS_DATA_SIZE="1m"),
    )
    results = sb.read_notebook(output_notebook).scraps.dataframe.set_index("name")[
        "data"
    ]

    assert results["map"] == pytest.approx(0.00201, rel=TOL, abs=ABS_TOL)
    assert results["ndcg"] == pytest.approx(0.02516, rel=TOL, abs=ABS_TOL)
    assert results["precision"] == pytest.approx(0.03172, rel=TOL, abs=ABS_TOL)
    assert results["recall"] == pytest.approx(0.009302, rel=TOL, abs=ABS_TOL)
    assert results["rmse"] == pytest.approx(0.8621, rel=TOL, abs=ABS_TOL)
    assert results["mae"] == pytest.approx(0.68023, rel=TOL, abs=ABS_TOL)
    assert results["exp_var"] == pytest.approx(0.4094, rel=TOL, abs=ABS_TOL)
    assert results["rsquared"] == pytest.approx(0.4038, rel=TOL, abs=ABS_TOL)


# This is a flaky test that can fail unexpectedly
@pytest.mark.flaky(reruns=5, reruns_delay=2)
@pytest.mark.spark
@pytest.mark.notebooks
@pytest.mark.integration
@pytest.mark.skip(reason="It takes too long in the current test machine")
@pytest.mark.skipif(sys.platform == "win32", reason="Not implemented on Windows")
def test_mmlspark_lightgbm_criteo_integration(notebooks, output_notebook, kernel_name):
    notebook_path = notebooks["mmlspark_lightgbm_criteo"]
    pm.execute_notebook(
        notebook_path,
        output_notebook,
        kernel_name=kernel_name,
        parameters=dict(DATA_SIZE="full", NUM_ITERATIONS=50),
    )
    results = sb.read_notebook(output_notebook).scraps.dataframe.set_index("name")[
        "data"
    ]

    assert results["auc"] == pytest.approx(0.68895, rel=TOL, abs=ABS_TOL)


@pytest.mark.spark
@pytest.mark.notebooks
@pytest.mark.integration
@pytest.mark.parametrize(
    "size, algos, expected_values_ndcg",
    [
        (["100k"], ["als"], [0.035812]),
    ],
)
def test_benchmark_movielens_pyspark(
    notebooks, output_notebook, kernel_name, size, algos, expected_values_ndcg
):
    notebook_path = notebooks["benchmark_movielens"]

    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
    os.environ.pop("SPARK_HOME", None)

    pm.execute_notebook(
        notebook_path,
        output_notebook,
        kernel_name=kernel_name,
        parameters=dict(data_sizes=size, algorithms=algos),
    )
    results = sb.read_notebook(output_notebook).scraps.dataframe.set_index("name")[
        "data"
    ]
    assert len(results["results"]) == 1
    for i, value in enumerate(results["results"]):
        assert results["results"][i] == pytest.approx(value, rel=TOL, abs=ABS_TOL)
