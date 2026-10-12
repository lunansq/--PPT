#!/usr/bin/env python3
"""Run the pinned ToolUniverse guideline implementations without a full ML install.

This emits retrieval records, never clinical recommendations or a latest-version claim.
ToolUniverse code is supplied by --tooluniverse-dir; its native source schemas are used.
"""
from pathlib import Path
import argparse,concurrent.futures,datetime,importlib,json,os,re,subprocess,sys
from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode
DEFAULT_TOOLS=('NICE_Clinical_Guidelines_Search','PubMed_Guidelines_Search','EuropePMC_Guidelines_Search')
SENSITIVE={'api_key','apikey','access_token','authorization','token','secret'}
def redact(value):
 if isinstance(value,dict):return {k:('[REDACTED]' if k.lower() in SENSITIVE else redact(v)) for k,v in value.items()}
 if isinstance(value,list):return [redact(v) for v in value]
 if isinstance(value,str):return re.sub(r'(?i)(api_key|access_token|authorization|token|secret)(=|%3D)[^&\s\"<>]+',r'\1\2[REDACTED]',value)
 return value
def normalize(result):
 if not isinstance(result,dict):return {'status':'error','data':[],'metadata':{},'error':'unexpected result type','raw':redact(result)}
 if result.get('status')!='success':return {'status':'error','data':[],'metadata':result.get('metadata',{}),'error':redact(result.get('error','provider did not report success'))}
 data=result.get('data',[]);metadata=result.get('metadata',{})
 if not isinstance(data,list) or not isinstance(metadata,dict):return {'status':'error','data':[],'metadata':{},'error':'invalid provider result contract'}
 return {'status':'success','data':redact(data),'metadata':redact(metadata),'error':None}
def build_jobs(query,names,limit):
 return [{'name':n,'arguments':{'query':query,'limit':limit,**({'search_type':'guideline'} if n=='TRIP_Database_Guidelines_Search' else {})}} for n in names]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--query',required=True);p.add_argument('--tools',nargs='+',default=list(DEFAULT_TOOLS));p.add_argument('--limit',type=int,default=10);p.add_argument('--tooluniverse-dir',type=Path);p.add_argument('--execute',action='store_true');p.add_argument('--timeout',type=float,default=15);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 if not 1<=a.limit<=200:p.error('--limit must be 1..200')
 if not 0<a.timeout<=60:p.error('--timeout must be 0..60 seconds')
 contracts=json.loads((Path(__file__).resolve().parents[1]/'docs/clinical-sources/tool_contracts.json').read_text());known={c['name']:c for c in contracts}
 if any(n not in known or n.endswith('Full_Text') for n in a.tools):p.error('use only a supported guideline search tool')
 jobs=build_jobs(a.query,a.tools,a.limit)
 if not a.execute:payload={'status':'planned_not_executed','jobs':jobs,'latest_version_confirmed':False}
 else:
  if not a.tooluniverse_dir:p.error('--execute requires --tooluniverse-dir')
  src=a.tooluniverse_dir.resolve();os.environ['TOOLUNIVERSE_LIGHT_IMPORT']='true';sys.path.insert(0,str(src/'src'))
  try:
   module=importlib.import_module('tooluniverse.unified_guideline_tools');requests=importlib.import_module('requests')
  except ImportError as e:p.error('ToolUniverse selective import failed: '+str(e))
  native=json.loads((src/'src/tooluniverse/data/unified_guideline_tools.json').read_text());native={c['name']:c for c in native}
  original=requests.sessions.Session.request
  def bounded(self,method,url,**kwargs):kwargs['timeout']=a.timeout;return original(self,method,url,**kwargs)
  requests.sessions.Session.request=bounded
  commit=subprocess.check_output(['git','-C',str(src),'rev-parse','HEAD'],text=True).strip()
  def run(job):
   try:
    c=native[job['name']];res=getattr(module,c['type'])(c).run(job['arguments']);result=normalize(res)
   except Exception as e:result=normalize({'status':'error','error':str(e)})
   return {**job,'result':result,'queried_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'upstream_commit':commit,'latest_version_confirmed':False}
  with concurrent.futures.ThreadPoolExecutor(max_workers=min(3,len(jobs))) as ex:records=list(ex.map(run,jobs))
  payload={'status':'completed_with_errors' if any(r['result']['status']=='error' for r in records) else 'retrieved_pending_original_verification','records':records,'latest_version_confirmed':False}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(redact(payload),ensure_ascii=False,indent=2));print(json.dumps({'status':payload['status'],'out':str(a.out)},ensure_ascii=False))
 if a.execute and payload['status']=='completed_with_errors':return 2
 return 0
if __name__=='__main__':raise SystemExit(main())
