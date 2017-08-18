import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


def fit_spectrum_noise(amplitudes, show_plots=False):
    
    hist, edges = np.histogram(amplitudes, bins=np.arange(-5000, 5000, 100))
    
    mids = edges


    def gauss(x, mean, sigma, amp):
        return amp * np.exp( - (x - mean)*(x - mean) / (2 * sigma * sigma))

#     print hist[np.where(hist == np.amax(hist))[0]]

    if show_plots:
        plt.bar(mids[:-1], hist, align='center', width=.5)
        plt.show()

    
    ped_index = np.where(hist == np.amax(hist))[0][0]
    ped_mean = mids[np.where(hist == np.amax(hist))[0][0]]
    peak_index = np.where(np.diff(hist) > 15)[0][-1]
    peak_mean = mids[np.where(np.diff(hist) > 15)[0][-1]]

#     print peak_mean

#     plt.bar(edges[:-1], hist, align='center', width=100, alpha=0.2, color='b')
#     plt.plot(np.arange(mids[0], mids[-1], 0.1), gauss(np.arange(mids[0], mids[-1], 0.1), ped_mean, 200, np.amax(hist)) + gauss(np.arange(mids[0], mids[-1], 0.1), peak_mean, 100, 0.027 * np.amax(hist)), "r-", linewidth=2, label='initial guess')
#     plt.xlim(-1000, None)
#     plt.show()

    try:
        ped_coeff, _ = curve_fit(gauss, mids[ped_index - 10:ped_index + 10], hist[ped_index - 10:ped_index + 10], p0=(ped_mean, 200, np.amax(hist)), sigma=100, absolute_sigma=True)
    
#         plt.plot(np.arange(mids[0], mids[-1], 0.1), gauss(np.arange(mids[0], mids[-1], 0.1), *ped_coeff) + gauss(np.arange(mids[0], mids[-1], 0.1), peak_mean, .5, 0.027 * np.amax(hist)), "m-", linewidth=2, label='between fits')

        lower_bound = np.argwhere(mids > ped_coeff[0] + 4 * ped_coeff[1])[0][0]
#         print mids[lower_bound:peak_index + 20]
        
        test = np.amax([lower_bound, peak_index -10])

#         print mids[test]
        peak_coeff, _ = curve_fit(gauss, mids[test:peak_index + 20], hist[test:peak_index + 20], p0=(peak_mean, 100, 0.027 * np.amax(hist)), sigma=10, absolute_sigma=True)
    
    # TODO: better error handling
    except RuntimeError:
        print 'Error occured'
        plt.legend(loc=0)
        plt.show()
        return {'mean': 0, 'sigma': 2, 'amp': 0}, {'mean': 0, 'sigma': 0, 'amp': 0}

#         return {'mean': ped_mean, 'sigma': 2, 'amp': 0}, {'mean': 0.027 * np.amax(hist), 'sigma': 0, 'amp': 0}
#     except ValueError:
#         print 'Error occured'
#         plt.legend(loc=0)
#         plt.show()
# 
#         return {'mean': 0, 'sigma': 2, 'amp': 0}, {'mean': 0, 'sigma': 0, 'amp': 0}

 
#         return {'mean': ped_mean, 'sigma': 2, 'amp': 0}, {'mean': 0.027 * np.amax(hist), 'sigma': 0, 'amp': 0}
    except TypeError:
        print 'Error occured'
        plt.legend(loc=0)
        plt.show()
  
        return {'mean': 0, 'sigma': 2, 'amp': 0}, {'mean': 0, 'sigma': 0, 'amp': 0}

 
#         return {'mean': ped_mean, 'sigma': 2, 'amp': 0}, {'mean': 0.027 * np.amax(hist), 'sigma': 0, 'amp': 0}


#     plt.ylim(0, 3000)
#     plt.xlabel('Electrons')
#     plt.ylabel('Counts')
#     plt.plot(np.arange(mids[0], mids[-1], 0.1), gauss(np.arange(mids[0], mids[-1], 0.1), *ped_coeff), "g-", linewidth=2, label='result')
#     plt.plot(np.arange(mids[0], mids[-1], 0.1), gauss(np.arange(mids[0], mids[-1], 0.1), *peak_coeff), "g-", linewidth=2)
#     plt.legend(loc=0)
# #  
#     plt.show()

    pedestal = {'mean': ped_coeff[0], 'sigma': np.abs(ped_coeff[1]), 'amp': ped_coeff[2]}
    peak = {'mean': peak_coeff[0], 'sigma': np.abs(peak_coeff[1]), 'amp': peak_coeff[2]}
    
    return pedestal, peak


def create_noise_map(amplitudes):
    noise_map = np.zeros((amplitudes.shape[1], amplitudes.shape[2]))

    for index, _ in np.ndenumerate(noise_map):
        pedestal, _ = fit_spectrum_noise(amplitudes[:,index[0], index[1]])
        noise_map[index[0], index[1]] = pedestal['sigma']

    return noise_map


# def create_gain_map(amplitudes):
#     gain_map = np.zeros((amplitudes.shape[1], amplitudes.shape[2]))
# 
#     for index, _ in np.ndenumerate(noise_map):
#         pedestal, peak = fit_spectrum_gain(amplitudes[:,index[0], index[1]])
#         gain_map[index[0], index[1]] = peak['mean'] / 1640
# 
#     return gain_map


if __name__ == '__main__':
    calibrated = np.load('/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/fe_source/16x12_flavor2_calibrated.npy')
    noise_map = create_noise_map(calibrated)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title('Noise / e$^-$')
    im = ax.imshow(noise_map, interpolation='none')
    fig.colorbar(im, ax=ax)
    plt.show()
    
    noise_values = noise_map.reshape(-1)
    noise_hist, edges = np.histogram(noise_values, bins=np.arange(170, 315, 5))
    plt.bar(edges[:-1], noise_hist, align='center', width=5, alpha=1)
    plt.xlabel('Noise / e$^-$')
    plt.ylabel('Counts')
    plt.show()
#     in_volt = np.load('/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/fe_source/16x12_flavor2_volt.npy')
#     gain_map = create_gain_map(in_volt * 1000000)
#     print gain_map
#     
#     fig = plt.figure()
#     ax = fig.add_subplot(111)
#     ax.set_title('Gain / V/e-')
#     im = ax.imshow(gain_map, interpolation='none')
#     fig.colorbar(im, ax=ax)
#     plt.show()