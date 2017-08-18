''' Example how to use the clusterizer'''
import numpy as np
from builtins import str
import sys
import os.path
from matplotlib.backends.backend_pdf import PdfPages
import tables as tb

from pixel_clusterizer import clusterizer
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvas

import testbeam_analysis.tools.analysis_utils


def plot_cluster_size(input_cluster_file, dut_name=None, output_pdf_file=None, chunk_size=1000000):
    '''Plotting cluster size histogram.

    Parameters
    ----------
    input_cluster_file : string
        Filename of the input cluster file.
    dut_name : string
        Name of the DUT. If None, the filename of the input cluster file will be used.
    output_pdf_file : string
        Filename of the output PDF file. If None, the filename is derived from the input file.
    chunk_size : int
        Chunk size of the data when reading from file.
    '''
    if not dut_name:
        dut_name = os.path.split(input_cluster_file)[1]

    if not output_pdf_file:
        output_pdf_file = os.path.splitext(input_cluster_file)[0] + '_cluster_size.pdf'

    with PdfPages(output_pdf_file) as output_pdf:
        with tb.open_file(input_cluster_file, 'r') as input_file_h5:
            height = None
            n_hits = 0
            n_clusters = input_file_h5.root.Cluster.nrows
            for start_index in range(0, n_clusters, chunk_size):
                cluster_n_hits = input_file_h5.root.Cluster[start_index:start_index + chunk_size]['n_hits']
                # calculate cluster size histogram
                if height is None:
                    max_cluster_size = np.amax(cluster_n_hits)
                    height = testbeam_analysis.tools.analysis_utils.hist_1d_index(cluster_n_hits, shape=(max_cluster_size + 1,))
                elif max_cluster_size < np.amax(cluster_n_hits):
                    max_cluster_size = np.amax(cluster_n_hits)
                    height.resize(max_cluster_size + 1)
                    height += testbeam_analysis.tools.analysis_utils.hist_1d_index(cluster_n_hits, shape=(max_cluster_size + 1,))
                else:
                    height += testbeam_analysis.tools.analysis_utils.hist_1d_index(cluster_n_hits, shape=(max_cluster_size + 1,))
                n_hits += np.sum(cluster_n_hits)

        left = np.arange(max_cluster_size + 1)
        fig = Figure()
        _ = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        ax.bar(left, height, align='center')
        ax.set_title('Cluster size of %s\n(%i hits in %i clusters)' % (dut_name, n_hits, n_clusters))
        ax.set_xlabel('Cluster size')
        ax.set_ylabel('#')
        ax.grid()
        ax.set_yscale('log')
        ax.set_xlim(xmin=0.5)
        ax.set_ylim(ymin=1e-1)
        output_pdf.savefig(fig)
        ax.set_yscale('linear')
        ax.set_ylim(ymax=np.amax(height))
        ax.set_xlim(0.5, min(10, max_cluster_size) + 0.5)
        output_pdf.savefig(fig)



def pprint_array(array):  # Just to print the arrays in a nice way
    offsets = []
    for column_name in array.dtype.names:
        sys.stdout.write(column_name)
        sys.stdout.write('\t')
        offsets.append(column_name.count(''))
    for row in array:
        print('')
        for i, column in enumerate(row):
            sys.stdout.write(' ' * (offsets[i] / 2))
            sys.stdout.write(str(column))
            sys.stdout.write('\t')
    print('')


if __name__ == "__main__":
    # You can define your hit struct as you like; but it has to either contain the field names defined in pixel_clusterizer.data_struct.HitInfo or a mapping of the names have to be provided.
    # The field data types do NOT have to be the same!
    hit_dtype = np.dtype([('event_number', '<i4'),
                          ('frame', '<u1'),
                          ('column', '<u2'),
                          ('row', '<u2'),
                          ('charge', '<u4')])

    # Create some fake data
    hits = np.ones(shape=(3, ), dtype=hit_dtype)
    hits[0]['column'], hits[0]['row'], hits[0]['charge'], hits[0]['event_number'] = 17, 36, 11, 19
    hits[1]['column'], hits[1]['row'], hits[1]['charge'], hits[1]['event_number'] = 18, 36, 6, 19
    hits[2]['column'], hits[2]['row'], hits[2]['charge'], hits[2]['event_number'] = 7, 7, 1, 19
    
    
    input_hits_file = '/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/Hits_calibrated.h5'

    with tb.open_file(input_hits_file, 'r') as input_file_h5:
        hits = input_file_h5.root.Hits[:10000]

        
        # Initialize clusterizer object
        clusterizer = clusterizer.HitClusterizer()
    
        # All cluster settings are listed here with their std. values
        clusterizer.set_column_cluster_distance(2)  # cluster distance in columns
        clusterizer.set_row_cluster_distance(2)  # cluster distance in rows
        clusterizer.set_frame_cluster_distance(4)   # cluster distance in time frames
        clusterizer.set_min_hit_charge(4400)
        clusterizer.set_max_hit_charge(25000)  # only add hits with charge <= 29
        clusterizer.ignore_same_hits(True)  # Ignore same hits in an event for clustering
        clusterizer.set_hit_dtype(hit_dtype)  # Set the data type of the hits (parameter data types and names)
        clusterizer.set_hit_fields({'event_number': 'event_number',  # Set the mapping of the hit names to the internal names (here there is no mapping done, this is the std. setting)
                                    'column': 'column',
                                    'row': 'row',
                                    'charge': 'charge',
                                    'frame': 'frame'
                                    })
    
        # Main functions
        cluster_hits, clusters = clusterizer.cluster_hits(hits)  # cluster hits
    
    # Print input / output histograms
#     print('INPUT:')
#     pprint_array(hits)
    print('OUTPUT:')
    print('Hits with cluster info:')
    pprint_array(cluster_hits)
    print('Cluster info:')
    pprint_array(clusters)
    
    with tb.open_file('/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/Hits_calibrated_Cluster.h5', 'w') as output_file_h5:
        cluster_hits_table = output_file_h5.create_table(output_file_h5.root, name='ClusterHits', description=cluster_hits.dtype, title='Cluster hits table', filters=tb.Filters(complib='blosc', complevel=5, fletcher32=False))
        # create cluster table dynamically
        cluster_table = output_file_h5.create_table(output_file_h5.root, name='Cluster', description=clusters.dtype, title='Cluster table', filters=tb.Filters(complib='blosc', complevel=5, fletcher32=False))
    
        cluster_hits_table.append(cluster_hits)
            
        cluster_table.append(clusters)
        
    plot_cluster_size('/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/Hits_calibrated_Cluster.h5',
                      output_pdf_file='/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/Clusters.pdf',
                      chunk_size=10000000)
