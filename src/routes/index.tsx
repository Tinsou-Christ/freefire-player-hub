import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { useServerFn } from "@tanstack/react-start";
import { getFFInfo, SERVERS, SERVER_LABELS } from "@/lib/ffinfo.functions";
import { buildSummary, creditStatus, petName } from "@/lib/ffinfo-format";
import logo from "@/assets/christus-logo.png";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Christus Store — Free Fire Info API par UID" },
      {
        name: "description",
        content:
          "Christus Store : profil Free Fire complet (niveau, rang BR/CS, pet, clan, credit score) à partir d'un UID, sur tous les serveurs.",
      },
      { property: "og:title", content: "Christus Store — Free Fire Info API par UID" },
      {
        property: "og:description",
        content:
          "Consultez toutes les infos d'un compte Free Fire via son UID. Endpoints JSON et texte, compatibles avec la commande ffinfo.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Index,
});

type Result = { uid: string; server: string; raw: Record<string, any> };

function Stat({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-border bg-secondary/60 px-3 py-2">
      <span className="block text-[11px] uppercase tracking-wider text-muted-foreground">
        {label}
      </span>
      <b className="text-base">{value ?? "—"}</b>
    </div>
  );
}

function Index() {
  const fetchInfo = useServerFn(getFFInfo);
  const [uid, setUid] = useState("");
  const [server, setServer] = useState("IND");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<Result | null>(null);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const data = (await fetchInfo({ data: { uid: uid.trim(), server } })) as Result;
      setResult(data);
    } catch (err) {
      setResult(null);
      setError(err instanceof Error ? err.message : "Erreur inconnue");
    } finally {
      setLoading(false);
    }
  };

  const b = result?.raw["basicinfo"] ?? {};
  const pet = result?.raw["petinfo"] ?? {};
  const score = result?.raw["creditscoreinfo"]?.creditscore;

  return (
    <main className="min-h-screen bg-background px-4 py-10">
      <div className="mx-auto w-full max-w-3xl">
        <header className="mb-8 text-center">
          <img
            src={logo}
            alt="Logo Christus Store"
            width={96}
            height={96}
            className="mx-auto h-24 w-24 object-contain"
          />
          <p className="mt-2 text-xs font-bold uppercase tracking-[0.25em] text-primary">
            Christus Store
          </p>
          <h1
            className="text-4xl font-extrabold tracking-tight"
            style={{
              backgroundImage: "var(--gradient-brand)",
              WebkitBackgroundClip: "text",
              backgroundClip: "text",
              color: "transparent",
            }}
          >
            Free Fire Info API
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Profil complet d'un joueur via son UID — mêmes données que la commande{" "}
            <code className="rounded bg-secondary px-1.5 py-0.5">ffinfo</code>.
          </p>
        </header>

        <form
          onSubmit={onSubmit}
          className="flex flex-wrap gap-3 rounded-2xl border border-border bg-card p-5"
          style={{ boxShadow: "var(--shadow-glow)" }}
        >
          <input
            value={uid}
            onChange={(e) => setUid(e.target.value)}
            inputMode="numeric"
            required
            placeholder="UID du joueur (ex : 1234567890)"
            className="min-w-0 flex-1 rounded-xl border border-border bg-input px-4 py-3 text-foreground outline-none focus:border-ring"
          />
          <select
            value={server}
            onChange={(e) => setServer(e.target.value)}
            className="rounded-xl border border-border bg-input px-3 py-3 text-foreground outline-none focus:border-ring"
          >
            {SERVERS.map((s) => (
              <option key={s} value={s}>
                {s}
                {SERVER_LABELS[s] ? ` — ${SERVER_LABELS[s]}` : ""}
              </option>
            ))}
          </select>
          <button
            type="submit"
            disabled={loading}
            className="rounded-xl px-5 py-3 font-bold text-primary-foreground disabled:opacity-60"
            style={{ backgroundImage: "var(--gradient-brand)" }}
          >
            {loading ? "Recherche…" : "Rechercher"}
          </button>
        </form>

        {error && <p className="mt-4 text-sm text-destructive">{error}</p>}

        {result && (
          <>
            <section className="mt-5 rounded-2xl border border-border bg-card p-5">
              <div className="flex flex-wrap items-center gap-4">
                <img
                  src={`https://profile.thug4ff.com/api/profile?uid=${result.uid}`}
                  alt={`Photo de profil du joueur ${b.nickname ?? result.uid}`}
                  loading="lazy"
                  className="h-24 w-24 rounded-xl border border-border object-cover"
                />
                <div>
                  <div className="text-xl font-bold">{b.nickname}</div>
                  <div className="text-sm text-muted-foreground">
                    UID {result.uid} · Serveur {result.server} · Région {b.region}
                  </div>
                </div>
              </div>
              <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-4">
                <Stat label="Niveau" value={b.level} />
                <Stat label="Likes" value={b.liked} />
                <Stat label="Rang BR" value={b.rank} />
                <Stat label="Rang CS" value={b.csrank} />
                <Stat label="Pet" value={petName(pet.id)} />
                <Stat
                  label="Clan"
                  value={result.raw["clanbasicinfo"]?.clanname || "Aucun"}
                />
                <Stat label="Credit score" value={score ?? "N/A"} />
                <Stat label="Statut" value={creditStatus(score)} />
              </div>
            </section>

            <section className="mt-5 rounded-2xl border border-border bg-card p-5">
              <pre className="max-h-[520px] overflow-auto whitespace-pre-wrap break-words text-[13px] leading-relaxed text-foreground">
                {buildSummary(result.raw, result.server)}
              </pre>
            </section>
          </>
        )}

        <section className="mt-5 rounded-2xl border border-border bg-card p-5">
          <h2 className="mb-3 text-lg font-semibold">Endpoints de l'API (déploiement Render)</h2>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li>
              <code className="rounded bg-secondary px-1.5 py-0.5">
                GET /api/ffinfo?uid=UID&amp;server=IND
              </code>{" "}
              — JSON complet + résumé
            </li>
            <li>
              <code className="rounded bg-secondary px-1.5 py-0.5">
                GET /api/ffinfo/text?uid=UID&amp;server=IND
              </code>{" "}
              — texte brut format ffinfo
            </li>
            <li>
              <code className="rounded bg-secondary px-1.5 py-0.5">
                GET /api/profile-image?uid=UID
              </code>{" "}
              — image de profil
            </li>
            <li>
              <code className="rounded bg-secondary px-1.5 py-0.5">GET /api/servers</code> ·{" "}
              <code className="rounded bg-secondary px-1.5 py-0.5">GET /health</code>
            </li>
          </ul>
        </section>
      </div>
    </main>
  );
}
