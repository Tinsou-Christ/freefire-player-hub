import { createServerFn } from "@tanstack/react-start";

const UPSTREAM = "https://ffapii.vercel.app/get_player_personal_show";

export const SERVERS = [
  "SG", "BD", "RU", "ID", "TW", "US", "VN", "TH", "ME", "PK", "CIS", "BR", "IND",
] as const;

export const getFFInfo = createServerFn({ method: "GET" })
  .inputValidator((data: { uid: string; server: string }) => {
    const uid = String(data?.uid ?? "").trim();
    const server = String(data?.server ?? "").trim().toUpperCase();
    if (!/^\d+$/.test(uid)) throw new Error("UID invalide : uniquement des chiffres.");
    if (!(SERVERS as readonly string[]).includes(server)) throw new Error("Serveur invalide.");
    return { uid, server };
  })
  .handler(async ({ data }) => {
    const res = await fetch(
      `${UPSTREAM}?server=${data.server.toLowerCase()}&uid=${data.uid}`,
    );
    if (!res.ok) throw new Error("Impossible de récupérer les données Free Fire.");
    const json = (await res.json()) as Record<string, any>;
    if (!json?.basicinfo) throw new Error("Joueur introuvable.");
    return { uid: data.uid, server: data.server, raw: json };
  });
