import { createServerFn } from "@tanstack/react-start";

const UPSTREAMS = [
  (uid: string, region: string) =>
    `https://ffapii.vercel.app/get_player_personal_show?server=${region}&uid=${uid}`,
];

/** Tous les serveurs Free Fire (codes officiels + alias régionaux). */
export const SERVERS = [
  "IND", "BD", "PK", "SG", "ID", "TW", "VN", "TH",
  "ME", "MEA", "RU", "CIS", "EU", "US", "NA", "BR", "SAC",
] as const;

const REGION_MAP: Record<string, string> = {
  IND: "ind", BD: "bd", PK: "pk", SG: "sg", ID: "id", TW: "tw", VN: "vn",
  TH: "th", ME: "me", MEA: "me", RU: "ru", CIS: "cis", EU: "eu", US: "us",
  NA: "na", BR: "br", SAC: "sac",
};

export const SERVER_LABELS: Record<string, string> = {
  IND: "Inde", BD: "Bangladesh", PK: "Pakistan", SG: "Singapour",
  ID: "Indonésie", TW: "Taïwan", VN: "Vietnam", TH: "Thaïlande",
  ME: "Moyen-Orient", MEA: "Moyen-Orient & Afrique", RU: "Russie",
  CIS: "CIS", EU: "Europe", US: "États-Unis", NA: "Amérique du Nord",
  BR: "Brésil", SAC: "Amérique du Sud",
};

function normalizeKeys(value: unknown): any {
  if (Array.isArray(value)) return value.map(normalizeKeys);
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>).map(([k, v]) => [
        k.toLowerCase(),
        normalizeKeys(v),
      ]),
    );
  }
  return value;
}

export const getFFInfo = createServerFn({ method: "GET" })
  .inputValidator((data: { uid: string; server: string }) => {
    const uid = String(data?.uid ?? "").trim();
    const server = String(data?.server ?? "").trim().toUpperCase();
    if (!/^\d+$/.test(uid)) throw new Error("UID invalide : uniquement des chiffres.");
    if (!(SERVERS as readonly string[]).includes(server)) throw new Error("Serveur invalide.");
    return { uid, server };
  })
  .handler(async ({ data }) => {
    const region = REGION_MAP[data.server] ?? data.server.toLowerCase();
    const errors: string[] = [];

    for (const build of UPSTREAMS) {
      try {
        const res = await fetch(build(data.uid, region), {
          headers: {
            "User-Agent": "ChristusStore-FFInfo/2.0 (+https://christus.store)",
            Accept: "application/json",
          },
        });
        if (!res.ok) {
          errors.push(`HTTP ${res.status}`);
          continue;
        }
        const json = normalizeKeys(await res.json()) as Record<string, any>;
        if (json?.["basicinfo"]) return { uid: data.uid, server: data.server, raw: json };
        errors.push(String(json?.["message"] ?? "aucune donnée joueur"));
      } catch {
        errors.push("connexion impossible");
      }
    }

    if (errors.some((e) => e.includes("aucune donnée"))) {
      throw new Error(
        `Joueur introuvable sur le serveur ${data.server}. Vérifiez l'UID et la région.`,
      );
    }
    throw new Error(
      `Les serveurs Free Fire sont momentanément indisponibles (${errors.join(", ")}). Réessayez dans un instant.`,
    );
  });
