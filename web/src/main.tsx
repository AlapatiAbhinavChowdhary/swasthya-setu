import { StrictMode, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

type Disease = { id: string; name_en: string; documents: number; last_indexed: string | null; reviewed: boolean };
type Chat = { answer: string; emergency: boolean; sources: { number: number; source: string; snippet: string }[] };

function App() {
  const [page, setPage] = useState("home");
  const [language, setLanguage] = useState("en");
  const [dark, setDark] = useState(false);
  const [diseases, setDiseases] = useState<Disease[]>([]);
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState<Chat | null>(null);
  const [loading, setLoading] = useState(false);
  useEffect(() => { fetch("/coverage").then(r => r.json()).then(data => setDiseases(data.diseases)); }, []);
  const visibleDiseases = useMemo(() => diseases, [diseases]);
  const ask = async () => {
    if (!message.trim()) return;
    setLoading(true);
    try {
      const response = await fetch("/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message, language }) });
      setChat(await response.json());
    } finally { setLoading(false); }
  };
  const speak = (text: string) => window.speechSynthesis?.speak(new SpeechSynthesisUtterance(text));
  return <div className={dark ? "app dark" : "app"}>
    <header><strong>Swasthya Setu</strong><nav>{["home", "chat", "diseases", "vaccination", "alerts", "facilities", "about"].map(item => <button key={item} onClick={() => setPage(item)}>{item[0].toUpperCase() + item.slice(1)}</button>)}</nav><select aria-label="Language" value={language} onChange={e => setLanguage(e.target.value)}><option value="en">English</option><option value="hi">हिन्दी</option></select><button onClick={() => setDark(!dark)}>{dark ? "Light" : "Dark"}</button></header>
    <main>
      {page === "home" && <section className="hero"><h1>Swasthya Setu</h1><p>Verified public-health awareness, not diagnosis or medical advice.</p><button className="primary" onClick={() => setPage("chat")}>Ask a question</button></section>}
      {page === "chat" && <section><h1>Chat</h1><textarea aria-label="Health question" value={message} onChange={e => setMessage(e.target.value)} placeholder="Ask a health-awareness question" /><button className="primary" onClick={ask} disabled={loading}>{loading ? "Checking..." : "Send"}</button><button onClick={() => speak(chat?.answer ?? "")}>Read aloud</button>{chat && <article className={chat.emergency ? "emergency" : ""}><p>{chat.answer}</p><h2>Sources</h2>{chat.sources.map(source => <p key={source.number}><b>[{source.number}]</b> {source.source} — {source.snippet}</p>)}</article>}</section>}
      {page === "diseases" && <section><h1>Diseases</h1><div className="grid">{visibleDiseases.map(d => <button className="card" key={d.id} onClick={() => setPage(`disease:${d.id}`)}><h2>{d.name_en}</h2><p>{d.documents ? `${d.documents} verified document(s)` : "Coming soon: no verified sources indexed yet"}</p>{!d.reviewed && <small>Pending expert review</small>}</button>)}</div></section>}
      {page.startsWith("disease:") && <section><h1>{visibleDiseases.find(d => d.id === page.slice(8))?.name_en}</h1><p>Coverage is generated from indexed official sources.</p></section>}
      {page === "vaccination" && <section><h1>Vaccination</h1><p>Verified schedules only. Pending expert review.</p></section>}
      {page === "alerts" && <section><h1>Alerts <span className="badge">DEMO</span></h1><p>Live outbreak data is not connected.</p></section>}
      {page === "facilities" && <section><h1>Facilities</h1><p>Facility data is not connected. Call 108 in an emergency.</p></section>}
      {page === "about" && <section><h1>About and coverage</h1><table><thead><tr><th>Disease</th><th>Documents</th><th>Last indexed</th></tr></thead><tbody>{visibleDiseases.map(d => <tr key={d.id}><td>{d.name_en}</td><td>{d.documents}</td><td>{d.last_indexed ?? "—"}</td></tr>)}</tbody></table></section>}
    </main><footer>Not for diagnosis, prescriptions, or doses. Pending expert review.</footer>
  </div>;
}
createRoot(document.getElementById("root")!).render(<StrictMode><App /></StrictMode>);
