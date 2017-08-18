import tables as tb

input_hits_file = '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/fe_source/47x12_50000_Hits.h5'

with tb.open_file(input_hits_file, 'w') as in_file:
    data = in_file.root.Hits[:]
    print data