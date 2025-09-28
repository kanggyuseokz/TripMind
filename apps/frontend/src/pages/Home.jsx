import { useState } from "react";
import { parseText, searchQuotes, estimateCost } from "../lib/api";

export default function Home() {
  const [text,setText]=useState("");
  const [parsed,setParsed]=useState(null);
  const [quotes,setQuotes]=useState(null);
  const [total,setTotal]=useState(null);
  const [picked,setPicked]=useState({flight:null,hotel:null});

  const onParse = async () => setParsed(await parseText(text));
  const onSearch = async () => setQuotes(await searchQuotes(parsed));
  const onPick   = (flight, hotel) => setPicked({flight, hotel});
  const onTotal  = async () => setTotal(await estimateCost(picked));

  return (
    <div style={{maxWidth:720, margin:"40px auto"}}>
      <h1>TripMind MVP</h1>
      <textarea rows={4} value={text} onChange={e=>setText(e.target.value)} placeholder="예) 서울에서 오사카 3박 2명" style={{width:"100%"}}/>
      <button onClick={onParse}>1) 파싱</button>
      {parsed && (
        <div>
          <pre>{JSON.stringify(parsed,null,2)}</pre>
          <button onClick={onSearch}>2) 견적 조회</button>
        </div>
      )}
      {quotes && (
        <div>
          <h3>항공</h3>
          {quotes.flights.map(f=>(
            <div key={f.id} onClick={()=>onPick(f,picked.hotel)} style={{cursor:"pointer"}}>
              {f.vendor} {f.route} – {f.price.toLocaleString()}원
            </div>
          ))}
          <h3>숙소</h3>
          {quotes.hotels.map(h=>(
            <div key={h.id} onClick={()=>onPick(picked.flight,h)} style={{cursor:"pointer"}}>
              {h.name} ({h.nights}박) – {h.priceTotal.toLocaleString()}원
            </div>
          ))}
          <button onClick={onTotal} disabled={!picked.flight || !picked.hotel}>3) 총액 계산</button>
        </div>
      )}
      {total && (<pre>{JSON.stringify(total,null,2)}</pre>)}
    </div>
  );
}
