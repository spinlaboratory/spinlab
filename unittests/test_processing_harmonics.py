import unittest

import numpy as np
import spinlab as sl

from spinlab.processing.harmonics import (
    combine_harmonics,
    label_harmonics,
    reconstruct_harmonics,
    _harmonic_filter,
)


class sl_harmonics_tester(unittest.TestCase):
    def test_combine_harmonics_pairs_sequential_traces(self):
        b0 = np.linspace(0, 1, 8)
        real_parts = np.arange(1, 5) * 10.0  # 10, 20, 30, 40
        imag_parts = np.arange(1, 5) * 1.0  # 1, 2, 3, 4

        values = np.zeros((8, 8))
        for h in range(4):
            values[:, 2 * h] = real_parts[h]
            values[:, 2 * h + 1] = imag_parts[h]

        data = sl.SpinData(values, ["B0", "X"], [b0, np.arange(8)])

        out = combine_harmonics(data)

        self.assertEqual(out.dims, ["B0", "harmonic"])
        self.assertEqual(out.shape, (8, 4))
        np.testing.assert_array_equal(out.coords["harmonic"], np.arange(1, 5))
        expected = real_parts + 1j * imag_parts
        np.testing.assert_allclose(out.values, np.tile(expected, (8, 1)))
        self.assertEqual(out.proc_attrs[-1][0], "combine_harmonics")

    def test_combine_harmonics_discards_existing_imaginary_part(self):
        values = np.array([[1.0 + 5j, 2.0 + 6j]])
        data = sl.SpinData(values, ["B0", "X"], [np.array([0.0]), np.arange(2)])

        out = combine_harmonics(data)

        np.testing.assert_allclose(out.values, np.array([[1.0 + 2.0j]]))

    def test_combine_harmonics_requires_even_length_dim(self):
        values = np.ones((4, 3))
        data = sl.SpinData(values, ["B0", "X"], [np.arange(4), np.arange(3)])

        with self.assertRaises(ValueError):
            combine_harmonics(data)

    def test_combine_harmonics_requires_dim_present(self):
        values = np.ones((4, 2))
        data = sl.SpinData(values, ["B0", "X"], [np.arange(4), np.arange(2)])

        with self.assertRaises(KeyError):
            combine_harmonics(data, dim="Y")

    def test_combine_harmonics_custom_coord(self):
        values = np.ones((4, 4))
        data = sl.SpinData(values, ["B0", "X"], [np.arange(4), np.arange(4)])

        out = combine_harmonics(data, coord=np.array([1, 2]))

        np.testing.assert_array_equal(out.coords["harmonic"], np.array([1, 2]))

    def test_label_harmonics_relabels_dim_without_changing_values(self):
        b0 = np.linspace(0, 1, 8)
        values = np.arange(8 * 5).reshape(8, 5).astype(float)
        data = sl.SpinData(values, ["B0", "X"], [b0, np.arange(5)])

        out = label_harmonics(data)

        self.assertEqual(out.dims, ["B0", "harmonic"])
        self.assertEqual(out.shape, (8, 5))
        np.testing.assert_array_equal(out.coords["harmonic"], np.arange(1, 6))
        np.testing.assert_allclose(out.values, values)
        self.assertEqual(out.proc_attrs[-1][0], "label_harmonics")

    def test_label_harmonics_requires_dim_present(self):
        values = np.ones((4, 5))
        data = sl.SpinData(values, ["B0", "X"], [np.arange(4), np.arange(5)])

        with self.assertRaises(KeyError):
            label_harmonics(data, dim="Y")

    def test_label_harmonics_custom_coord(self):
        values = np.ones((4, 3))
        data = sl.SpinData(values, ["B0", "X"], [np.arange(4), np.arange(3)])

        out = label_harmonics(data, coord=np.array([1, 2, 3]))

        np.testing.assert_array_equal(out.coords["harmonic"], np.array([1, 2, 3]))

    def test_label_harmonics_coord_length_mismatch_raises(self):
        values = np.ones((4, 3))
        data = sl.SpinData(values, ["B0", "X"], [np.arange(4), np.arange(3)])

        with self.assertRaises(ValueError):
            label_harmonics(data, coord=np.array([1, 2]))


def _synthesize_harmonics(f_B, d_field, modulation_amplitude, n_harmonics):
    """Forward-model synthetic harmonics s_n(B) from a known 1st-derivative line

    Implements S_n(u) = D_n(u) * F(u) (the forward relationship underlying
    reconstruct_harmonics) so that reconstruction can be tested by round-trip.
    """
    n_field = len(f_B)
    u = 2 * np.pi * np.fft.fftfreq(n_field, d=d_field)
    F_u = np.fft.fft(f_B)

    harmonics = np.zeros((n_field, n_harmonics), dtype=complex)
    for idx, n in enumerate(range(1, n_harmonics + 1)):
        Dn = _harmonic_filter(u, n, modulation_amplitude)
        s_n = np.real(np.fft.ifft(Dn * F_u))
        harmonics[:, idx] = s_n + 0j

    return harmonics


class sl_harmonics_reconstruct_tester(unittest.TestCase):
    def test_reconstruct_harmonics_recovers_known_lineshape(self):
        B = np.linspace(-20, 20, 512)
        d_field = B[1] - B[0]
        sigma = 1.5
        f_B = -(B / sigma**2) * np.exp(-(B**2) / (2 * sigma**2))

        modulation_amplitude = 3.0
        harmonics = _synthesize_harmonics(f_B, d_field, modulation_amplitude, n_harmonics=8)

        data = sl.SpinData(
            harmonics, ["B0", "harmonic"], [B, np.arange(1, 9)]
        )

        out = reconstruct_harmonics(data, modulation_amplitude)

        self.assertEqual(out.dims, ["B0"])
        np.testing.assert_allclose(np.real(out.values), f_B, atol=1e-6)
        np.testing.assert_allclose(np.imag(out.values), 0, atol=1e-6)
        self.assertEqual(out.proc_attrs[-1][0], "reconstruct_harmonics")

    def test_reconstruct_harmonics_reconstructs_real_and_imag_channels_independently(self):
        B = np.linspace(-20, 20, 256)
        d_field = B[1] - B[0]
        sigma = 1.0
        f_real = np.exp(-(B**2) / (2 * sigma**2))
        f_imag = -(B / sigma**2) * np.exp(-(B**2) / (2 * sigma**2))

        modulation_amplitude = 2.0
        harmonics_real = _synthesize_harmonics(f_real, d_field, modulation_amplitude, 6)
        harmonics_imag = _synthesize_harmonics(f_imag, d_field, modulation_amplitude, 6)
        harmonics = np.real(harmonics_real) + 1j * np.real(harmonics_imag)

        data = sl.SpinData(harmonics, ["B0", "harmonic"], [B, np.arange(1, 7)])

        out = reconstruct_harmonics(data, modulation_amplitude)

        np.testing.assert_allclose(np.real(out.values), f_real, atol=1e-6)
        np.testing.assert_allclose(np.imag(out.values), f_imag, atol=1e-6)

    def test_reconstruct_harmonics_with_lowpass_filter_runs(self):
        B = np.linspace(-20, 20, 256)
        d_field = B[1] - B[0]
        f_B = np.exp(-(B**2) / 2)
        harmonics = _synthesize_harmonics(f_B, d_field, 2.0, 4)
        data = sl.SpinData(harmonics, ["B0", "harmonic"], [B, np.arange(1, 5)])

        out = reconstruct_harmonics(data, 2.0, cutoff=1.0, filter_width=0.2)

        self.assertEqual(out.shape, (256,))

    def test_reconstruct_harmonics_requires_dims_present(self):
        data = sl.SpinData(np.ones((4, 2)), ["B0", "harmonic"], [np.arange(4), np.arange(1, 3)])

        with self.assertRaises(KeyError):
            reconstruct_harmonics(data, 1.0, dim="Y")
        with self.assertRaises(KeyError):
            reconstruct_harmonics(data, 1.0, harmonic_dim="Y")

    def test_reconstruct_harmonics_requires_even_field_spacing(self):
        b0 = np.array([0.0, 1.0, 3.0, 4.0])
        data = sl.SpinData(
            np.ones((4, 2), dtype=complex), ["B0", "harmonic"], [b0, np.arange(1, 3)]
        )

        with self.assertRaises(ValueError):
            reconstruct_harmonics(data, 1.0)

    def test_reconstruct_harmonics_requires_positive_harmonic_orders(self):
        data = sl.SpinData(
            np.ones((4, 2), dtype=complex), ["B0", "harmonic"], [np.arange(4), np.array([0, 1])]
        )

        with self.assertRaises(ValueError):
            reconstruct_harmonics(data, 1.0)

    def test_reconstruct_harmonics_requires_filter_width_with_cutoff(self):
        data = sl.SpinData(
            np.ones((4, 2), dtype=complex), ["B0", "harmonic"], [np.arange(4), np.arange(1, 3)]
        )

        with self.assertRaises(ValueError):
            reconstruct_harmonics(data, 1.0, cutoff=1.0)


if __name__ == "__main__":
    unittest.main()
