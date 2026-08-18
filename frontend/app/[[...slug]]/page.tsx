import type { Metadata } from "next";
import { AstroTwinApp } from "@/components/AstroTwinApp";

type Params = { slug?: string[] };

export async function generateMetadata({params}:{params:Promise<Params>}):Promise<Metadata>{
  const {slug=[]}=await params;
  const isShare=slug[0]==="circle"&&slug[1]==="share"&&slug[2];
  const isResult=slug[0]==="circle"&&slug[1]==="result"&&slug[2];
  if(!isShare&&!isResult)return {};
  try{
    const base=process.env.NEXT_PUBLIC_API_URL ?? (process.env.NODE_ENV === "development" ? "http://localhost:8000" : "");
    const endpoint=isShare?`/api/compatibility/share/${slug[2]}`:`/api/compatibility/${slug[2]}`;
    const report=await fetch(`${base}${endpoint}`,{cache:"no-store"}).then(r=>r.ok?r.json():Promise.reject());
    const title=`${report.person_a_name} × ${report.person_b_name} — ${report.overall_score}% AstroCircle Match`;
    const description=`Explore this ${report.compatibility_type} reflection across communication, emotional alignment, ambition, decisions and support.`;
    return {title,description,openGraph:{title,description,images:[]},twitter:{title,description,images:[]}};
  }catch{return {title:"AstroCircle Compatibility Reflection",description:"A shareable AstroTwin compatibility reflection.",openGraph:{images:[]},twitter:{images:[]}}}
}

export default function Page(){ return <AstroTwinApp/>; }
