import numpy
import batman
import scipy
import scipy.signal
from transitleastsquares import (
    transitleastsquares,
    catalog_info,
    period_grid,
    duration_grid,
    FAP,
    cleaned_array,
    transit_mask,
    resample
)

def loadfile(filename):
    data = numpy.genfromtxt(
            filename,
            delimiter=",",
            dtype="f8, f8",
            names=["t", "y"]
        )
    return data["t"], data["y"]


if __name__ == "__main__":
    numpy.random.seed(seed=0)  # reproducibility
    print("Starting tests. This should take less than one minute...")
    
    # Resampling
    testtime = numpy.linspace(0, 1, 1000)
    testflux = numpy.linspace(0.99, 1.01, 1000)
    a, b = resample(time=testtime, flux=testflux, factor=100)
    expected_result_a = (
        0.,
        0.11111111,
        0.22222222,
        0.33333333,
        0.44444444,
        0.55555556,
        0.66666667,
        0.77777778,
        0.88888889,
        1.
        )
    numpy.testing.assert_almost_equal(a, expected_result_a)
    expected_result_b = (
        0.99,
        0.99222222,
        0.99444444,
        0.99666667,
        0.99888889,
        1.00111111,
        1.00333333,
        1.00555556,
        1.00777778,
        1.01
        )
    numpy.testing.assert_almost_equal(b, expected_result_b)
    numpy.testing.assert_equal(len(a), 10)
    numpy.testing.assert_almost_equal(min(a), 0)
    numpy.testing.assert_almost_equal(max(a), 1)
    numpy.testing.assert_almost_equal(numpy.mean(a), 0.5)
    numpy.testing.assert_equal(len(b), 10)
    numpy.testing.assert_almost_equal(min(b), 0.99)
    numpy.testing.assert_almost_equal(max(b), 1.01)
    numpy.testing.assert_almost_equal(numpy.mean(b), 1)
    print('Test passed: Resampling')

    # Clean array test
    dirty_array = numpy.ones(10, dtype=object)
    time_array = numpy.linspace(1, 10, 10)
    dy_array = numpy.ones(10, dtype=object)
    dirty_array[1] = None
    dirty_array[2] = numpy.inf
    dirty_array[3] = -numpy.inf
    dirty_array[4] = numpy.nan
    dirty_array[5] = -99

    t, y, dy = cleaned_array(time_array, dirty_array, dy_array)
    numpy.testing.assert_equal(len(t), 5)
    numpy.testing.assert_equal(numpy.sum(t), 35)

    numpy.testing.assert_equal(FAP(SDE=2), numpy.nan)
    numpy.testing.assert_equal(FAP(SDE=7), 0.009443778)
    numpy.testing.assert_equal(FAP(SDE=99), 8.0032e-05)
    print("Test passed: FAP table")

    periods = period_grid(R_star=1, M_star=1, time_span=0.1)  # R_sun  # M_sun  # days
    numpy.testing.assert_almost_equal(max(periods), 2.4999999999999987)
    numpy.testing.assert_almost_equal(min(periods), 0.6002621413799498)
    numpy.testing.assert_equal(len(periods), 268)

    periods = period_grid(R_star=1, M_star=1, time_span=20)  # R_sun  # M_sun  # days
    numpy.testing.assert_almost_equal(max(periods), 10)
    numpy.testing.assert_almost_equal(min(periods), 0.6015575922909607)
    numpy.testing.assert_equal(len(periods), 1716)

    periods = period_grid(
        R_star=5,  # R_sun
        M_star=1,  # M_sun
        time_span=20,  # days
        period_min=0,
        period_max=999,
        oversampling_factor=3,
    )
    numpy.testing.assert_almost_equal(max(periods), 10)
    numpy.testing.assert_almost_equal(min(periods), 0.6015575922909607)
    numpy.testing.assert_equal(len(periods), 1716)

    periods = period_grid(
        R_star=1,  # R_sun
        M_star=1,  # M_sun
        time_span=20,  # days
        period_min=0,
        period_max=999,
        oversampling_factor=3,
    )
    numpy.testing.assert_almost_equal(max(periods), 10)
    numpy.testing.assert_almost_equal(min(periods), 0.60155759)
    numpy.testing.assert_equal(len(periods), 1716)

    periods = period_grid(
        R_star=0.1,  # R_sun
        M_star=1,  # M_sun
        time_span=1000,  # days
        period_min=0,
        period_max=999,
        oversampling_factor=3,
    )
    numpy.testing.assert_equal(len(periods), 4308558)
    print("Test passed: period_grid")

    # Duration grid
    periods = period_grid(
        R_star=1,  # R_sun
        M_star=1,  # M_sun
        time_span=20,  # days
        period_min=0,
        period_max=999,
        oversampling_factor=3,
    )
    durations = duration_grid(periods, log_step=1.05, shortest=2)
    numpy.testing.assert_almost_equal(max(durations), 0.12)
    numpy.testing.assert_almost_equal(min(durations), 0.011618569353576557)
    numpy.testing.assert_equal(len(durations), 49)
    print("Test passed: duration_grid")

    # 266980320
    # 279741377
    # 394137592
    # 261136679

    
    (a, b), mass, mass_min, mass_max, radius, radius_min, radius_max = catalog_info(
        TIC_ID=279741377
    )
    numpy.testing.assert_equal((a, b), (0.354, 0.2321))
    numpy.testing.assert_equal(mass, 1.07496)
    numpy.testing.assert_equal(mass_min, 0.129324)
    numpy.testing.assert_equal(mass_max, 0.129324)
    numpy.testing.assert_equal(radius, 2.87762)
    numpy.testing.assert_equal(radius_min, 0.418964)
    numpy.testing.assert_equal(radius_max, 0.418964)
    print("Test passed: TESS Input Catalog (TIC) pull from Vizier using astroquery")


    (a, b), mass, mass_min, mass_max, radius, radius_min, radius_max = catalog_info(
        EPIC_ID=204341806
    )
    numpy.testing.assert_almost_equal((a, b), (1.1605, -0.1704))
    numpy.testing.assert_almost_equal(mass, numpy.nan)
    numpy.testing.assert_almost_equal(mass_min, numpy.nan)
    numpy.testing.assert_almost_equal(mass_max, numpy.nan)
    numpy.testing.assert_almost_equal(radius, numpy.nan)
    numpy.testing.assert_almost_equal(radius_min, numpy.nan)
    numpy.testing.assert_almost_equal(radius_max, numpy.nan)

    (a, b), mass, mass_min, mass_max, radius, radius_min, radius_max = catalog_info(
        EPIC_ID=204099713
    )
    numpy.testing.assert_almost_equal((a, b), (0.4804, 0.1867))
    numpy.testing.assert_almost_equal(mass, 1.046)
    numpy.testing.assert_almost_equal(mass_min, 0.898)
    numpy.testing.assert_almost_equal(mass_max, 0.642)
    numpy.testing.assert_almost_equal(radius, 1.261)
    numpy.testing.assert_almost_equal(radius_min, 1.044)
    numpy.testing.assert_almost_equal(radius_max, 0.925)
    print("Test passed: EPIC catalog pull from Vizier using astroquery")

    (a, b), mass, mass_min, mass_max, radius, radius_min, radius_max = catalog_info(
        KIC_ID=757076
    )
    numpy.testing.assert_almost_equal((a, b), (0.5819, 0.137))
    numpy.testing.assert_almost_equal(mass, 1.357)
    numpy.testing.assert_almost_equal(mass_max, 0.204)
    numpy.testing.assert_almost_equal(mass_min, 0.475)

    numpy.testing.assert_almost_equal(radius, 3.128)
    numpy.testing.assert_almost_equal(radius_max, 0.987)
    numpy.testing.assert_almost_equal(radius_min, 2.304)

    print("Test passed: KIC catalog pull from Vizier using astroquery")
        
    # Create test data
    start = 48
    days = 365.25 * 3
    samples_per_day = 12  # 48
    samples = int(days * samples_per_day)  # 48
    t = numpy.linspace(start, start + days, samples)

    # Use batman to create transits
    ma = batman.TransitParams()
    ma.t0 = (
        start + 20
    )  # time of inferior conjunction; first transit is X days after start
    ma.per = 365.25  # orbital period
    ma.rp = 6371 / 696342  # 6371 planet radius (in units of stellar radii)
    ma.a = 217  # semi-major axis (in units of stellar radii)
    ma.inc = 90  # orbital inclination (in degrees)
    ma.ecc = 0  # eccentricity
    ma.w = 90  # longitude of periastron (in degrees)
    ma.u = [0.5]  # limb darkening coefficients
    ma.limb_dark = "linear"  # limb darkening model
    m = batman.TransitModel(ma, t)  # initializes model
    original_flux = m.light_curve(ma)  # calculates light curve

    # Create noise and merge with flux
    ppm = 5
    stdev = 10 ** -6 * ppm
    noise = numpy.random.normal(0, stdev, int(samples))
    y = original_flux + noise
    y[1] = numpy.nan
    model = transitleastsquares(t, y)
    results = model.power(
        period_min=360,
        period_max=370,
        transit_depth_min=10 * 10 ** -6,
        oversampling_factor=5,
        duration_grid_step=1.02
    )
    
    numpy.testing.assert_almost_equal(results.period_uncertainty, 0.216212529678387, decimal=5)
    numpy.testing.assert_equal(results.per_transit_count[0], 7)
    numpy.testing.assert_equal(len(results.transit_times), 3)
    numpy.testing.assert_almost_equal(results.period, 365.2582192473641, decimal=5)
    numpy.testing.assert_almost_equal(
        results.transit_times[0], 68.00349264912924, decimal=5
    )
    numpy.testing.assert_almost_equal(results.depth, 0.999897160189092, decimal=5)
    numpy.testing.assert_almost_equal(results.duration, 0.5908251624976649, decimal=5)
    numpy.testing.assert_almost_equal(
        min(results.chi2red), 0.6719167401148216, decimal=5
    )
    numpy.testing.assert_almost_equal(results.SDE, 5.691301613227594, decimal=5)
    numpy.testing.assert_almost_equal(
        results.odd_even_mismatch, 0.29083256866622437, decimal=5
    )
    numpy.testing.assert_almost_equal(results.rp_rs, 0.009119851811944274, decimal=5)

    # Full light curve model
    numpy.testing.assert_almost_equal(
        max(results.model_lightcurve_time), 1143.7472155961277, decimal=5)
    numpy.testing.assert_almost_equal(
        min(results.model_lightcurve_time), 48.0059010663453, decimal=5)
    numpy.testing.assert_almost_equal(
        numpy.mean(results.model_lightcurve_time), 595.877471821318, decimal=5)
    numpy.testing.assert_almost_equal(
        numpy.sum(results.model_lightcurve_time), 39166430.34534341, decimal=5)

    numpy.testing.assert_almost_equal(
        max(results.model_lightcurve_model), 1, decimal=5)
    numpy.testing.assert_almost_equal(
        min(results.model_lightcurve_model), 0.999897160189092, decimal=5)
    numpy.testing.assert_almost_equal(
        numpy.mean(results.model_lightcurve_model), 0.9999998641488729, decimal=5)
    numpy.testing.assert_almost_equal(
        numpy.sum(results.model_lightcurve_model), 65728.99107064126, decimal=5)

    transit_times_expected = [68.003492, 433.261711, 798.519931]
    numpy.testing.assert_almost_equal(
        results.transit_times, transit_times_expected, decimal=5)
    numpy.testing.assert_almost_equal(results.duration, 0.590825, decimal=5)

    numpy.testing.assert_almost_equal(
        max(results.model_folded_phase), 1.0000380285975052, decimal=5)
    numpy.testing.assert_almost_equal(
        min(results.model_folded_phase), 3.8028597505324e-05, decimal=5)
    numpy.testing.assert_almost_equal(
        numpy.mean(results.model_folded_phase), 0.5000380285975052, decimal=5)
    numpy.testing.assert_almost_equal(
        numpy.sum(results.model_folded_phase), 6574.499999999999, decimal=5)

    numpy.testing.assert_almost_equal(
        max(results.model_folded_model), 1, decimal=5)
    numpy.testing.assert_almost_equal(
        min(results.model_folded_model), 0.999897160189092, decimal=5)
    numpy.testing.assert_almost_equal(
        numpy.mean(results.model_folded_model), 0.9999998679702978, decimal=5)
    numpy.testing.assert_almost_equal(
        numpy.sum(results.model_folded_model), 13147.998264073476, decimal=5)

    numpy.testing.assert_almost_equal(
        max(results.folded_phase), 0.9999608485845858, decimal=5)
    numpy.testing.assert_almost_equal(
        min(results.folded_phase), 1.44015016259047e-05, decimal=5)
    numpy.testing.assert_almost_equal(
        numpy.mean(results.folded_phase), 0.500000089528271, decimal=5)
    numpy.testing.assert_almost_equal(
        numpy.sum(results.folded_phase), 6574.001177117707, decimal=5)

    numpy.testing.assert_almost_equal(
        max(results.folded_y), 1.000019008301075, decimal=5)
    numpy.testing.assert_almost_equal(
        min(results.folded_y), 0.9998860842491378, decimal=5)
    numpy.testing.assert_almost_equal(
        numpy.mean(results.folded_y), 0.9999997920032417, decimal=5)
    numpy.testing.assert_almost_equal(
        numpy.sum(results.folded_y), 13147.997265, decimal=5)

    numpy.testing.assert_almost_equal(
        results.depth_mean_even, (0.999915, 6.785539e-06), decimal=5)
    numpy.testing.assert_almost_equal(
        results.depth_mean_odd, (0.999920, 1.209993e-05), decimal=5)
    numpy.testing.assert_almost_equal(
        results.depth_mean, (0.999917, 6.086923e-06), decimal=5)
    
    numpy.testing.assert_almost_equal(
        results.transit_depths, [0.99991085, 0.99992095, 0.99992007], decimal=5)
    numpy.testing.assert_almost_equal(
        results.transit_depths_uncertainties, [4.19177855e-06, 1.20999330e-05, 1.26699399e-05], decimal=5)
    numpy.testing.assert_almost_equal(
        results.odd_even_mismatch, 0.29083256866622437, decimal=5)
    numpy.testing.assert_almost_equal(
        results.per_transit_count, [7., 7., 7.], decimal=5)
    numpy.testing.assert_almost_equal(
        results.transit_count, 3, decimal=5)
    numpy.testing.assert_almost_equal(
        results.distinct_transit_count, 3, decimal=5)
    numpy.testing.assert_almost_equal(
        results.empty_transit_count, 0, decimal=5)
    numpy.testing.assert_almost_equal(
        results.snr_per_transit, [38.92162, 34.51048, 34.89514], decimal=5)
    numpy.testing.assert_almost_equal(
        results.snr, 62.542764907612785, decimal=5)
    numpy.testing.assert_almost_equal(
        results.snr_pink_per_transit, [52.24377, 46.32278, 46.8391], decimal=5)

    print("Test passed: Synthetic data")
    
    numpy.random.seed(seed=0)  # reproducibility
    print("Starting tests...")

    # Create test data
    start = 48
    days = 365.25 * 3
    samples_per_day = 12  # 48
    samples = int(days * samples_per_day)  # 48
    t = numpy.linspace(start, start + days, samples)
    print('samples', samples)

    # Use batman to create transits
    ma = batman.TransitParams()
    ma.t0 = (
        start + 20
    )  # time of inferior conjunction; first transit is X days after start
    ma.per = 365.25  # orbital period
    ma.rp = 6371 / 696342  # 6371 planet radius (in units of stellar radii)
    ma.a = 217  # semi-major axis (in units of stellar radii)
    ma.inc = 90  # orbital inclination (in degrees)
    ma.ecc = 0  # eccentricity
    ma.w = 90  # longitude of periastron (in degrees)
    ma.u = [0.5]  # limb darkening coefficients
    ma.limb_dark = "linear"  # limb darkening model
    m = batman.TransitModel(ma, t)  # initializes model
    original_flux = m.light_curve(ma)  # calculates light curve

    # Create noise and merge with flux
    ppm = 5
    stdev = 10 ** -6 * ppm
    noise = numpy.random.normal(0, stdev, int(samples))
    y = original_flux + noise

    # Inject excess noise near the end of the time series.
    # When searching without uncertainties, the SDE is 4.827
    # When searching with uncertainties, the SDE is larger, 5.254. Test passed!
    noise = numpy.random.normal(0, 10*stdev, 3149)
    y[10000:] = y[10000:] + noise

    dy = numpy.full(len(y),stdev)
    dy[10000:] = 10*stdev

    model = transitleastsquares(t, y, dy)
    results = model.power(
        period_min=360,
        period_max=370,
        oversampling_factor=3,
        duration_grid_step=1.05,
        T0_fit_margin=0.2
    )
    print('SDE', results.SDE)
    numpy.testing.assert_almost_equal(results.SDE, 5.254817340391126, decimal=5)
    print("Test passed: Synthetic data with uncertainties")


    # Testing transit shapes
    t, y = loadfile("transitleastsquares/EPIC206154641.csv")
    trend = scipy.signal.medfilt(y, 25)
    y_filt = y / trend

    # grazing
    from transitleastsquares import transitleastsquares

    model_grazing = transitleastsquares(t, y_filt)
    results_grazing = model_grazing.power(transit_template="grazing")

    numpy.testing.assert_almost_equal(
        results_grazing.duration, 0.08785037229975422, decimal=5
    )
    numpy.testing.assert_almost_equal(
        min(results_grazing.chi2red), 0.06683059525866272, decimal=5
    )
    numpy.testing.assert_almost_equal(results_grazing.SDE, 64.59390167350149, decimal=5)
    numpy.testing.assert_almost_equal(
        results_grazing.rp_rs, 0.0848188816853949, decimal=5
    )
    print("Test passed: Grazing-shaped")

    # box
    model_box = transitleastsquares(t, y_filt)
    results_box = model_box.power(transit_template="box")

    numpy.testing.assert_almost_equal(
        results_box.duration, 0.0660032849735193, decimal=5
    )
    print(min(results_box.chi2red))
    print(results_box.SDE)
    print(results_box.rp_rs)

    numpy.testing.assert_almost_equal(
        min(results_box.chi2red), 0.12358085916803863, decimal=5
    )
    numpy.testing.assert_almost_equal(results_box.SDE, 56.748626429853424, decimal=5)
    numpy.testing.assert_almost_equal(results_box.rp_rs, 0.0861904513547099, decimal=5)

    print("Test passed: Box-shaped")

    # Multi-run
    t, y = loadfile("transitleastsquares/EPIC201367065.csv")
    trend = scipy.signal.medfilt(y, 25)
    y_filt = y / trend

    model = transitleastsquares(t, y_filt)
    results = model.power()

    # Mask of the first planet
    intransit = transit_mask(t, results.period, 2 * results.duration, results.T0)
    y_second_run = y_filt[~intransit]
    t_second_run = t[~intransit]
    t_second_run, y_second_run = cleaned_array(t_second_run, y_second_run)

    # Search for second planet
    model_second_run = transitleastsquares(t_second_run, y_second_run)
    results_second_run = model_second_run.power()
    numpy.testing.assert_almost_equal(
        results_second_run.duration, 0.1478628403227008, decimal=5
    )
    numpy.testing.assert_almost_equal(
        results_second_run.SDE, 34.98291056410117, decimal=5
    )
    numpy.testing.assert_almost_equal(
        results_second_run.rp_rs, 0.025852178872027086, decimal=5
    )
    print("Test passed: Multi-planet")




    # Test for transit_depth_min=1000*10**-6, where no transit is found

    # Create test data
    start = 48
    days = 365.25 * 3
    samples_per_day = 12  # 48
    samples = int(days * samples_per_day)  # 48
    t = numpy.linspace(start, start + days, samples)

    # Use batman to create transits
    ma = batman.TransitParams()
    ma.t0 = (
        start + 20
    )  # time of inferior conjunction; first transit is X days after start
    ma.per = 365.25  # orbital period
    ma.rp = 6371 / 696342  # 6371 planet radius (in units of stellar radii)
    ma.a = 217  # semi-major axis (in units of stellar radii)
    ma.inc = 90  # orbital inclination (in degrees)
    ma.ecc = 0  # eccentricity
    ma.w = 90  # longitude of periastron (in degrees)
    ma.u = [0.5]  # limb darkening coefficients
    ma.limb_dark = "linear"  # limb darkening model
    m = batman.TransitModel(ma, t)  # initializes model
    original_flux = m.light_curve(ma)  # calculates light curve

    # Create noise and merge with flux
    ppm = 5
    stdev = 10 ** -6 * ppm
    noise = numpy.random.normal(0, stdev, int(samples))
    y = original_flux + noise
    y[1] = numpy.nan
    model = transitleastsquares(t, y)
    results = model.power(
        transit_depth_min=1000*10**-6,
        period_min=360,
        period_max=370,
        oversampling_factor=5,
        duration_grid_step=1.02,
        T0_fit_margin=0.1
    )

    numpy.testing.assert_equal(results.transit_times, [numpy.nan])
    numpy.testing.assert_equal(results.period, numpy.nan)
    numpy.testing.assert_equal(results.depth, 1)
    numpy.testing.assert_equal(results.duration, numpy.nan)
    numpy.testing.assert_equal(results.snr, numpy.nan)
    numpy.testing.assert_equal(results.snr_pink_per_transit, [numpy.nan])
    numpy.testing.assert_equal(results.odd_even_mismatch, numpy.nan)
    numpy.testing.assert_equal(results.SDE, 0)
    numpy.testing.assert_equal(results.SDE_raw, 0)
    numpy.testing.assert_almost_equal(results.chi2_min, 13148.0)
    numpy.testing.assert_almost_equal(results.chi2red_min, 1.0003043213633598)
    numpy.testing.assert_equal(len(results.periods), 278)
    numpy.testing.assert_almost_equal(max(results.periods), 369.9831654894093)
    numpy.testing.assert_almost_equal(min(results.periods), 360.0118189140635)
    numpy.testing.assert_almost_equal(max(results.power), 0)
    numpy.testing.assert_almost_equal(min(results.periods), 360.0118189140635)
    numpy.testing.assert_almost_equal(min(results.power), 0)
    numpy.testing.assert_almost_equal(max(results.chi2), 13148.0)
    numpy.testing.assert_almost_equal(max(results.chi2red), 1.0003043213633598)
    print("Test passed: transit_depth_min=1000*10**-6, where no transit is fit")

    print("All tests completed")
    
