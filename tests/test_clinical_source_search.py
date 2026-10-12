import importlib.util,unittest
from pathlib import Path
S=Path(__file__).parents[1]/'scripts/clinical_source_search.py';spec=importlib.util.spec_from_file_location('source_search',S);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class RetrievalIntegrity(unittest.TestCase):
 def test_connection_error_is_not_zero_hits(self):
  r=m.normalize({'status':'error','error':'403 blocked'});self.assertEqual(r['status'],'error');self.assertNotIn('total',r['metadata'])
 def test_real_empty_result_keeps_reported_zero(self):
  r=m.normalize({'status':'success','data':[],'metadata':{'total':0,'returned':0}});self.assertEqual(r['metadata']['total'],0);self.assertEqual(r['status'],'success')
 def test_truncation_is_preserved(self):
  r=m.normalize({'status':'success','data':[{'title':'one'}],'metadata':{'total':99,'returned':1,'truncated':True}});self.assertEqual(r['metadata']['total'],99);self.assertTrue(r['metadata']['truncated'])
 def test_credentials_are_redacted(self):
  r=m.redact({'api_key':'secret-value','url':'https://example.org/?api_key=private&query=eye'});self.assertNotIn('private',r['url']);self.assertEqual(r['api_key'],'[REDACTED]')
 def test_trip_uses_native_schema_spelling(self):
  self.assertEqual(m.build_jobs('eye',['TRIP_Database_Guidelines_Search'],3)[0]['arguments']['search_type'],'guideline')
if __name__=='__main__':unittest.main()
