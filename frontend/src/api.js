import {createClient} from '@supabase/supabase-js';
const url=import.meta.env.VITE_SUPABASE_URL, key=import.meta.env.VITE_SUPABASE_ANON_KEY;
export const supabase=url&&key?createClient(url,key):null;
export const API=(import.meta.env.VITE_API_URL||'').replace(/\/$/,'');
export async function api(path,options={}) {
 const session=supabase?(await supabase.auth.getSession()).data.session:null;
 const headers={...(options.body instanceof FormData?{}:{'Content-Type':'application/json'}),...options.headers};
 if(session)headers.Authorization=`Bearer ${session.access_token}`;
 const response=await fetch(API+path,{...options,headers});
 if(!response.ok){let error;try{error=await response.json()}catch{error={detail:`Request failed (${response.status})`}};throw new Error(Array.isArray(error.detail)?error.detail.map(x=>`${x.loc.slice(1).join('.')}: ${x.msg}`).join('; '):error.detail||'Request failed')}
 if(options.blob)return response.blob();return response.json();
}
export const send=(path,data={},method='POST')=>api(path,{method,body:JSON.stringify(data)});
export async function downloadDocument(doc){const blob=await api('/api/v1/documents/'+doc.id,{blob:true});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=doc.original_name; a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
