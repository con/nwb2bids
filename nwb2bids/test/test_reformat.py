from nwb2bids import reformat
import os

def test_reformat_all(nwb_testdata, tmp_path):
   nwb_testdir = os.path.dirname(nwb_testdata)
   reformat.reformat_all(nwb_testdir, tmp_path)
   # This should be done by invoking the validator once BEP032 is in the BIDS schema:
   for root, dirs, files in os.walk(tmp_path):
      if root == tmp_path:
         assert dirs == ['sub-1234']
         assert files == ['participants.json', 'participants.tsv']
      if root == os.path.join(tmp_path, 'sub-1234'):
         assert dirs == ['ses-20240309']
         assert files == ['sessions.json', 'sessions.tsv']
      if root == os.path.join(tmp_path, 'sub-1234', 'ses-20240309'):
         assert dirs == ['ephys']
         assert files == []
      if root == os.path.join(tmp_path, 'sub-1234', 'ses-20240309', 'ephys'):
         assert dirs == []
         assert files == ['sub-1234contacts.tsv', 'sub-1234channels.tsv', 'sub-1234_ses-20240309_ephys.nwb', 'sub-1234probes.tsv']
