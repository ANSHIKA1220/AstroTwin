const configuredApiUrl = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "");

// Production requests stay on the Vercel origin and are reverse-proxied to
// Render by next.config.ts. This makes the signed session cookie first-party;
// direct vercel.app -> onrender.com requests can be rejected by browsers that
// block third-party cookies.
export const API_URL = process.env.NODE_ENV === "development"
  ? configuredApiUrl ?? "http://localhost:8000"
  : "";

function errorMessage(detail: unknown, fallback: string): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map(item => typeof item?.msg === "string" ? item.msg : "Invalid input").join(" · ");
  return fallback;
}

export async function api<T>(path:string, options:RequestInit={}):Promise<T>{
  let response: Response;
  try { response = await fetch(`${API_URL}${path}`, { ...options, credentials:"include", headers:{"Content-Type":"application/json",...(options.headers||{})}, cache:"no-store" }); }
  catch { throw new Error("AstroTwin could not reach its service. Please try again in a moment."); }
  if(!response.ok) {
    const payload = await response.json().catch(()=>({detail:null}));
    throw new Error(errorMessage(payload.detail, `Request failed (${response.status})`));
  }
  return response.json();
}
export const post = <T>(path:string, body:unknown) => api<T>(path,{method:"POST",body:JSON.stringify(body)});
export const put = <T>(path:string, body:unknown) => api<T>(path,{method:"PUT",body:JSON.stringify(body)});
export const del = <T>(path:string) => api<T>(path,{method:"DELETE"});
