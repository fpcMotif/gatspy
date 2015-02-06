from __future__ import division

import numpy as np
from numpy.testing import assert_allclose, assert_equal

from ..lomb_scargle_fast import (extirpolate, bitceil, trig_sum,
                                 lomb_scargle_fast)


def test_extirpolate():
    rng = np.random.RandomState(0)
    x = 100 * rng.rand(50)
    y = np.sin(x)
    f = lambda x: np.sin(x / 10)

    def check_result(N, M=5):
        y_hat = extirpolate(x, y, N, M)
        x_hat = np.arange(len(y_hat))
        assert_allclose(np.dot(f(x), y), np.dot(f(x_hat), y_hat))

    for N in [100, None]:
        yield check_result, N


def test_extirpolate_with_integers():
    rng = np.random.RandomState(0)
    x = 100 * rng.rand(50)
    x[:25] = x[:25].astype(int)
    y = np.sin(x)
    f = lambda x: np.sin(x / 10)

    def check_result(N, M=5):
        y_hat = extirpolate(x, y, N, M)
        x_hat = np.arange(len(y_hat))
        assert_allclose(np.dot(f(x), y), np.dot(f(x_hat), y_hat))

    for N in [100, None]:
        yield check_result, N


def test_bitceil():
    slow_bitceil = lambda N: int(2 ** np.ceil(np.log2(N)))

    for N in (2 ** np.arange(1, 12)):
        for offset in (-1, 0, 1):
            assert_equal(slow_bitceil(N + offset), bitceil(N + offset))


def test_trig_sum():
    rng = np.random.RandomState(0)
    t = 10 * rng.rand(50)
    h = np.sin(t)

    def check_result(f0, adjust_t, freq_factor, df=0.01):
        tfit = t - t.min() if adjust_t else t
        S1, C1 = trig_sum(tfit, h, df, N=1000, use_fft=True,
                          f0=f0, freq_factor=freq_factor, oversampling=10)
        S2, C2 = trig_sum(tfit, h, df, N=1000, use_fft=False,
                          f0=f0, freq_factor=freq_factor, oversampling=10)
        assert_allclose(S1, S2, atol=1E-2)
        assert_allclose(C1, C2, atol=1E-2)

    for f0 in [0, 1]:
        for adjust_t in [True, False]:
            for freq_factor in [1, 2]:
                yield check_result, f0, adjust_t, freq_factor


def test_lomb_scargle_fast():
    """Test lomb scargle with and without FFT"""
    rng = np.random.RandomState(0)

    t = 30 * rng.rand(100)
    y = np.sin(t)
    dy = 0.1 + 0.1 * rng.rand(len(t))
    y += dy * rng.randn(len(t))

    def check_results(subtract_mean, fit_offset):
        freq1, P1 = lomb_scargle_fast(t, y, dy,
                                      subtract_mean=subtract_mean,
                                      fit_offset=fit_offset, use_fft=True)
        freq2, P2 = lomb_scargle_fast(t, y, dy,
                                      subtract_mean=subtract_mean,
                                      fit_offset=fit_offset, use_fft=False)
        assert_allclose(freq1, freq2)
        assert_allclose(P1, P2, atol=0.005)

    for subtract_mean in [True, False]:
        for fit_offset in [True, False]:
            yield check_results, subtract_mean, fit_offset
