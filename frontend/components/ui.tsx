"use client";
import { motion } from "framer-motion";
import { ReactNode } from "react";
import { Sparkles } from "lucide-react";

export function Logo(){return <a href="/" className="logo" aria-label="AstroTwin home"><span className="logoMark"><Sparkles size={18}/></span><span>AstroTwin</span></a>}
export function Card({children,className=""}:{children:ReactNode;className?:string}){return <motion.section initial={{opacity:0,y:8}} animate={{opacity:1,y:0}} className={`card ${className}`}>{children}</motion.section>}
export function Button({children,variant="primary",className="",...props}:React.ButtonHTMLAttributes<HTMLButtonElement>&{variant?:"primary"|"secondary"|"ghost"}){return <button className={`button ${variant} ${className}`} {...props}>{children}</button>}
export function PageTitle({eyebrow,title,description,action}:{eyebrow?:string;title:string;description?:string;action?:ReactNode}){return <header className="pageTitle"><div>{eyebrow&&<div className="eyebrow">{eyebrow}</div>}<h1>{title}</h1>{description&&<p>{description}</p>}</div>{action}</header>}
export function ScoreRing({value,size="large"}:{value:number;size?:"large"|"small"}){const safe=Math.max(0,Math.min(100,value));return <motion.div initial={{opacity:0,scale:.88,rotate:-8}} animate={{opacity:1,scale:1,rotate:0}} transition={{duration:.55,ease:"easeOut"}} className={`scoreRing ${size}`} style={{"--score":`${safe*3.6}deg`} as React.CSSProperties}><div><motion.strong initial={{opacity:0}} animate={{opacity:1}} transition={{delay:.25}}>{safe}</motion.strong><span>/100</span></div></motion.div>}
export function Progress({label,value}:{label:string;value:number}){const safe=Math.max(0,Math.min(100,value));return <div className="progress"><div><span>{label}</span><strong>{Math.round(value)}</strong></div><div className="track"><motion.i initial={{width:0}} animate={{width:`${safe}%`}} transition={{duration:.65,ease:"easeOut"}}/></div></div>}
export function Loading(){return <div className="state"><span className="spinner"/><h3>Aligning your experience…</h3></div>}
export function ErrorState({message,retry}:{message:string;retry?:()=>void}){return <Card className="state"><h3>We lost the signal</h3><p>{message}</p>{retry&&<Button onClick={retry}>Try again</Button>}</Card>}
export function EmptyState({title,body,action}:{title:string;body:string;action?:ReactNode}){return <Card className="state"><Sparkles/><h3>{title}</h3><p>{body}</p>{action}</Card>}
