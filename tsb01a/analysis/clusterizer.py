import numpy as np
import tables as tb

from pixel_clusterizer import clusterizer

# Initialize clusterizer object
clusterizer = clusterizer.HitClusterizer()

hit_dtype = np.dtype([('event_number', '<u8'),
                      ('frame', '<u1'),
                      ('column', '<u2'),
                      ('row', '<u2'),
                      ('charge', '<i4')])

# All cluster settings are listed here with their std. values
clusterizer.set_column_cluster_distance(2)  # cluster distance in columns
clusterizer.set_row_cluster_distance(2)  # cluster distance in rows
clusterizer.set_frame_cluster_distance(1)  # cluster distance in time frames
clusterizer.set_min_hit_charge(30)
clusterizer.set_max_hit_charge(200)  # only add hits with charge <= 29
clusterizer.ignore_same_hits(True)  # Ignore same hits in an event for clustering
clusterizer.set_hit_dtype(hit_dtype)  # Set the data type of the hits (parameter data types and names)
clusterizer.set_hit_fields({'event_number': 'event_number',
                            # Set the mapping of the hit names to the internal names (here there is no mapping done, this is the std. setting)
                            'column': 'column',
                            'row': 'row',
                            'charge': 'charge',
                            'frame': 'frame'
                            })

path = '/media/tsb01a_data/testbeam_data_apr17/100um/v_bias_40/'
input_file = path + "Hits.h5"

with tb.open_file(input_file, "r") as in_file_h5:
    hits = in_file_h5.root.Hits[:]

# Main functions
cluster_hits, clusters = clusterizer.cluster_hits(hits)  # cluster hits

with tb.open_file(path + "Hits_Cluster.h5", "w") as output_file_h5:
    cluster_hits_table = output_file_h5.create_table(output_file_h5.root, name='ClusterHits',
                                                     description=cluster_hits.dtype, title='Cluster hits table',
                                                     filters=tb.Filters(complib='blosc', complevel=5, fletcher32=False))
    # create cluster table dynamically
    cluster_table = output_file_h5.create_table(output_file_h5.root, name='Cluster', description=clusters.dtype,
                                                title='Cluster table',
                                                filters=tb.Filters(complib='blosc', complevel=5, fletcher32=False))

    cluster_hits_table.append(cluster_hits)

    cluster_table.append(clusters)

