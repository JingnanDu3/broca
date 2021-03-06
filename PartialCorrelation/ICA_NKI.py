import nibabel as nib
import numpy as np
from scipy.io import savemat
from nilearn.decomposition.canica import CanICA
from nibabel import gifti

# LEFT indices
cort = nib.freesurfer.read_label('/afs/cbs.mpg.de/software/freesurfer/5.3.0/ubuntu-precise-amd64/subjects/fsaverage5/label/lh.cortex.label')

# load data
#subs = ['A00028185'] # list of subject ids to include
subs = np.loadtxt("/scr/murg2/MachineLearning/partialcorr/NKI/subject_list_NKI.txt", dtype=str)
filenames = []
for sub in subs:
    print "SUBJECT ", sub
    try:
        data_file = gifti.giftiio.read('/scr/ilz1/nilearn_vol2surf_sink/fwhm6/%s_lh_preprocessed_fsaverage5_fwhm6.gii' % sub)
        data = np.array([data_file.darrays[i].data for i in range(len(data_file.darrays))])
        data = data.T
        data = data[cort, :]
        data = np.expand_dims(data,axis=1)    
        data = np.expand_dims(data,axis=1)
        filename = '/scr/murg2/MachineLearning/partialcorr/ICA/ICA_NKI/%s.nii.gz' % sub
        img = nib.Nifti1Image(data, np.eye(4))
        img.to_filename(filename)
        filenames.append(filename)
    except:
        print "subject " + sub + " cannot be run"
        

# create artificial mask:
mask = np.ones(len(cort))
mask = np.expand_dims(mask,axis=1)
mask = np.expand_dims(mask,axis=1)
img = nib.Nifti1Image(mask, np.eye(4))
img.to_filename('/scr/murg2/MachineLearning/partialcorr/ICA/ICA_NKI/mask.nii.gz')

# run ICA on group level:
n_components = 20
n_jobs = 20 #number of CPUs used
canica = CanICA(mask='/scr/murg2/MachineLearning/partialcorr/ICA/ICA_NKI/mask.nii.gz',
                n_components=n_components, smoothing_fwhm=0.,
                threshold=None, verbose=10, random_state=0, n_jobs=n_jobs)

canica.fit(filenames)

# Retrieve the independent components in brain space
components_img = canica.masker_.inverse_transform(canica.components_)

A = np.zeros((10242,n_components))
A[cort,:] = components_img.get_data().squeeze()
#np.save('/scr/murg2/MachineLearning/partialcorr/ICA/ICA_HCP/ica_HCP500_output_%s.npy' % str(n_components), A)
savemat('/scr/murg2/MachineLearning/partialcorr/ICA/ICA_NKI/ica_NKI_output_%s.mat' % str(n_components), {'ic':A})

## RUN ICA ON INDIVIDUAL LEVEL:
for sub in subs:
    try:
        n_components = 20
        n_jobs = 20 #number of CPUs used
        canica = CanICA(mask='/scr/murg2/MachineLearning/partialcorr/ICA/ICA_NKI/mask.nii.gz',
                        n_components=n_components, smoothing_fwhm=0.,
                        threshold=None, verbose=10, random_state=0, n_jobs=n_jobs)
        filename = '/scr/murg2/MachineLearning/partialcorr/ICA/ICA_NKI/%s.nii.gz' % sub
        canica.fit(filename)
        
        # Retrieve the independent components in brain space
        components_img = canica.masker_.inverse_transform(canica.components_)
        
        A = np.zeros((10242,n_components))
        # STILL NEED TO RESOLVE CORT INDICIES
        A[cort,:] = components_img.get_data().squeeze()
        #np.save('/scr/murg2/MachineLearning/partialcorr/ICA/ICA_NKI/ica_output_%s_%s.npy' % (sub, str(n_components)), A)
        savemat('/scr/murg2/MachineLearning/partialcorr/ICA/ICA_NKI/ica_output_%s_%s.mat' % (sub, str(n_components)), {'ic':A})
    except:
        print "subject " + sub + " cannot be run"
        
        
        
        
