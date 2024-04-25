from nwb2bids import base
import os

def test_reposit(nwb_testdata, tmp_path):
   nwb_testdir = os.path.dirname(nwb_testdata)
   base.reposit(nwb_testdir, tmp_path)
   # This should be done by invoking the validator once BEP032 is in the BIDS schema:
   for root, dirs, files in os.walk(tmp_path):
      if root == tmp_path:
         assert dirs == ['sub-1234']
         assert set(files) == set(['participants.json', 'participants.tsv'])
      if root == os.path.join(tmp_path, 'sub-1234'):
         assert dirs == ['ses-20240309']
         assert set(files) == set(['sessions.json', 'sessions.tsv'])
      if root == os.path.join(tmp_path, 'sub-1234', 'ses-20240309'):
         assert dirs == ['ephys']
         assert files == []
      if root == os.path.join(tmp_path, 'sub-1234', 'ses-20240309', 'ephys'):
         assert dirs == []
         assert set(files) == set([
            'sub-1234_contacts.tsv',
            'sub-1234_channels.tsv',
            'sub-1234_probes.tsv',
            'sub-1234_ses-20240309_ephys.nwb',
            ])
